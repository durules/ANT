from django.forms import ModelForm, formset_factory, BaseModelFormSet, modelformset_factory
from django.shortcuts import render
from django.views import generic

from stocks.models import StkAct, StkActDet


class StkActListView(generic.ListView):
    model = StkAct
    template_name = 'act/stk_act_list.html'
    paginate_by = 100

    def get_queryset(self):
        return StkAct.objects.all().order_by("-d_create_date")


def stk_act_detail(request, pk):
    if request.method == 'POST':
        form = StkActForm(request.POST)
        if form.is_valid():
            return "Ok"
    else:
        form = StkActForm()

    DetFormSet = modelformset_factory(
        StkActDet,
        fields=['id_good', 'n_qty'],
    )
    det_form_set = DetFormSet(queryset=StkActDet.objects.filter(id_act_id=pk))
    return render(request, 'act/stk_act_detail.html', {'form': form, 'det_form_set': det_form_set})


class StkActForm(ModelForm):
    class Meta:
        model = StkAct
        fields = ['s_state']


