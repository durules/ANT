import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm, formset_factory, BaseModelFormSet, modelformset_factory, HiddenInput, forms, \
    BaseInlineFormSet, inlineformset_factory
from django.forms.models import ModelFormMetaclass
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.db import models

from goods.models import GdsGood
from stocks.models import StkAct, StkActDet

n_gds_count = GdsGood.objects.count()


class StkActListView(LoginRequiredMixin, generic.ListView):
    model = StkAct
    template_name = 'stocks/act/stk_act_list.html'
    paginate_by = 100

    def get_queryset(self):
        return StkAct.objects.all().order_by("-d_create_date")


@login_required
def insert_in_act(request):
    act = StkAct.inset_in_act()
    return stk_act_detail_by_instance(request, act)


@login_required
def insert_out_act(request):
    act = StkAct.inset_out_act()
    return stk_act_detail_by_instance(request, act)


@login_required
def stk_act_edit(request, pk):
    # редактирование принятой накладной
    StkAct.roll_back_state(pk)
    return HttpResponseRedirect(reverse('stk_act-detail', args=[str(pk)]))


@login_required
def stk_act_detail_by_instance(request, act):
    # редактирование накладной по переданному экземпляру объекта
    if request.method == 'POST':
        act_form = StkActForm(request.POST, prefix='act', instance=act)
        act_det_form_set = det_form_set_class(request.POST, prefix='det', instance=act)

        if act_form.is_valid() and act_det_form_set.is_valid():
            act_new = act_form.save(commit=False)
            act_det_array = act_det_form_set.save(False)

            # применение данных
            act_new.apply_form_data(act_det_array, act_det_form_set.deleted_objects)

            return HttpResponseRedirect(reverse('stk_acts'))
        else:
            return render(request, 'stocks/act/stk_act_detail.html', {'form': act_form, 'det_form_set': act_det_form_set})
    else:
        form = StkActForm(instance=act, prefix='act')

        det_form_set = det_form_set_class(instance=act, prefix='det')
        return render(request, 'stocks/act/stk_act_detail.html', {'form': form, 'det_form_set': det_form_set})


@login_required
def stk_act_detail(request, pk):
    # редактирование на кладной в состоянии оформляется
    act = StkAct.objects.get(pk=pk)
    return stk_act_detail_by_instance(request, act)


class StkActForm(ModelForm):
    class Meta:
        model = StkAct
        fields = ['s_state', 'n_direction']
        widgets = {'n_direction': HiddenInput(), 's_state': HiddenInput()}


class StkActDetFormSet(BaseInlineFormSet):
    def clean(self):
        super(StkActDetFormSet, self).clean()

        if any(self.errors):
            return

        id_goods = []
        for form in self.forms:
            if 'id_good' in form.cleaned_data:
                id_good = form.cleaned_data['id_good']
                if id_good:
                    # проверка на ункальность ТМЦ
                    if id_good in id_goods:
                        print('Тмц в позициях должены быть уникальны')
                        raise forms.ValidationError("Тмц в позициях должены быть уникальны")

                    id_goods.append(id_good)

                    # проверка, что количество неотрицательно
                    if 'n_qty' in form.cleaned_data:
                        if form.cleaned_data['n_qty'] < 0:
                            print('Количество должно быть больше 0')
                            raise forms.ValidationError("Количество должно быть больше 0")
                    else:
                        print('Не указано количество')
                        raise forms.ValidationError("Не указано количество")


det_form_set_class = inlineformset_factory(
            StkAct,
            StkActDet,
            fields=['id_good', 'n_qty'],
            max_num=n_gds_count,
            extra=n_gds_count,
            formset=StkActDetFormSet
        )