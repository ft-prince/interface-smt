from django.contrib import admin
from django.utils.html import format_html
from .models import Machine, MachineLoginTracker

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'required_skills', 'display_user_count', 'display_checklists', 'display_status')
    search_fields = ('name', 'users__username')
    list_filter = ('required_skills', 'show_fixture_cleaning', 'show_rejection_sheets', 'show_soldering_bit', 
                  'show_maintenance_checklist', 'show_reading_list', 'show_pchart', 'show_startup_checklist',
                  'show_tip_voltage_resistance', 'show_pcb_panel_inspection', 'show_rework_analysis',
                  'show_solder_paste_control')
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
        ('Checklist Configuration', {
            'fields': (
                'show_fixture_cleaning', 'show_rejection_sheets', 'show_soldering_bit',
                'show_maintenance_checklist', 'show_reading_list', 'show_pchart', 'show_startup_checklist',
                'show_tip_voltage_resistance', 'show_pcb_panel_inspection', 'show_rework_analysis',
                'show_solder_paste_control'
            ),
            'description': 'Configure which checklists are visible to operators using this machine'
        }),
    )
    
    def display_user_count(self, obj):
        return format_html('<b>{}</b> users', obj.users.count())
    display_user_count.short_description = 'Authorized Users'
    
    def display_checklists(self, obj):
        enabled_count = sum([
            obj.show_fixture_cleaning,
            obj.show_rejection_sheets,
            obj.show_soldering_bit,
            obj.show_maintenance_checklist,
            obj.show_reading_list,
            obj.show_pchart,
            obj.show_startup_checklist,
            obj.show_tip_voltage_resistance,
            obj.show_pcb_panel_inspection,
            obj.show_rework_analysis,
            obj.show_solder_paste_control
        ])
        total_count = 11  # Updated total number of checklist types
        
        if enabled_count == total_count:
            return format_html('<span style="color: green;">{}/{} enabled</span>', enabled_count, total_count)
        elif enabled_count == 0:
            return format_html('<span style="color: red;">{}/{} enabled</span>', enabled_count, total_count)
        else:
            return format_html('<span style="color: orange;">{}/{} enabled</span>', enabled_count, total_count)
    display_checklists.short_description = 'Checklists'
    
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