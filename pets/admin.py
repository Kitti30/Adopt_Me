from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        "thumb", "name", "species", "province", "status",
        "is_published", "posted_by", "created_at",
    )
    list_display_links = ("thumb", "name")
    list_editable = ("status", "is_published")
    list_filter = ("species", "status", "is_published", "province")
    search_fields = ("name", "breed", "province", "posted_by__username")
    list_select_related = ("posted_by",)
    actions = ["publish", "unpublish", "mark_available"]

    @admin.display(description="รูป")
    def thumb(self, obj):
        if not obj.photo:
            return "-"
        return format_html(
            '<img src="{}" style="width:56px;height:56px;object-fit:cover;border-radius:12px">',
            obj.photo.url,
        )

    @admin.action(description="แสดงประกาศที่เลือก")
    def publish(self, request, queryset):
        n = queryset.update(is_published=True)
        self.message_user(request, f"แสดงประกาศ {n} รายการ", messages.SUCCESS)

    @admin.action(description="ซ่อนประกาศที่เลือก")
    def unpublish(self, request, queryset):
        n = queryset.update(is_published=False)
        self.message_user(request, f"ซ่อนประกาศ {n} รายการ", messages.SUCCESS)

    @admin.action(description="ตั้งสถานะเป็น 'รอบ้าน'")
    def mark_available(self, request, queryset):
        n = queryset.update(status=Pet.Status.AVAILABLE)
        self.message_user(request, f"เปลี่ยนสถานะ {n} รายการ", messages.SUCCESS)