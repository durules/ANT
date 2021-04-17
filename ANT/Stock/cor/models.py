from django.db import models

# Create your models here.

class CorColor(models.Model):
    """
    Цвет.
    Хранит наименование цвета и его hex-код.
    """
    s_caption = models.CharField("Наименование", max_length=200)
    # цвет раскраски, например #875f5c
    s_color = models.CharField("Цвет", max_length=200)

    class Meta:
        ordering = ["s_caption"]
        verbose_name = "Цвет"
        verbose_name_plural = "Цвет"

    def __str__(self):
        return self.s_caption
