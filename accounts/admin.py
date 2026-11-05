from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count

from pets.models import Pet

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 1
    max_num = 1


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = (
        "username", "email", "phone", "province",
        "is_active", "is_staff", "pet_count", "request_count", "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "profile__phone", "profile__province")
    actions = ["deactivate_users", "activate_users"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("profile")
            .annotate(
                _pets=Count("pets", distinct=True),
                _reqs=Count("adoption_requests", distinct=True),
            )
        )

    @admin.display(description="เบอร์โทร")
    def phone(self, obj):
        return getattr(getattr(obj, "profile", None), "phone", "") or "-"

    @admin.display(description="จังหวัด")
    def province(self, obj):
        return getattr(getattr(obj, "profile", None), "province", "") or "-"

    @admin.display(description="ประกาศ", ordering="_pets")
    def pet_count(self, obj):
        return obj._pets

    @admin.display(description="คำขอ", ordering="_reqs")
    def request_count(self, obj):
        return obj._reqs

    @admin.action(description="ระงับบัญชีที่เลือก (และซ่อนประกาศของบัญชีนั้น)")
    def deactivate_users(self, request, queryset):
        ids = list(
            queryset.exclude(pk=request.user.pk)
            .exclude(is_superuser=True)
            .values_list("pk", flat=True)
        )
        User.objects.filter(pk__in=ids).update(is_active=False)
        Pet.objects.filter(posted_by_id__in=ids).update(is_published=False)
        self.message_user(request, f"ระงับบัญชี {len(ids)} รายการ", messages.SUCCESS)

    @admin.action(description="เปิดใช้งานบัญชีที่เลือก")
    def activate_users(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, f"เปิดใช้งาน {n} บัญชี (ประกาศที่ถูกซ่อนต้องเปิดแสดงเองที่หน้า Pets)", messages.SUCCESS)