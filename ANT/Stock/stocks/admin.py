from django.contrib import admin

from stocks.models import StkRemains, StkAct, StkActDet


class StkRemainsAdmin(admin.ModelAdmin):
    pass


admin.site.register(StkRemains, StkRemainsAdmin)
admin.site.register(StkAct)
admin.site.register(StkActDet)
