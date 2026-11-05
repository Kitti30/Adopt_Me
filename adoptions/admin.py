from django.contrib import admin

from .models import AdoptionRequest


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("applicant", "pet", "status", "reviewed_by", "created_at")
    list_filter = ("status",)
    search_fields = ("applicant__username", "pet__name")
    list_select_related = ("applicant", "pet", "reviewed_by")

    # ดูอย่างเดียว: การอนุมัติต้องทำผ่านหน้า "ตรวจคำขอ" เพื่อให้สถานะน้องกับคำขอตรงกัน
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False