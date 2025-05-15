# admin.py
from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin
from .models import Product, Screen ,DailyChecklistItem,MonthlyChecklistItem,WeeklyChecklistItem,StartUpCheckSheet,RejectionSheet,Defects,MachineLocation,SolderingBitRecord,PChartData,ControlChartReading,ControlChartStatistics,QSF,ProcessMachineMapping




# Register other models
# admin.site.register(Product)
admin.site.register(ProcessMachineMapping)
# admin.site.register(Screen)
admin.site.register(QSF)
admin.site.register(DailyChecklistItem)
admin.site.register(WeeklyChecklistItem)
admin.site.register(MonthlyChecklistItem)
# admin.site.register(StartUpCheckSheet)
admin.site.register(RejectionSheet)
# admin.site.register(Defects)

# admin.site.register(SolderingBitRecord)
@admin.register(MachineLocation)
class MachineLocationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'min_skill_required')
    search_fields = ('location_name',)


@admin.register(StartUpCheckSheet)
class StartUpCheckSheetAdmin(admin.ModelAdmin):
    list_display = ('process_operation', 'revision_no', 'effective_date', 'month')
    list_filter = ('process_operation', 'month')

admin.site.register(PChartData)


admin.site.register(ControlChartReading)

admin.site.register(ControlChartStatistics)