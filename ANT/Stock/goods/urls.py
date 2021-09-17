from dal import autocomplete
from django.conf.urls import url

from goods.models import GdsGood
from goods.views import GdsGoodAutocomplete

urlpatterns = [
    url(
        r'^gds-good-autocomplete/$',
        GdsGoodAutocomplete.as_view(),
        name='gds-good-autocomplete',
    ),
]
