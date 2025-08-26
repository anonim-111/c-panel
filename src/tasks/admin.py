from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "description", "assigned_to", "created_by", "status", "created_at"]
    list_display_links = ["id", "title"]