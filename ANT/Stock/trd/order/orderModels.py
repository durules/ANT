from django.db import models, transaction
from django.urls import reverse

from cor.state.stateModels import CorState, CorStateHistory
from django.utils.timezone import localtime
from django.utils import timezone

from cor.exception.app_exception import AppException
from stocks.models import StkAct


class TrdOrderState(CorState):
    """
    Состояния заказа.
    """

    class Meta:
        verbose_name = "Состояние заказа"
        verbose_name_plural = "Состояния заказа"

    @staticmethod
    def get_start_state():
        return TrdOrderState.objects.order_by('n_order')[0]

    def is_write_off_goods(self):
        # признак, что в этом состоянии списываются тмц со склада
        if self.n_order is None:
            return False
        else:
            return self.n_order >= TrdOrderState.get_write_off_state_number()

    @staticmethod
    def get_write_off_state_number():
        # Номер состояния, начиная с которого списываются ТМЦ со склада
        return 300

    @staticmethod
    def get_is_finished_state_number():
        # Номер состояния, начиная с которого заказ считается завершенным
        return 500

    def is_finished(self):
        # признак, что в этом состоянии заказ считаются завершенным
        if self.n_order is None:
            return False
        else:
            return self.n_order >= TrdOrderState.get_is_finished_state_number()


class TrdOrderStateHistory(CorStateHistory):
    """
    История состояний заказа.
    """

    id_order = models.ForeignKey('TrdOrder', on_delete=models.CASCADE, null=False, verbose_name="Заказ")

    class Meta:
        verbose_name = "История состояний заказа"
        verbose_name_plural = "Истории состояний заказа"

    @staticmethod
    def create_item(id_order_id, id_state_from, id_state_to, s_user):
        if not id_state_from == id_state_to:
            obj = TrdOrderStateHistory()
            obj.id_order_id = id_order_id
            obj.fill_on_insert(id_state_from, id_state_to, s_user)
            obj.save()
            return obj
        else:
            return None


class TrdOrderPriorityLevel(models.Model):
    """
    Уровень приоритета заказа.
    Позволяет настроить уровни приоритетов заказов
    """
    id_color = models.ForeignKey('cor.CorColor', on_delete=models.PROTECT, null=False, verbose_name="Цвет")

    # чем выше число, тем более приоритетный уровнь
    n_level = models.PositiveIntegerField(verbose_name="Уровень", blank=True, null=True)

    class Meta:
        verbose_name = "Уровень приоритета заказа"
        verbose_name_plural = "Уровени приоритета заказа"

    def __str__(self):
        if not self.id_color:
            return str(self.id)
        else:
            return str(self.id_color)


class TrdOrderStatePriorityLevel(models.Model):
    """
    Уровни состояний заказа.
    Для состояния заказа позволяет настроить при каком количестве дней
    после оформления заказа, он считается более приоритетным
    """
    id_order_state = models.ForeignKey('TrdOrderState', on_delete=models.CASCADE, null=False,
                                       verbose_name="Состояние заказа")
    id_trade_system = models.ForeignKey('TrdTradeSystem', on_delete=models.CASCADE, null=False,
                                        verbose_name="Торговая система")
    id_level = models.ForeignKey('TrdOrderPriorityLevel', on_delete=models.PROTECT, null=False, verbose_name="Уровень")
    n_from = models.PositiveIntegerField(verbose_name="Дней от", blank=True, null=True)
    n_to = models.PositiveIntegerField(verbose_name="до", blank=True, null=True)

    class Meta:
        verbose_name = "Уровень состояния заказа"
        verbose_name_plural = "Уровни состояния заказа"
        unique_together = [['id_order_state', 'id_trade_system', 'id_level']]
        ordering = ["id_trade_system", "id_order_state"]

    def __str__(self):
        if not self.id_level:
            return str(self.id)
        else:
            return self.id_level.id_color.s_color

    def get_color(self):
        if self.id_level_id is not None:
            if self.id_level.id_color_id is not None:
                return self.id_level.id_color.s_color
        return None


