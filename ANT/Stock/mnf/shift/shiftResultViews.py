import json

from dal import autocomplete
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
from mnf.item.itemModels import MnfItem
from mnf.shift.shiftResultModels import MnfShiftResult, MnfShiftResultItems, MnfShiftResultMaterials
from stocks.models import StkAct, StkActDet

n_item_count = MnfItem.objects.count()
n_good_count = GdsGood.objects.count()


class MnfShiftResultListView(LoginRequiredMixin, generic.ListView):
    model = MnfShiftResult
    template_name = 'mnf/shift/mnf_shift_result_list.html'
    paginate_by = 100

    def get_queryset(self):
        return MnfShiftResult.objects.all().order_by("-d_create_date")


@login_required
def insert(request):
    act = MnfShiftResult.insert()
    return mnf_shift_result_detail_by_instance(request, act)


@login_required
def mnf_shift_result_edit(request, pk):
    # редактирование принятой накладной
    MnfShiftResult.roll_back_state(pk)
    return HttpResponseRedirect(reverse('mnf_shift_result-detail', args=[str(pk)]))


@login_required
def mnf_shift_result_detail_by_instance(request, instance):

    # редактирование отчета по переданному экземпляру объекта
    if request.method == 'POST':
        shift_result_form = MnfShiftResultForm(request.POST, prefix='header', instance=instance)
        mnf_shift_result_items_form_set = items_form_set_class(request.POST, prefix='det_items', instance=instance)
        mnf_shift_result_materials_form_set = materials_form_set_class(request.POST, prefix='det_materials', instance=instance)

        if shift_result_form.is_valid() and mnf_shift_result_items_form_set.is_valid() and mnf_shift_result_materials_form_set.is_valid():
            shift_result_new = shift_result_form.save(commit=False)
            items_det_array = mnf_shift_result_items_form_set.save(False)
            materials_det_array = mnf_shift_result_materials_form_set.save(False)

            # применение данных
            shift_result_new.apply_form_data(
                items_det_array,
                mnf_shift_result_items_form_set.deleted_objects,
                materials_det_array,
                mnf_shift_result_materials_form_set.deleted_objects
            )

            return HttpResponseRedirect(reverse('mnf_shift_results'))
        else:
            return render(request, 'mnf/shift/mnf_shift_result_detail.html', {'form': shift_result_form, 'det_items_set': mnf_shift_result_items_form_set, 'det_materials_set': mnf_shift_result_materials_form_set})
    else:
        shift_result_form = MnfShiftResultForm(prefix='header', instance=instance)
        mnf_shift_result_items_form_set = items_form_set_class(prefix='det_items', instance=instance)
        mnf_shift_result_materials_form_set = materials_form_set_class(prefix='det_materials',
                                                                       instance=instance)

        return render(request, 'mnf/shift/mnf_shift_result_detail.html', {'form': shift_result_form, 'det_items_set': mnf_shift_result_items_form_set, 'det_materials_set': mnf_shift_result_materials_form_set})


@login_required
def mnf_shift_result_detail(request, pk):
    # редактирование отчета в состоянии оформляется
    act = MnfShiftResult.objects.get(pk=pk)
    return mnf_shift_result_detail_by_instance(request, act)


class MnfShiftResultForm(ModelForm):
    class Meta:
        model = MnfShiftResult
        fields = ['s_state']
        widgets = {'s_state': HiddenInput()}


class MnfShiftResultItemsFormSet(BaseInlineFormSet):
    pass


class MnfShiftResultMaterialsFormSet(BaseInlineFormSet):
    pass


items_form_set_class = inlineformset_factory(
            MnfShiftResult,
            MnfShiftResultItems,
            fields=['id_item', 'n_qty'],
            max_num=n_item_count,
            extra=n_item_count,
            formset=MnfShiftResultItemsFormSet,
            widgets={
                'id_item': autocomplete.ModelSelect2(
                     url='mnf-item-autocomplete',
                )
            }
        )


materials_form_set_class = inlineformset_factory(
            MnfShiftResult,
            MnfShiftResultMaterials,
            fields=['id_good', 'n_qty'],
            max_num=n_good_count,
            extra=n_good_count,
            formset=MnfShiftResultMaterialsFormSet,
            widgets={
                'id_good': autocomplete.ModelSelect2(
                     url='gds-good-autocomplete',
                )
            }
        )