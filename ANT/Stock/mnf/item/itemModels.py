from django.db import models
from django.urls import reverse

from mnf.material.materialModels import MnfMaterial


class MnfItem(models.Model):
    """
    Объект производства.
    Описывает структуру производимого товара, его состав.
    """
    sCaption = models.CharField("Наименование", max_length=200)

    class Meta:
        ordering = ["sCaption"]
        verbose_name = "Объект производства"
        verbose_name_plural = "Объекты производства"

    def __str__(self):
        return self.sCaption

    def get_absolute_url(self):
        return reverse('MnfItem-detail', args=[str(self.id)])


class MnfItemDet(models.Model):
    """
    Состав объекта производства.
    """
    id_item = models.ForeignKey('MnfItem', on_delete=models.CASCADE, null=False, verbose_name="Объект производства")
    id_material = models.ForeignKey('MnfMaterial', on_delete=models.PROTECT, null=True, verbose_name="Материал")
    n_qty = models.PositiveIntegerField(verbose_name="Количество", blank=True, null=False)

    class Meta:
        verbose_name = "Состав объекта производства"
        verbose_name_plural = "Составы объекта производства"
        unique_together= [['id_item', 'id_material']]

    def __str__(self):
        if not self.id_material:
            return str(self.id)
        else:
            return self.id_material.s_caption

    def get_absolute_url(self):
        return reverse('MnfItemDet-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.n_qty is None:
            self.n_qty = 1

        super(MnfItemDet, self).save(*args, **kwargs)