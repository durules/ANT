from typing import Dict, Any, Callable, Union

from django.db import models, transaction

from django.urls import reverse
from django.utils.datetime_safe import datetime

from stock.app_exception import AppException


class StkRemains(models.Model):
    """Остатки товаров.

    Изменение остатков производятся только через накладные.
    У накладной есть поле idSrcDoc, которое указывает на документ, создавший эту накладную."""

    # ТМЦ
    idGood = models.OneToOneField('goods.GdsGood', on_delete=models.CASCADE, null=False, verbose_name="Тмц")
    # Количество
    nQty = models.BigIntegerField("Количество")

    class Meta:
        verbose_name = "Остатки"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('StkRemains-detail', args=[str(self.id)])

    @staticmethod
    def apply_changes(remains_dict, n_direction):
        # Применение изменений в регистр остатков
        # n_direction - принимает значения (1 - добавить количества, -1 - удалить количества)

        remains_current_dict = StkRemains.get_remains_ids()
        for dict_key in remains_dict:
            id_good = dict_key
            n_qty = remains_dict[dict_key]
            if remains_current_dict.get(id_good) is None:
                obj = StkRemains.insert(id_good)
                obj.nQty = n_qty * n_direction
                obj.save()
            else:
                obj = StkRemains.objects.select_for_update().get(pk=remains_current_dict[id_good])
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
    """Накладные"""
    STATE_REGISTERING = "100"
    STATE_DONE = "300"

    s_state_choices = ((STATE_REGISTERING, "Оформляется"), (STATE_DONE, "Выполнен"))

    d_create_date = models.DateTimeField("Дата содания", db_index=True)
    d_reg_date = models.DateTimeField("Дата проведения", null=True)
    n_direction = models.SmallIntegerField("Направление", null=False)
    s_state = models.CharField("Состояние", max_length=3, choices=s_state_choices, null=False)
    s_desc = models.TextField("Описание", null=True, blank=True)

    class Meta:
        verbose_name = "Накладная"
        verbose_name_plural = "Накладные"

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

        print(res_dict)
        return res_dict

    def set_s_state(self, value: str):
        self.s_state = value
        self.set_d_reg_date(datetime.now())

    def get_absolute_url(self):
        return reverse('stk_act-detail', args=[str(self.id)])

    def apply_form_data(self, changed_act_det_array, deleted_act_det_array):
        # применение данных из формы редактирования
        with transaction.atomic():
            # блокируем объект
            if self.id:
                old_act = StkAct.objects.select_for_update().get(pk = self.id)
                if old_act.s_state == StkAct.STATE_DONE:
                    raise AppException("Ошибка сохранения накладной. Накладная находится в состоянии Выполнен")

            self.set_s_state(StkAct.STATE_DONE)
            self.save()

            for det in changed_act_det_array:
                det.id_act = self
                det.save()

            for det in deleted_act_det_array:
                det.delete()

            # Обновляем остатки
            qty_dict: Dict = self.__get_det_qty()
            StkRemains.apply_changes(qty_dict, self.n_direction)

    @staticmethod
    def roll_back_state(id):
        # откат состояния
        with transaction.atomic():
            act = StkAct.objects.select_for_update().get(pk=id)
            if act.s_state == StkAct.STATE_REGISTERING:
                raise AppException("Ошибка отката накладной. Накладная находится в состоянии Оформляется")

            act.set_s_state(StkAct.STATE_REGISTERING)
            act.save()

            # Обновляем остатки
            qty_dict: Dict = act.__get_det_qty()
            StkRemains.apply_changes(qty_dict, act.n_direction * -1)

    def __str__(self):
        if self.n_direction == 1:
            s_type = "Приходная"
        else:
            s_type = "Расходная"

        return s_type + " накладная от " + self.d_create_date.strftime('%d.%m.%Y %H:%M')

    def get_head_line(self):
        return self.__str__()


class StkActDet(models.Model):
    # Позиции накладной

    # Накладная
    id_act = models.ForeignKey('stocks.StkAct', on_delete=models.CASCADE, null=False, verbose_name="Накладная")
    # ТМЦ
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=False, verbose_name="Тмц")
    # Количество
    n_qty = models.BigIntegerField("Количество")

    class Meta:
        verbose_name = "Позиция накладной"
        verbose_name_plural = "Позиции накладной"

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
