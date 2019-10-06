from django.db import models

# ТМЦ
from django.urls import reverse


class StkRemains(models.Model):
    # Остатки товаров

    # ТМЦ
    idGood = models.OneToOneField('goods.GdsGood', on_delete=models.CASCADE, null=False)
    # Количество
    nQty = models.BigIntegerField("Количество")

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('StkRemains-detail', args=[str(self.id)])
