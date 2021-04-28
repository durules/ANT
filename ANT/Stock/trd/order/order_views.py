from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, forms, \
    BaseInlineFormSet, inlineformset_factory, Textarea, DateInput, SelectDateWidget
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from goods.models import GdsGood
from trd.models import TrdTradeSystem
from trd.order.orderModels import TrdOrder, TrdOrderDet

n_gds_count = GdsGood.objects.count()


class TrdOrderListView(LoginRequiredMixin, generic.ListView):
    model = TrdOrder
    template_name = 'trd/order/trd_order_list.html'
    paginate_by = 100

    def get_queryset(self):
        return TrdOrder.objects.all().order_by("-d_reg_date")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['trade_system_list'] = TrdTradeSystem.objects.all()

        color_dict = {}

        return context


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
            return render(request, 'trd/order/trd_order_detail.html', {'form': order_form, 'det_form_set': order_det_form_set})
    else:
        form = TrdOrderForm(instance=order, prefix='order')

        det_form_set = det_form_set_class(instance=order, prefix='det')
        return render(request, 'trd/order/trd_order_detail.html', {'form': form, 'det_form_set': det_form_set})


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
            formset=TrdOrderDetFormSet
        )