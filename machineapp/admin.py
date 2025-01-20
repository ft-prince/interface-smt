from django.contrib import admin
from django.utils.html import format_html
from .models import Machine, MachineLoginTracker

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_skills', 'display_user_count', 'display_status')
    search_fields = ('name', 'users__username')
    list_filter = ('required_skills',)
    filter_horizontal = ('users',)
    ordering = ('name',)
    
    fieldsets = (
        ('Machine Information', {
            'fields': ('name', 'required_skills')
        }),
        ('User Access', {
            'fields': ('users',),
            'description': 'Assign users who are authorized to access this machine'
        }),
    )

    def display_user_count(self, obj):
        return format_html('<b>{}</b> users', obj.users.count())
    display_user_count.short_description = 'Authorized Users'

    def display_status(self, obj):
        if obj.users.exists():
            return format_html(
                '<span style="color: green;">✓ In Use</span>'
            )
        return format_html(
            '<span style="color: gray;">○ Available</span>'
        )
    display_status.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('users')

@admin.register(MachineLoginTracker)
class MachineLoginTrackerAdmin(admin.ModelAdmin):
    list_display = ('machine', 'browser_key', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'machine')
    search_fields = ('machine__name', 'browser_key')