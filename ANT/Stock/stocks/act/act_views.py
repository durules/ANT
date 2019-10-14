from django.forms import ModelForm, formset_factory, BaseModelFormSet, modelformset_factory, HiddenInput
from django.forms.models import ModelFormMetaclass
from django.shortcuts import render
from django.views import generic
from django.db import models

from stocks.models import StkAct, StkActDet


class StkActListView(generic.ListView):
    model = StkAct
    template_name = 'act/stk_act_list.html'
    paginate_by = 100

    def get_queryset(self):
        return StkAct.objects.all().order_by("-d_create_date")


def insert_in_act(request):
    act = StkAct.inset_in_act()
    stk_act_detail(request, act.id)


def insert_out_act(request):
    act = StkAct.inset_out_act()
    stk_act_detail(request, act.id)


def stk_act_detail(request, pk):
    if request.method == 'POST':
        form = StkActForm(request.POST)
        if form.is_valid():
            return "Ok"
    else:
        act = StkAct.objects.get(pk=pk)
        form = StkActForm(instance=act)

    det_form_set_class = modelformset_factory(
        StkActDet,
        fields=['id_good', 'n_qty'],
    )
    det_form_set = det_form_set_class(queryset=StkActDet.objects.filter(id_act_id=pk),)
    return render(request, 'act/stk_act_detail.html', {'form': form, 'det_form_set': det_form_set})


class MyModelForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(args, kwargs)
        for boundfield in self:
            boundfield.css_classes("form-control")


class StkActForm(ModelForm):
    class Meta:
        model = StkAct
        fields = ['s_state', 'n_direction']
        widgets = {'n_direction': HiddenInput()}


class StkActDetForm(MyModelForm):
    class Meta:
        model = StkActDet
        fields = ['id_good', 'n_qty']



