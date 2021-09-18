from django.urls import path

from intg.ebay import restApi

urlpatterns = [
    path('ebay/delete_account', restApi.delete_account),
]
