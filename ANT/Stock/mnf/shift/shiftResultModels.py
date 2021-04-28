from django.db import models, transaction
from django.urls import reverse
from django.utils.timezone import localdate, localtime

from goods.models import GdsGood
from mnf.item.itemModels import MnfItemDet
from django.utils import timezone

from stock.app_exception import AppException
from stocks.models import StkAct, StkActDet


class MnfShiftResult(models.Model):
    """
    Результат смены.
    Описывает количество произведенных товаров и затраченные материалы.
    Для списания ТМЦ со склада формирует расходную накладную.
    """

    STATE_REGISTERING = "100"
    STATE_DONE = "300"

    s_state_choices = ((STATE_REGISTERING, "Оформляется"), (STATE_DONE, "Выполнен"))

    d_create_date = models.DateTimeField("Дата содания", db_index=True)
    # d_reg_date = models.DateTimeField("Дата проведения", null=True)
    s_state = models.CharField("Состояние", max_length=3, choices=s_state_choices, null=False)
    # Ссылка на сформированную расходную накладную
    id_act = models.ForeignKey('stocks.StkAct', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Расходная накладная")
    # Ссылка на сформированную приходную накладную
    id_act_in = models.ForeignKey('stocks.StkAct', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Приходная накладная", related_name='+')

    class Meta:
        verbose_name = "Отчет о выполненной работе"
        verbose_name_plural = "Отчеты о выполненной работе"

    def __str__(self):
        return self.get_head_line()

    def get_absolute_url(self):
        return reverse('mnf_shift_result-detail', args=[str(self.id)])

    def get_head_line(self):
        return "Отчет о выполненной работе от " + localtime(self.d_create_date).strftime('%d.%m.%Y %H:%M')

    @staticmethod
    def insert():
        obj = MnfShiftResult()
        obj.d_create_date = timezone.now()
        obj.s_state = "100"
        return obj

    # Синхронизация данных с накладной
    def __sync_with_act(self):
        # создание накладных
        act_out = self.id_act
        act_in = self.id_act_in

        if act_out is None:
            act_out = StkAct.inset_out_act()
            act_out.s_desc = "Сформирована от \"" + self.get_head_line() + "\""
            act_out.save()
            self.id_act = act_out

        if act_out.s_state != StkAct.STATE_REGISTERING:
            raise AppException("Ошибка синхронизации с расходной накладной. Накладная в неверном состоянии")

        if act_in is None:
            act_in = StkAct.inset_in_act()
            act_in.s_desc = "Сформирована от \"" + self.get_head_line() + "\""
            act_in.save()
            self.id_act_in = act_in

        if act_in.s_state != StkAct.STATE_REGISTERING:
            raise AppException("Ошибка синхронизации с приходной накладной. Накладная в неверном состоянии")

        # Формирование списка ТМЦ для накладной
        self_gds_out_dict = {}
        self_gds_in_dict = {}

        def add_qty(dict, id_good, n_qty):
            if id_good in dict:
                dict[id_good] = dict[id_good] + n_qty
            else:
                dict[id_good] = n_qty

        def add_out_qty(id_good, n_qty):
            add_qty(self_gds_out_dict, id_good, n_qty)

        def add_in_qty(id_good, n_qty):
            add_qty(self_gds_in_dict, id_good, n_qty)

        for shift_result_item in MnfShiftResultItems.objects.filter(id_shift_result = self):
            # приход
            add_in_qty(shift_result_item.id_item.id_good_id, shift_result_item.n_qty)

            # расход
            for item_det in MnfItemDet.objects.filter(id_item=shift_result_item.id_item):
                add_out_qty(item_det.id_good_id, item_det.n_qty * shift_result_item.n_qty)

        for shift_result_material in MnfShiftResultMaterials.objects.filter(id_shift_result = self):
            add_out_qty(shift_result_material.id_good_id, shift_result_material.n_qty)

        # обновление позиций
        act_out.apply_det_data(self_gds_out_dict)
        act_in.apply_det_data(self_gds_in_dict)

    # применение данных из формы редактирования
    def apply_form_data(self, changed_items_array, deleted_items_array, changed_materials_array, deleted_materials_array):
        # применение данных из формы редактирования
        with transaction.atomic():
            # блокируем объект
            if self.id is not None:
                old_obj = MnfShiftResult.objects.select_for_update().get(pk = self.id)
                if old_obj.s_state == MnfShiftResult.STATE_DONE:
                    raise AppException("Ошибка сохранения накладной. Накладная находится в состоянии Выполнен")

            self.s_state = MnfShiftResult.STATE_DONE
            self.save()

            for det in changed_items_array:
                det.id_shift_result = self
                det.save()

            for det in deleted_items_array:
                det.delete()

            for det in changed_materials_array:
                det.id_shift_result = self
                det.save()

            for det in deleted_materials_array:
                det.delete()

            # синхронизация с накладной
            self.__sync_with_act()
            StkAct.apply_done_state(self.id_act_id)
            StkAct.apply_done_state(self.id_act_in.id)

            self.save()

    @staticmethod
    def roll_back_state(id):
        # откат состояния
        with transaction.atomic():
            shift_result = MnfShiftResult.objects.select_for_update().get(pk=id)
            if shift_result.s_state == MnfShiftResult.STATE_REGISTERING:
                raise AppException("Ошибка отката отчета. Отчет находится в состоянии Оформляется")

            # Откат накладной
            act_out = shift_result.id_act
            act_in = shift_result.id_act_in
            if act_out is not None:
                StkAct.roll_back_state(act_out.id)
            if act_in is not None:
                StkAct.roll_back_state(act_in.id)

            shift_result.s_state = MnfShiftResult.STATE_REGISTERING
            shift_result.save()


class MnfShiftResultItems(models.Model):
    """
    Произведенные объекты.
    Перечень объектов, произведенных за смену.
    """
    id_shift_result = models.ForeignKey('MnfShiftResult', on_delete=models.CASCADE, null=False, verbose_name="Отчет о выполненной работе")
    id_item = models.ForeignKey('MnfItem', on_delete=models.PROTECT, null=False, verbose_name="Объект производства")
    n_qty = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Произведенный объект"
        verbose_name_plural = "Произведенные объекты"
        unique_together = [['id_shift_result', 'id_item']]


class MnfShiftResultMaterials(models.Model):
    """
    Дополнительные материалы.
    Здесь указываются дополнительно потраченные материалы, без учета материалов на объекты.
    Например брак.
    """
    id_shift_result = models.ForeignKey('MnfShiftResult', on_delete=models.CASCADE, null=False, verbose_name="Отчет о выполненной работе")
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=True, verbose_name="Тмц")
    n_qty = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Дополнительный материал"
        verbose_name_plural = "Дополнительные материалы"
        unique_together = [['id_shift_result', 'id_good']]