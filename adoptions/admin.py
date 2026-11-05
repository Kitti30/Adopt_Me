from django.contrib import admin

from .models import AdoptionRequest


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("applicant", "pet", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("applicant__username", "pet__name")