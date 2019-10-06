from django.contrib import admin

from stocks.models import StkRemains


class StkRemainsAdmin(admin.ModelAdmin):
    pass

admin.site.register(StkRemains, StkRemainsAdmin)
