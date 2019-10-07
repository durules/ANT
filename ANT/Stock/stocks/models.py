from typing import Dict, Any, Callable, Union

from django.db import models

# ТМЦ
from django.urls import reverse
from django.utils.datetime_safe import datetime

from stock.app_exception import AppException


class StkRemains(models.Model):
    # Остатки товаров

    # ТМЦ
    idGood = models.OneToOneField('goods.GdsGood', on_delete=models.CASCADE, null=False, verbose_name="Тмц")
    # Количество
    nQty = models.BigIntegerField("Количество")

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('StkRemains-detail', args=[str(self.id)])

    # Применение изменений в регистр остатков
    # n_direction - принимает значения (1 - добавить количества, -1 - удалить количества)
    @staticmethod
    def apply_changes(remains_dict, n_direction):
        remains_current_dict = StkRemains.get_remains_ids()
        for dict_key in remains_dict:
            id_good = dict_key
            n_qty = remains_dict[dict_key]
            if remains_current_dict.get(id_good) is None:
                obj = StkRemains.insert(id_good)
                obj.nQty = n_qty * n_direction
                obj.save()
            else:
                obj = StkRemains.objects.get(pk=remains_current_dict[id_good])
                obj.nQty = obj.nQty + n_qty * n_direction
                obj.save()

    # Получение остатков по каждому из ТМЦ
    # Возвращет словарь ид ТМЦ - колечество
    @staticmethod
    def get_remains():
        remains = StkRemains.objects.all()

        remains_by_good_dict = {}
        for remain in remains:
            remains_by_good_dict[remain.idGood_id] = remain.nQty
        return remains_by_good_dict

    # Получение индентификаторов записей остатков
    # Возвращет словарь ид ТМЦ - ид записи
    @staticmethod
    def get_remains_ids():
        remains = StkRemains.objects.all()

        remains_dict = {}
        for remain in remains:
            remains_dict[remain.idGood_id] = remain.id
        return remains_dict

    @staticmethod
    def insert(id_good):
        return StkRemains(idGood_id=id_good, nQty=0)


class StkAct(models.Model):
    STATE_REGISTERING = "100"
    STATE_DONE = "300"

    s_state_choices = ((STATE_REGISTERING, "Оформляется"), (STATE_DONE, "Выполнен"))

    # Накладные

    d_create_date = models.DateTimeField("Дата содания")
    d_reg_date = models.DateTimeField("Дата проведения")
    n_direction = models.SmallIntegerField("Направление", null=False)
    s_state = models.CharField("Состояние", max_length=3, choices=s_state_choices)

    @staticmethod
    def __insert():
        obj = StkAct()
        obj.set_d_create_date(datetime.now())
        obj.set_s_state("100")
        return obj

    @staticmethod
    def inset_in_act():
        obj = StkAct.__insert()
        obj.set_n_direction(1)
        return obj

    @staticmethod
    def inset_out_act():
        obj = StkAct.__insert()
        obj.set_n_direction(-1)
        return obj

    def set_d_create_date(self, value: datetime):
        self.d_create_date = value

    def set_d_reg_date(self, value: datetime):
        self.d_reg_date = value

    def set_n_direction(self, value: int):
        self.n_direction = value

    # Получение данных по позициям, в виде словаря - ид ТМЦ - количество
    def __get_det_qty(self) -> Dict:
        res_dict: Dict = {}

        for det in StkActDet.objects.filter(id_act_id=self.id):
            # Хоть записи и должны быть уникальны, на всякий случай слкадываю
            res_dict[det.id_good_id] = res_dict.get(det.id_good_id, 0) + det.n_qty

        return res_dict

    def set_s_state(self, value: str):
        s_old_state = self.s_state

        if s_old_state == StkAct.STATE_REGISTERING and value == StkAct.STATE_DONE:
            # Перевод в Выполнен. Обновляем остатки
            qty_dict: Dict = self.__get_det_qty
            StkRemains.apply_changes(qty_dict, self.n_direction)

        elif s_old_state == StkAct.STATE_DONE and value == StkAct.STATE_REGISTERING:
            # Перевод в Оформляется. Откатываем изменения на складе
            qty_dict = self.__get_det_qty
            StkRemains.apply_changes(qty_dict, self.n_direction * -1)

        self.s_state = value

    def get_s_state(self):
        return self.s_state


class StkActDet(models.Model):
    # Позиции накладной

    # Накладная
    id_act = models.ForeignKey('stocks.StkAct', on_delete=models.CASCADE, null=False, verbose_name="Накладная")
    # Номер позиции
    n_order = models.IntegerField("Номер")
    # ТМЦ
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=False, verbose_name="Тмц")
    # Количество
    n_qty = models.BigIntegerField("Количество")

    @staticmethod
    def insert(id_act, id_good):
        n_order_max = 0

        for det in StkActDet.objects.filter(id_act_id=id_act).filter(id_good_id=id_good):
            if det.id_good_id == id_good:
                raise AppException("Позиция с таким ТМЦ и Накладной уже существует")

            if det.n_order > n_order_max:
                n_order_max = det.n_order

        obj = StkActDet()
        obj.set_id_act(id_act)
        obj.set_id_good(id_good)
        obj.set_n_order(n_order_max + 1)
        return obj

    def set_id_act(self, value: float):
        self.id_act_id = value

    def set_id_good(self, value: datetime):
        self.id_good_id = value

    def set_n_qty(self, value: int):
        if value < 0:
            raise AppException('Количество не должно быть отрицательным')

        self.n_qty = value

    def set_n_order(self, value: int):
        self.n_order = value
