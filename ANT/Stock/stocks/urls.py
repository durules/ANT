from django.urls import path

from stocks import views
from stocks.act import act_views

urlpatterns = [
    path('', views.index, name='index'),
    path('acts/', act_views.StkActListView.as_view(), name='stk_acts'),
    path('acts/new_in/', act_views.insert_in_act, name='stk_acts_new_in'),
    path('acts/new_out/', act_views.insert_out_act, name='stk_acts_new_out'),
    path('act/<pk>', act_views.stk_act_detail, name='stk_act-detail'),
    path('act/<pk>/edit/', act_views.stk_act_edit, name='stk_act_edit'),
]
