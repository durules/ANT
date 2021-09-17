from dal import autocomplete
from django.forms import inlineformset_factory, forms, ModelForm, ModelChoiceField
from django.urls import reverse_lazy
from django.views import generic

from goods.models import GdsGood
from stocks.models import StkAct, StkActDet


class TForm(ModelForm):
    class Meta:
        model = StkActDet
        fields = ('id_good', 'n_qty')
        widgets = {
            'id_good': autocomplete.ModelSelect2(
                'good-autocomplete'
            )
        }


class StkActForm(ModelForm):
    id_good = ModelChoiceField(
        queryset=GdsGood.objects.all(),
        widget=autocomplete.ModelSelect2(url='good-autocomplete')
    )

    class Meta:
        model = StkAct
        fields = ['s_state', 'n_direction', 's_desc', 'id_good']


class UpdateView(generic.UpdateView):
    model = StkAct
    form_class = StkActForm
    template_name = 'stocks/act/stk_act_detail.html'
    success_url = reverse_lazy('stk_act-detail')
    formset_class = inlineformset_factory(
        StkAct,
        StkActDet,
        form=TForm,
        extra=1,
        fk_name='id_act',
        fields=('id_good', 'n_qty')
    )

    def get_object(self):
        return StkAct.objects.first()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        result = super().form_valid(form)
        self.formset.save()
        return result

    @property
    def formset(self):
        if '_formset' not in self.__dict__:
            setattr(self, '_formset', self.formset_class(
                self.request.POST if self.request.method == 'POST' else None,
                instance=getattr(self, 'object', self.get_object()),
            ))
        return self._formset