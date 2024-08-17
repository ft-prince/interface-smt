# admin.py
from django.contrib import admin
#from django.contrib.auth.admin import UserAdmin
from .models import Product, Screen ,DailyChecklistItem,MonthlyChecklistItem,WeeklyChecklistItem




# Register other models
admin.site.register(Product)
admin.site.register(Screen)
admin.site.register(MonthlyChecklistItem)
admin.site.register(WeeklyChecklistItem)
admin.site.register(DailyChecklistItem)

