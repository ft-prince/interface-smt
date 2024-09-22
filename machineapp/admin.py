from django.contrib import admin
from .models import  Machine

# Register your models here.


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_skills', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)