from django.views import generic

from stocks.models import StkAct


class StkActListView(generic.ListView):
    model = StkAct
    template_name = 'act/stk_act_list.html'

    def get_queryset(self):
        return StkAct.objects.all().order_by("-d_create_date")
