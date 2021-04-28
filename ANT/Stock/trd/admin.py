from django.contrib import admin

from trd.models import TrdTradeSystem, TrdDeliveryService
from trd.order.orderModels import TrdOrderState, TrdOrderStateLevel

# Заказ


class TrdOrderStateLevelInline(admin.TabularInline):
    model = TrdOrderStateLevel


class TrdOrderStateAdmin(admin.ModelAdmin):
    inlines = [TrdOrderStateLevelInline]


# Торговая система


class TrdTradeSystemAdmin(admin.ModelAdmin):
    pass


# Служба доставки


class TrdDeliveryServiceAdmin(admin.ModelAdmin):
    pass


admin.site.register(TrdOrderState, TrdOrderStateAdmin)
admin.site.register(TrdTradeSystem, TrdTradeSystemAdmin)
admin.site.register(TrdDeliveryService, TrdDeliveryServiceAdmin)
