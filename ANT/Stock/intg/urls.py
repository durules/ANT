from django.urls import path

from intg import views

urlpatterns = [
    path('run_order_integration/', views.run_order_integration, name='run_order_integration'),
    path('run_order_integration/<pk>', views.run_order_integration_by_id, name='run_order_integration_by_id'),
]
