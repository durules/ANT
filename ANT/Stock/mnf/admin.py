from django.contrib import admin

from mnf.item.itemModels import MnfItemDet, MnfItem
from mnf.material.materialModels import MnfMaterial
from mnf.shift.shiftResultModels import MnfShiftResult


class MnfItemDetInline(admin.TabularInline):
    model = MnfItemDet


@admin.register(MnfItem)
class MnfItemAdmin(admin.ModelAdmin):
    inlines = [MnfItemDetInline]


@admin.register(MnfMaterial)
class MnfMaterialAdmin(admin.ModelAdmin):
    fields = ['s_caption']


@admin.register(MnfShiftResult)
class MnfItemAdmin(admin.ModelAdmin):
    pass