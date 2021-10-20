from django.db import models
from django.utils import timezone


class IntgCircuit(models.Model):
    """
    Контур интеграци.
    """

    TYPE_EBAY = "Ebay"
    TYPE_Wix = "Wix"

    s_type_choices = [(TYPE_EBAY, "Ebay"), (TYPE_Wix, "Wix")]

    s_caption = models.CharField("Наименование", null=False, max_length=256)
    id_trade_system = models.ForeignKey('trd.TrdTradeSystem', on_delete=models.PROTECT, verbose_name = "Торговая система")
    s_type = models.CharField("Тип интеграции", choices=s_type_choices, null=False, max_length=256)
    s_config = models.TextField("Конфигурация")

    class Meta:
        verbose_name = "Контур интеграции"
        verbose_name_plural = "Контуры интеграции"

    def __str__(self):
        return self.s_caption


class IntgCircuitRunTimeData(models.Model):
    """
    Данные интеграции.
    Свзяь с контуром 1 к 1
    """

    id_circuit = models.ForeignKey('intg.IntgCircuit', on_delete=models.CASCADE, verbose_name = "Контур")
    s_json_data = models.TextField("Json-данные")

    class Meta:
        verbose_name = "Данные интеграции"
        verbose_name_plural = "Данные интеграции"

    @staticmethod
    def get_by_circuit(circuit):
        """Получение записи по контуру"""
        return IntgCircuitRunTimeData.objects.filter(id_circuit=circuit).first()

    @staticmethod
    def register_by_circuit(circuit):
        """Регистрация записи по контуру.
        Если запись не найдена, то она создается"""
        obj = IntgCircuitRunTimeData.get_by_circuit(circuit)
        if not obj:
            obj = IntgCircuitRunTimeData()
            obj.id_circuit = circuit
            obj.save()
        return obj
