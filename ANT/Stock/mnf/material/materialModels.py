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

    def get_remains_level(self, n_qty):
        # получение уровня остатков по количеству
        # возвращает объект класса MnfRemainsLevel, или None если не найден
        for mat_level in MnfMaterialRemainsLevel.objects.filter(id_material=self):
            if (mat_level.n_from is None or mat_level.n_from <= n_qty) and (mat_level.n_to is None or mat_level.n_to >= n_qty):
                return mat_level.id_level

        return None


class MnfMaterialRemainsLevel(models.Model):
    """
    Уровни остатков материала.
    Для конкретного материала позволяет настроить количества,
    при которых наступает тот или иной уровень
    """
    id_material = models.ForeignKey('MnfMaterial', on_delete=models.CASCADE, null=False, verbose_name="Материал")
    id_level = models.ForeignKey('MnfRemainsLevel', on_delete=models.PROTECT, null=False, verbose_name="Уровень")
    n_from = models.PositiveIntegerField(verbose_name="Количество от", blank=True, null=True)
    n_to = models.PositiveIntegerField(verbose_name="до", blank=True, null=True)

    class Meta:
        verbose_name = "Уровень остатков материала"
        verbose_name_plural = "Уровни остатков материала"
        unique_together= [['id_material', 'id_level']]

    def __str__(self):
        if not self.id_level:
            return str(self.id)
        else:
            return self.id_level.s_caption


class MnfRemainsLevel(models.Model):
    """
    Уровень остатков.
    Позволяет настроить раскраску остатков материалов, в зависимости
    от их количества на складе.
    """
    s_caption = models.CharField("Наименование", max_length=200)
    # цвет раскраски, например #875f5c
    s_color = models.CharField("Цвет", max_length=200)

    class Meta:
        ordering = ["s_caption"]
        verbose_name = "Уровень остатков"
        verbose_name_plural = "Уровни остатков"

    def __str__(self):
        return self.s_caption