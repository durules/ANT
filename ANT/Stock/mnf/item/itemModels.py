from django.db import models
from django.urls import reverse

from goods.models import GdsGood


class MnfItem(models.Model):
    """
    Объект производства.
    Описывает структуру производимого товара, его состав.
    """
    sCaption = models.CharField("Наименование", max_length=200)

    """
    Тмц, в который синхронизирован объект производства.
    Если пользователь при создании объекта не укажет ТМЦ, то будет создан новый.
    """
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Тмц")

    class Meta:
        ordering = ["sCaption"]
        verbose_name = "Объект производства"
        verbose_name_plural = "Объекты производства"

    def __str__(self):
        return self.sCaption

    def get_absolute_url(self):
        return reverse('MnfItem-detail', args=[str(self.id)])

    def __sync_with_good(self):
        """синхронизация с ТМЦ"""
        if self.id_good_id is None:
            self.id_good = GdsGood()

        gds = self.id_good
        gds.sCaption = self.sCaption
        gds.save()
        # чтобы обновилось поле в таблице
        self.id_good = gds

    def save(self, *args, **kwargs):
        self.__sync_with_good()
        super(MnfItem, self).save(*args, **kwargs)


class MnfItemDet(models.Model):
    """
    Состав объекта производства.
    """
    id_item = models.ForeignKey('MnfItem', on_delete=models.CASCADE, null=False, verbose_name="Объект производства")
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=True, verbose_name="Тмц")
    n_qty = models.PositiveIntegerField(verbose_name="Количество", blank=True, null=False)

    class Meta:
        verbose_name = "Состав объекта производства"
        verbose_name_plural = "Составы объекта производства"
        unique_together= [['id_item', 'id_good']]

    def __str__(self):
        if not self.id_good:
            return str(self.id)
        else:
            return self.id_good.sCaption

    def get_absolute_url(self):
        return reverse('MnfItemDet-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.n_qty is None:
            self.n_qty = 1

        super(MnfItemDet, self).save(*args, **kwargs)