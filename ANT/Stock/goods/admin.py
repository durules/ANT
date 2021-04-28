from django.contrib import admin

from goods.models import GdsGood, GdsGoodRemainsLevel


class GdsGoodRemainsLevelInline(admin.TabularInline):
    model = GdsGoodRemainsLevel


class GdsGoodAdmin(admin.ModelAdmin):
    inlines = [GdsGoodRemainsLevelInline]


admin.site.register(GdsGood, GdsGoodAdmin)
