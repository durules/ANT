from django.db import models


class GoodMapping(models.Model):
    @staticmethod
    def good_mapping_key():
        return "goods"

    @staticmethod
    def option_mapping_key():
        return "options"


    """
    Меппинг товаров.
    """
    id_circuit = models.ForeignKey('IntgCircuit', on_delete=models.PROTECT, verbose_name = "Контур")
    s_external_id = models.CharField("Идентификатор во внешней системе", null=False, max_length=256)

    class Meta:
        verbose_name = "Сопоставление товаров"
        verbose_name_plural = "Сопоставления товаров"

    @staticmethod
    def get_by_circuit(circuit):
        """Получение меппинга по контуру.
        Возвращает словарь
          ИД внешней системы: {
            goods: [(ТМЦ, Количетство)],
            options: {
              ИД внешней системы опции:  [(ТМЦ, Количетство)]
            }
          }
        """
        mapping_goods_dict = {}
        for goodMapping in GoodMapping.objects.filter(id_circuit=circuit):
            mapping_goods_dict[goodMapping.s_external_id] = {}

            # основное сопоставление
            mapping_key = GoodMapping.good_mapping_key()
            mapping_goods_dict[goodMapping.s_external_id][mapping_key] = []
            for goodMappingDet in GoodMappingDet.objects.filter(id_good_mapping=goodMapping):
                mapping_goods_dict[goodMapping.s_external_id][mapping_key].append((goodMappingDet.id_good, goodMappingDet.n_qty))

            # Опции
            mapping_key = GoodMapping.option_mapping_key()
            mapping_goods_dict[goodMapping.s_external_id][mapping_key] = {}
            for goodMappingOption in GoodMappingOption.objects.filter(id_good_mapping=goodMapping):
                mapping_goods_dict[goodMapping.s_external_id][mapping_key][goodMappingOption.s_external_id] = []

                for goodMappingOptionDet in GoodMappingOptionDet.objects.filter(id_good_mapping_option=goodMappingOption):
                    mapping_goods_dict[goodMapping.s_external_id][mapping_key][goodMappingOption.s_external_id].append(
                        (goodMappingOptionDet.id_good, goodMappingOptionDet.n_qty)
                    )

        return mapping_goods_dict


class GoodMappingDet(models.Model):
    """Детализация меппинга товаров"""

    # Меппинг
    id_good_mapping = models.ForeignKey('intg.GoodMapping', on_delete=models.CASCADE, null=False, verbose_name="Меппинг товара")
    # ТМЦ
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=False, verbose_name="Тмц")
    # Количество
    n_qty = models.BigIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция меппинга товаров"
        verbose_name_plural = "Позиции меппинга товаров"


class GoodMappingOption(models.Model):
    """Опции меппинга товаров"""

    # Меппинг
    id_good_mapping = models.ForeignKey('intg.GoodMapping', on_delete=models.CASCADE, null=False, verbose_name="Меппинг товара")
    # ТМЦ
    s_external_id = models.CharField("Идентификатор во внешней системе", null=False, max_length=256)

    class Meta:
        verbose_name = "Опция сопоставления товаров"
        verbose_name_plural = "Опции сопоставления товаров"


class GoodMappingOptionDet(models.Model):
    """Детализация опций"""

    # Меппинг
    id_good_mapping_option = models.ForeignKey('intg.GoodMappingOption', on_delete=models.CASCADE, null=False, verbose_name="Опция сопоставления товара")
    # ТМЦ
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=False, verbose_name="Тмц")
    # Количество
    n_qty = models.BigIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция опции сопоставления товаров"
        verbose_name_plural = "Позиции опции сопоставления товаров"


class DeliverySystemMapping(models.Model):
    """
    Меппинг службы доставки.
    """
    id_circuit = models.ForeignKey('intg.IntgCircuit', on_delete=models.PROTECT, verbose_name = "Контур")
    s_external_id = models.CharField("Идентификатор во внешней системе", null=False, max_length=256)
    id_delivery_service = models.ForeignKey('trd.TrdDeliveryService', on_delete=models.PROTECT, null=True, blank=True,
                                            verbose_name="Служба доставки")

    class Meta:
        verbose_name = "Сопоставление службы доставки"
        verbose_name_plural = "Сопоставления службы доставки"

    @staticmethod
    def get_by_circuit(circuit):
        """Получение меппинга по контуру.
        Возвращает словарь ИД внешней системы: служба доставки"""
        mapping_dict = {}
        for mapping in DeliverySystemMapping.objects.filter(id_circuit=circuit):
            mapping_dict[mapping.s_external_id] = mapping.id_delivery_service

        return mapping_dict


