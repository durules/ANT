import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, forms, \
    BaseInlineFormSet, inlineformset_factory, Textarea, DateInput, SelectDateWidget, TextInput, HiddenInput, CharField, \
    DateField, IntegerField, Select
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from goods.models import GdsGood
from trd.models import TrdTradeSystem
from trd.order.orderModels import TrdOrder, TrdOrderDet, TrdOrderStateHistory, TrdOrderState

n_gds_count = GdsGood.objects.count()


class TrdOrderListView(LoginRequiredMixin, generic.ListView):
    model = TrdOrder
    template_name = 'trd/order/trd_order_list.html'
    paginate_by = 100

    def __get_flt_d_date_from(self):
        str_value = self.request.GET.get('flt_d_date_from')
        if str_value is not None and not str_value == '':
            return datetime.datetime.strptime(str_value, "%d.%m.%Y").date()
        else:
            return None

    def __get_flt_d_date_to(self):
        str_value = self.request.GET.get('flt_d_date_to')
        if str_value is not None and not str_value == '':
            return datetime.datetime.strptime(str_value, "%d.%m.%Y").date()
        else:
            return None

    def __get_flt_id_trade_system(self):
        str_value = self.request.GET.get('flt_id_trade_system')
        if str_value is not None and not str_value == '':
            return int(str_value)
        else:
            return None

    def get_queryset(self):
        query_set = TrdOrder.objects
        d_date_from = self.__get_flt_d_date_from()
        d_date_to = self.__get_flt_d_date_to()
        id_trade_system = self.__get_flt_id_trade_system()
        if d_date_from is not None:
            query_set = query_set.filter(d_reg_date__gte=d_date_from)
        if d_date_to is not None:
            query_set = query_set.filter(d_reg_date__lte=d_date_to)
        if id_trade_system is not None:
            query_set = query_set.filter(id_trade_system_id=id_trade_system)
        return query_set.order_by("-d_reg_date")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['trade_system_list'] = TrdTradeSystem.objects.all()

        d_date_from = self.__get_flt_d_date_from()
        d_date_to = self.__get_flt_d_date_to()
        id_trade_system = self.__get_flt_id_trade_system()

        context['has_filter'] = d_date_from is not None or d_date_to is not None or id_trade_system is not None

        context['filter_form'] = TrdOrderListFilterForm(
            initial={
                'flt_d_date_from': d_date_from,
                'flt_d_date_to': d_date_to,
                'flt_id_trade_system': id_trade_system
            }
        )

        return context


class TrdOrderListFilterForm(forms.Form):
    flt_d_date_from = DateField(widget=DateInput(), label="Дата с", required=False)
    flt_d_date_to = DateField(widget=DateInput(), label="по", required=False)

    trade_system_choices = [
        (None, '-------')
    ]
    for trade_system in TrdTradeSystem.objects.all():
        trade_system_choices.append((trade_system.id, trade_system.s_caption))

    flt_id_trade_system = IntegerField(widget=Select(choices=trade_system_choices), label="Торговая система", required=False)


@login_required
def insert(request, id_trade_system):
    order = TrdOrder.inset_by_trade_system(id_trade_system, request.user.username)
    return trd_order_detail_by_instance(request, order)


@login_required
def trd_order_edit(request, pk):
    # редактирование заказа
    return HttpResponseRedirect(reverse('trd_order-detail', args=[str(pk)]))


@login_required
def trd_order_detail_by_instance(request, order):
    def _render(order_form, order_det_form_set):
        state_dict = {}
        for state in TrdOrderState.objects.all():
            state_dict[state.id] = state.s_caption

        state_history_list = []

        for state_history in TrdOrderStateHistory.objects.filter(id_order=order):
            s_state_from = ''
            if state_history.id_state_from is not None:
                s_state_from = state_dict[state_history.id_state_from]

            s_state_to = ''
            if state_history.id_state_to is not None:
                s_state_to = state_dict[state_history.id_state_to]

            state_history_list.append((state_history.d_date, s_state_from, s_state_to, state_history.s_user))

        return render(
            request,
            'trd/order/trd_order_detail.html',
            {
                'form': order_form,
                'det_form_set': order_det_form_set,
                'state_history_list': state_history_list
            }
        )

    # редактирование накладной по переданному экземпляру объекта
    if request.method == 'POST':
        order_form = TrdOrderForm(request.POST, prefix='order', instance=order)
        order_det_form_set = det_form_set_class(request.POST, prefix='det', instance=order)

        if order_form.is_valid() and order_det_form_set.is_valid():
            order_new = order_form.save(commit=False)
            order_det_array = order_det_form_set.save(False)

            # применение данных
            order_new.apply_form_data(order_det_array, order_det_form_set.deleted_objects, request.user.username)

            return HttpResponseRedirect(reverse('trd_order-detail', args = [order_new.id]))
        else:
            return _render(order_form, order_det_form_set)
    else:
        form = TrdOrderForm(instance=order, prefix='order')

        det_form_set = det_form_set_class(instance=order, prefix='det')
        return _render(form, det_form_set)


@login_required
def trd_order_detail(request, pk):
    # редактирование заказа
    order = TrdOrder.objects.get(pk=pk)
    return trd_order_detail_by_instance(request, order)


class TrdOrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TrdOrderForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['d_reg_date'].label = "Дата"
        if instance:
            if instance.id_state.n_order is not None:
                if instance.id_state.n_order > 100:
                    self.fields['d_reg_date'].widget = DateInput()
                    self.fields['d_reg_date'].widget.attrs['readonly'] = True

    class Meta:
        model = TrdOrder
        fields = [
            'id_state', 'd_reg_date', 's_reg_num', 's_receiver',
            's_address', 's_track_num', 'id_delivery_service', 's_desc'
        ]
        widgets = {
            's_desc': Textarea(attrs={'rows': 15}),
            's_address': Textarea(attrs={'rows': 4}),
            'd_reg_date': SelectDateWidget()
        }


class TrdOrderDetForm(ModelForm):
    class Meta:
        model = TrdOrderDet
        fields = [
            'id_good', 'n_qty'
        ]

    def __init__(self, *args, **kwargs):
        super(TrdOrderDetForm, self).__init__(*args, **kwargs)

        if self.instance:
            if self.instance.id_order_id is not None:
                if self.instance.id_order.id_state is not None:
                    if self.instance.id_order.id_state.is_write_off_goods():
                        for field_name in self.fields:
                            # скрываем, т.к. в шаблоне выводим данные без формы
                            self.fields[field_name].widget = HiddenInput()


class TrdOrderDetFormSet(BaseInlineFormSet):
    def clean(self):
        super(TrdOrderDetFormSet, self).clean()

        if any(self.errors):
            return

        id_goods = []
        for form in self.forms:
            if 'id_good' in form.cleaned_data:
                id_good = form.cleaned_data['id_good']
                if id_good:
                    # проверка на ункальность ТМЦ
                    if id_good in id_goods:
                        raise forms.ValidationError("Тмц в позициях должены быть уникальны")

                    id_goods.append(id_good)

                    # проверка, что количество неотрицательно
                    if 'n_qty' in form.cleaned_data:
                        if form.cleaned_data['n_qty'] < 0:
                            raise forms.ValidationError("Количество должно быть больше 0")
                    else:
                        raise forms.ValidationError("Не указано количество")


det_form_set_class = inlineformset_factory(
            TrdOrder,
            TrdOrderDet,
            fields=['id_good', 'n_qty'],
            max_num=n_gds_count,
            extra=n_gds_count,
            formset=TrdOrderDetFormSet,
            form=TrdOrderDetForm
        )

