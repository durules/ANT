from django.db import models
from django.urls import reverse
from mnf.material.materialModels import MnfMaterial


class MnfShiftResult(models.Model):
    """
    Результат смены.
    Описывает количество произведенных товаров и затраченные материалы.
    Для списания ТМЦ со склада формирует расходную накладную.
    """

    STATE_REGISTERING = "100"
    STATE_DONE = "300"

    s_state_choices = ((STATE_REGISTERING, "Оформляется"), (STATE_DONE, "Выполнен"))

    d_create_date = models.DateTimeField("Дата содания", db_index=True)
    d_reg_date = models.DateTimeField("Дата проведения", null=True)
    s_state = models.CharField("Состояние", max_length=3, choices=s_state_choices, null=False)
    # Ссылка на сформированную накладную
    id_act = models.ForeignKey('stocks.StkAct', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Накладная")

    class Meta:
        verbose_name = "Отчет о выполненной работе"
        verbose_name_plural = "Отчеты о выполненной работе"

    def __str__(self):
        return "Отчет о выполненной работе от " + self.d_create_date.strftime('%d.%m.%Y %H:%M')

    def get_absolute_url(self):
        return reverse('mnf_shift_result-detail', args=[str(self.id)])


class MnfShiftResultItems(models.Model):
    """
    Произведенные объекты.
    Перечень объектов, произведенных за смену.
    """
    id_shift_result = models.ForeignKey('MnfShiftResult', on_delete=models.CASCADE, null=False, verbose_name="Отчет о выполненной работе")
    id_item = models.ForeignKey('MnfItem', on_delete=models.PROTECT, null=False, verbose_name="Объект производства")
    n_qty = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Произведенный объект"
        verbose_name_plural = "Произведенные объекты"
        unique_together = [['id_shift_result', 'id_item']]


class MnfShiftResultMaterials(models.Model):
    """
    Дополнительные материалы.
    Здесь указываются дополнительно потраченные материалы, без учета материалов на объекты.
    Например брак.
    """
    id_shift_result = models.ForeignKey('MnfShiftResult', on_delete=models.CASCADE, null=False, verbose_name="Отчет о выполненной работе")
    id_material = models.ForeignKey('MnfMaterial', on_delete=models.PROTECT, null=True, verbose_name="Материал")
    n_qty = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Дополнительный материал"
        verbose_name_plural = "Дополнительные материалы"
        unique_together = [['id_shift_result', 'id_material']]