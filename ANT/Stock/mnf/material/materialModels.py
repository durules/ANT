from django.db import models
from django.urls import reverse

from goods.models import GdsGood


class MnfMaterial(models.Model):
    """
    Материал производства.
    Описывает доступные материалы, используемые в производстве объектов (MnfItem).

    При сохранении синхронизируется с товарами (GdsGood)
    """
    s_caption = models.CharField("Наименование", max_length=200)
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=True, verbose_name="Тмц", blank=True)

    class Meta:
        ordering = ["s_caption"]
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.s_caption

    def get_absolute_url(self):
        return reverse('MnfMaterial-detail', args=[str(self.id)])

    def __sync_with_good(self):
        """синхронизация с ТМЦ"""
        if self.id_good_id is None:
            self.id_good = GdsGood()

        gds = self.id_good
        gds.sCaption = self.s_caption
        gds.save()
        # чтобы обновилось поле в таблице
        self.id_good = gds

        print (self.id_good)
        print(self.id_good_id)

    def save(self, *args, **kwargs):
        self.__sync_with_good()
        super(MnfMaterial, self).save(*args, **kwargs)