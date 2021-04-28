from django.db import models


class TrdTradeSystem(models.Model):
    """
    Торговая система.
    Справочник возможных торговых площадок, откуда
    поступают заказы
    """
    s_caption = models.CharField("Наименование", max_length=256)

    class Meta:
        verbose_name = "Торговая система"
        verbose_name_plural = "Торговые системы"
        ordering = ["s_caption"]

    def __str__(self):
        return self.s_caption


class TrdDeliveryService(models.Model):
    """
    Служба доставки.
    Справочник возможных служб доставки
    """
    s_caption = models.CharField("Наименование", max_length=256)

    class Meta:
        verbose_name = "Служба доставки"
        verbose_name_plural = "Службы доставки"
        ordering = ["s_caption"]

    def __str__(self):
        return self.s_caption
