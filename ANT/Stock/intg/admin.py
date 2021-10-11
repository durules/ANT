from django.contrib import admin

from intg.cfg.cfgModels import IntgCircuit, IntgCircuitRunTimeData
from intg.cfg.mapping.mappingModels import GoodMapping, GoodMappingDet, DeliverySystemMapping


class GoodMappingDetInline(admin.TabularInline):
    model = GoodMappingDet
    autocomplete_fields = ['id_good']


@admin.register(GoodMapping)
class GoodMappingAdmin(admin.ModelAdmin):
    inlines = [GoodMappingDetInline]
    list_display = ('s_external_id', 'id_circuit')
    list_filter = ['id_circuit']
    search_fields = ['s_external_id']


@admin.register(DeliverySystemMapping)
class DeliverySystemMappingAdmin(admin.ModelAdmin):
    list_display = ['s_external_id', 'id_circuit', 'id_delivery_service']
    list_filter = ['id_circuit']
    search_fields = ['s_external_id', 'id_delivery_service__s_caption']


class IntgCircuitRunTimeDataInline(admin.TabularInline):
    model = IntgCircuitRunTimeData
    max_num = 1


@admin.register(IntgCircuit)
class IntgCircuitAdmin(admin.ModelAdmin):
    inlines = [IntgCircuitRunTimeDataInline]



