from django.contrib import admin

from goods.models import GdsGood

class GdsGoodAdmin(admin.ModelAdmin):
    pass

admin.site.register(GdsGood, GdsGoodAdmin)
