from django.urls import path
from django.views.generic import RedirectView

from mnf import views
from mnf.shift import shiftResultViews

urlpatterns = [
    path('', views.index, name='index'),
    path('shift_result/', shiftResultViews.MnfShiftResultListView.as_view(), name='mnf_shift_results'),
    path('shift_result/new/', shiftResultViews.insert, name='mnf_shift_results_new'),
    path('shift_result/<pk>', shiftResultViews.mnf_shift_result_detail, name='mnf_shift_result-detail'),
    path('shift_result/<pk>/edit/', shiftResultViews.mnf_shift_result_edit, name='mnf_shift_result_edit'),
]
