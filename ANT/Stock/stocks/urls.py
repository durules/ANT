from django.urls import path

from stocks import views
from stocks.act import act_views

urlpatterns = [
    path('', views.index, name='index'),
    path('acts/', act_views.StkActListView.as_view(), name='stk_acts'),
    path('act/<pk>', act_views.stk_act_detail, name='stk_acts-detail'),
]
