from django.db import models


from django.urls import reverse


class GdsGood(models.Model):
    """Товаро-материальная ценность"""
    sCaption = models.CharField("Наименование", max_length=200)

    class Meta:
        ordering = ["sCaption"]
        verbose_name = "ТМЦ"
        verbose_name_plural = "ТМЦ"

    def __str__(self):
        return self.sCaption

    def get_absolute_url(self):
        return reverse('GdsGood-detail', args=[str(self.id)])

    def get_remains_level(self, n_qty):
        # получение уровня остатков по количеству
        # возвращает объект класса MnfRemainsLevel, или None если не найден
        for rem_level in GdsGoodRemainsLevel.objects.filter(id_good=self):
            if (rem_level.n_from is None or rem_level.n_from <= n_qty) and (rem_level.n_to is None or rem_level.n_to >= n_qty):
                return rem_level.id_color

        return None


class GdsGoodRemainsLevel(models.Model):
    """
    Уровни остатков ТМЦ.
    Для конкретного тмц позволяет настроить количества,
    при которых наступает тот или иной уровень
    """
    id_good = models.ForeignKey('GdsGood', on_delete=models.CASCADE, null=False, verbose_name="ТМЦ")
    id_color = models.ForeignKey('cor.CorColor', on_delete=models.PROTECT, null=False, verbose_name="Цвет")
    n_from = models.PositiveIntegerField(verbose_name="Количество от", blank=True, null=True)
    n_to = models.PositiveIntegerField(verbose_name="до", blank=True, null=True)

    class Meta:
        verbose_name = "Уровень остатков тмц"
        verbose_name_plural = "Уровни остатков тмц"
        unique_together= [['id_good', 'id_color']]

    def __str__(self):
        if not self.id_color:
            return str(self.id)
        else:
            return self.id_color.s_caption

