from django.contrib import admin
from .models import Profile  # Import the Profile model

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'my_skill')  # Fields to display in the list view
    search_fields = ('user__username', 'my_skill')  # Enable search by username and skill
    list_filter = ('my_skill',)  # Enable filtering by skill level
