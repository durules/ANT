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