class TrdOrder(models.Model):
    """
    Заказ.
    """

    # Дата создания
    d_create_date = models.DateTimeField("Дата содания")
    # Дата заказа из торговой системы
    d_reg_date = models.DateTimeField("Дата регистрации", db_index=True)
    id_state = models.ForeignKey('TrdOrderState', on_delete=models.PROTECT, verbose_name="Состояние")
    id_trade_system = models.ForeignKey('TrdTradeSystem', on_delete=models.PROTECT, verbose_name="Торговая система", null=True, blank=True)
    s_desc = models.TextField("Описание", null=True, blank=True)

    # Ссылка на сформированную расходную накладную
    id_act_out = models.ForeignKey('stocks.StkAct', on_delete=models.PROTECT, null=True, blank=True,
                                   verbose_name="Расходная накладная")

    s_reg_num = models.CharField("Номер", null=True, blank=True, max_length=256, db_index=True)
    s_receiver = models.CharField("Получатель", null=True, blank=True, max_length=512)
    s_address = models.CharField("Адрес", null=True, blank=True, max_length=4000)
    s_track_num = models.CharField("Трек-номер", null=True, blank=True, max_length=256)
    id_delivery_service = models.ForeignKey('TrdDeliveryService', on_delete=models.PROTECT, null=True, blank=True,
                                            verbose_name="Служба доставки")

    class Meta:
        ordering = ["d_reg_date"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.get_head_line()

    def get_absolute_url(self):
        return reverse('trd_order-detail', args=[str(self.id)])

    def get_head_line(self):
        if self.id_trade_system is not None:
            trade_system = " из \"" + str(self.id_trade_system.s_caption) + "\""
        else:
            trade_system = ""

        if self.s_reg_num is not None:
            reg_num = " № " + str(self.s_reg_num)
        else:
            reg_num = ""

        return "Заказ" + reg_num + trade_system + " от " +  localtime(self.d_reg_date).strftime('%d.%m.%Y')

    def set_d_create_date(self, value: timezone):
        self.d_create_date = value

    def set_d_reg_date(self, value: timezone):
        self.d_reg_date = value

    def set_s_reg_num(self, value):
        self.s_reg_num = value

    def set_s_receiver(self, value):
        self.s_receiver = value

    def set_s_address(self, value):
        self.s_address = value

    def set_s_track_num(self, value):
        self.s_track_num = value

    def set_id_delivery_service(self, value):
        self.id_delivery_service = value

    def set_id_state(self, value: float, s_user):
        old_id_state = None
        old_id_state_id = None
        if self.id_state_id is not None:
            old_id_state = self.id_state
            old_id_state_id = old_id_state.id
        with transaction.atomic():
            self.id_state = TrdOrderState.objects.get(pk=value)

            # чтобы история состояний не ругалась, что нет заказа, когда мы его только создаем, и ставим стартовое состояние
            self.save()
            TrdOrderStateHistory.create_item(self.id, old_id_state_id, self.id_state.id, s_user)
            if old_id_state is not None and old_id_state.is_write_off_goods() and not self.id_state.is_write_off_goods():
                # откатываем накладную
                if self.id_act_out is not None:
                    StkAct.roll_back_state(self.id_act_out.id)
            elif (old_id_state is None or not old_id_state.is_write_off_goods()) and self.id_state.is_write_off_goods():
                # применяем накладную
                self.__sync_with_act()
                StkAct.apply_done_state(self.id_act_out_id)

            self.save()

    def set_id_trade_system(self, value: float):
        self.id_trade_system_id = value

    @staticmethod
    def __insert(s_user):
        obj = TrdOrder()
        obj.set_d_create_date(timezone.now())
        obj.set_d_reg_date(timezone.now())
        obj.set_id_state(TrdOrderState.get_start_state().id, s_user)
        obj.save()
        return obj

    @staticmethod
    def inset_by_trade_system(id_trade_system_id, s_user):
        obj = TrdOrder.__insert(s_user)
        obj.set_id_trade_system(id_trade_system_id)
        obj.save()
        return obj

    # Синхронизация данных с накладной
    def __sync_with_act(self):
        # создание накладных
        act_out = self.id_act_out

        if act_out is None:
            act_out = StkAct.inset_out_act()
            act_out.s_desc = "Сформирована от \"" + self.get_head_line() + "\""
            act_out.save()
            self.id_act_out = act_out

        if act_out.s_state != StkAct.STATE_REGISTERING:
            raise AppException("Ошибка синхронизации с расходной накладной. Накладная в неверном состоянии")

        # Формирование списка ТМЦ для накладной
        self_gds_out_dict = {}

        def add_qty(id_good, n_qty):
            if id_good in self_gds_out_dict:
                self_gds_out_dict[id_good] = self_gds_out_dict[id_good] + n_qty
            else:
                self_gds_out_dict[id_good] = n_qty

        for order_det in TrdOrderDet.objects.filter(id_order=self):
            add_qty(order_det.id_good_id, order_det.n_qty)

        act_out.apply_det_data(self_gds_out_dict)

    def apply_form_data(self, changed_act_det_array, deleted_act_det_array, s_user):
        # применение данных из формы редактирования
        with transaction.atomic():
            old_order = None
            # блокируем объект
            if self.id is not None:
                old_order = TrdOrder.objects.select_for_update().get(pk = self.id)

            self.save()

            for det in changed_act_det_array:
                det.id_order = self
                det.save()

            for det in deleted_act_det_array:
                det.delete()

            # Переводим в состояние, которое было до изменений в форме, чтобы сттер состояния корректно отработал
            id_new_state_id = self.id_state_id
            if old_order is not None:
                self.id_state = old_order.id_state
            else:
                self.id_state = None
            self.set_id_state(id_new_state_id, s_user)
            self.save()

    def get_level_by_state(self):
        # Получение уровня состояния (TrdOrderStateLevel) в котором находится заказ
        if self.id_state is None:
            return None
        else:
            current_date = timezone.now().date()
            order_date = localtime(self.d_reg_date).date()
            diff = abs((current_date - order_date).days)
            for level in TrdOrderStatePriorityLevel.objects.filter(id_order_state=self.id_state).filter(id_trade_system=self.id_trade_system):
                if (level.n_from is None or level.n_from <= diff) and (level.n_to is None or level.n_to >= diff):
                    return level


class TrdOrderDet(models.Model):
    # Позиции заказа

    # Заказ
    id_order = models.ForeignKey('TrdOrder', on_delete=models.CASCADE, null=False, verbose_name="Накладная")
    # ТМЦ
    id_good = models.ForeignKey('goods.GdsGood', on_delete=models.PROTECT, null=False, verbose_name="Тмц")
    # Количество
    n_qty = models.BigIntegerField("Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        unique_together = [['id_order', 'id_good']]

    @staticmethod
    def insert(id_order, id_good):
        n_order_max = 0

        for det in TrdOrderDet.objects.filter(id_order=id_order).filter(id_good_id=id_good):
            if det.id_good_id == id_good:
                raise AppException("Позиция с таким ТМЦ и Накладной уже существует")

            if det.n_order > n_order_max:
                n_order_max = det.n_order

        obj = TrdOrderDet()
        obj.set_id_order(id_order)
        obj.set_id_good(id_good)
        obj.set_n_order(n_order_max + 1)
        return obj

    def set_id_order(self, value: float):
        self.id_order_id = value

    def set_id_good(self, value):
        self.id_good_id = value

    def set_n_qty(self, value: int):
        if value < 0:
            raise AppException('Количество не должно быть отрицательным')

        self.n_qty = value

    def set_n_order(self, value: int):
        self.n_order = value
