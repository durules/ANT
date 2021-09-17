from django.shortcuts import render

# Create your views here.

from dal import autocomplete

from goods.models import GdsGood


class GdsGoodAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return GdsGood.objects.none()

        qs = GdsGood.objects.all()

        if self.q:
            qs = qs.filter(sCaption__icontains=self.q)

        return qs


