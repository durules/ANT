from django.urls import path

from intg import views
from trd import OrderReport
from trd.order import order_views

urlpatterns = [
    path('orders/', order_views.TrdOrderListView.as_view(), name='trd_orders'),
    path('orders/new/<id_trade_system>', order_views.insert, name='trd_order_new'),
    path('order/<pk>', order_views.trd_order_detail, name='trd_order-detail'),
    path('order_report/', OrderReport.build_report, name='trd_order_report'),
    path('run_order_integration/', views.run_order_integration, name='run_order_integration'),
]
