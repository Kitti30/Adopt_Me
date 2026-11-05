from django.contrib import admin

from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "species", "province", "status", "is_published", "posted_by", "created_at")
    list_filter = ("species", "status", "is_published")
    search_fields = ("name", "breed", "province")