from django.contrib import admin

# Register your models here.
from cor.models import CorColor


@admin.register(CorColor)
class CorColorAdmin(admin.ModelAdmin):
    pass
