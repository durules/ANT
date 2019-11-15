from django.urls import path

from mnf.shift import shiftResultViews
from stocks import views
from stocks.act import act_views

urlpatterns = [
    path('', views.index, name='index'),
    path('shift_result/', shiftResultViews.MnfShiftResultListView.as_view(), name='mnf_shift_results'),
    path('shift_result/new/', shiftResultViews.insert, name='mnf_shift_results_new'),
    path('shift_result/<pk>', shiftResultViews.mnf_shift_result_detail, name='mnf_shift_result-detail'),
    path('shift_result/<pk>/edit/', shiftResultViews.mnf_shift_result_edit, name='mnf_shift_result_edit'),
]
