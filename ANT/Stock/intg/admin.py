from django.contrib import admin
from django.shortcuts import redirect

from intg.cfg.cfgModels import IntgCircuit, IntgCircuitRunTimeData
from intg.cfg.mapping.mappingModels import GoodMapping, GoodMappingDet, DeliverySystemMapping, GoodMappingOption, \
    GoodMappingOptionDet
from django.utils.safestring import mark_safe
from django.urls import reverse


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''


class GoodMappingOptionDetInline(admin.TabularInline):
    model = GoodMappingOptionDet
    autocomplete_fields = ['id_good']


@admin.register(GoodMappingOption)
class GoodMappingOptionAdmin(admin.ModelAdmin):
    inlines = [GoodMappingOptionDetInline]

    def response_post_save_change(self, request, obj):
        id_good_mapping = GoodMappingOption.objects.get(pk=obj.pk).id_good_mapping
        return redirect("/admin/intg/goodmapping/%s/change/" % (id_good_mapping.id))


class GoodMappingOptionInline(EditLinkToInlineObject, admin.TabularInline):
    model = GoodMappingOption
    readonly_fields = ['edit_link']


class GoodMappingDetInline(admin.TabularInline):
    model = GoodMappingDet
    autocomplete_fields = ['id_good']


@admin.register(GoodMapping)
class GoodMappingAdmin(admin.ModelAdmin):
    inlines = [GoodMappingDetInline, GoodMappingOptionInline]
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






