from django.db import models, transaction
from django.urls import reverse
from django.utils.timezone import localdate, localtime

from goods.models import GdsGood
from mnf.item.itemModels import MnfItemDet
from django.utils import timezone

from stock.app_exception import AppException
from stocks.models import StkAct, StkActDet


class CorState(models.Model):
    """
    Состояния сущности.
    """
    s_caption = models.CharField("Наименование", null=False, max_length=256)
    n_order = models.IntegerField("Порядковый номер состояния")

    class Meta:
        ordering = ["n_order"]
        abstract = True

    def __str__(self):
        return self.s_caption


class CorStateHistory(models.Model):
    """
    История состояний.
    Хранит историю о том, из какого и в какое состояние был переведен объект.

    Модель, которая реализует этот класс, должна обладать ссылкой на объект, историю состояний
    которого она хранит.
    """
    d_date = models.DateTimeField("Дата")
    s_user = models.CharField("Пользователь", max_length=256)
    id_state_from = models.BigIntegerField("Состояние из", null=True)
    id_state_to = models.BigIntegerField("Состояние в")

    class Meta:
        abstract = True

    def fill_on_insert(self, id_state_from, id_state_to, s_user) :
        self.id_state_from = id_state_from
        self.id_state_to = id_state_to
        self.d_date = timezone.now()
        self.s_user = s_user
