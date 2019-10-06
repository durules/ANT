from django.db import models


from django.urls import reverse


class GdsGood(models.Model):
    # ТМЦ
    sCaption = models.CharField("Наименование", max_length=200)

    class Meta:
        ordering = ["sCaption"]

    def __str__(self):
        return self.sCaption

    def get_absolute_url(self):
        return reverse('GdsGood-detail', args=[str(self.id)])