from django.db import models
from django.utils import timezone


class GoodMapping(models.Model):
    """
    Меппинг товаров.
    """
    id_circuit = models.ForeignKey('intg.IntgCircuit', on_delete=models.PROTECT, verbose_name = "Контур")
    s_external_id = models.CharField("Идентификатор во внешней системе", null=False, max_length=256)

    class Meta:
        verbose_name = "Сопоставление товаров"
        verbose_name_plural = "Сопоставления товаров"



class GoodMappingDet(models.Model):
    """Детализация меппинга товаров"""

    # Меппинг
    id_good_mapping = models.ForeignKey('intg.GoodMapping', on_delete=models.CASCADE, null=False, verbose_name="Меппинг товара")
    # ТМЦ
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=False, verbose_name="Тмц")
    # Количество
    n_qty = models.BigIntegerField("Количество")

    class Meta:
        verbose_name = "Позиция меппинга товаров"
        verbose_name_plural = "Позиции меппинга товаров"


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


