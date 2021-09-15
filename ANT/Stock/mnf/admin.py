from django.contrib import admin

from mnf.item.itemModels import MnfItemDet, MnfItem
from mnf.shift.shiftResultModels import MnfShiftResult


class MnfItemDetInline(admin.TabularInline):
    model = MnfItemDet
    autocomplete_fields = ['id_good']


@admin.register(MnfItem)
class MnfItemAdmin(admin.ModelAdmin):
    inlines = [MnfItemDetInline]


@admin.register(MnfShiftResult)
class MnfItemAdmin(admin.ModelAdmin):
    pass
