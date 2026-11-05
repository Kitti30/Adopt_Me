from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from pets.models import Pet


class AdoptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "รอตรวจสอบ"
        VERIFIED = "verified", "ตรวจสอบแล้ว รอพิจารณา"
        APPROVED = "approved", "อนุมัติ"
        REJECTED = "rejected", "ไม่อนุมัติ"
        CANCELLED = "cancelled", "ยกเลิก"

    class Housing(models.TextChoices):
        HOUSE = "house", "บ้านเดี่ยว / ทาวน์เฮาส์"
        CONDO = "condo", "คอนโด / อพาร์ตเมนต์"
        DORM = "dorm", "หอพัก"
        OTHER = "other", "อื่น ๆ"

    class Ownership(models.TextChoices):
        OWN = "own", "เป็นเจ้าของที่พัก"
        RENT = "rent", "เช่า / อาศัยอยู่กับผู้อื่น"

    class Budget(models.TextChoices):
        LOW = "low", "ต่ำกว่า 1,000 บาท/เดือน"
        MID = "mid", "1,000 - 3,000 บาท/เดือน"
        HIGH = "high", "มากกว่า 3,000 บาท/เดือน"

    ACTIVE_STATUSES = ["pending", "verified", "approved"]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="requests")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adoption_requests"
    )

    # แบบสอบถามความพร้อม
    housing_type = models.CharField("ประเภทที่พัก", max_length=10, choices=Housing.choices)
    ownership = models.CharField("สถานะที่พัก", max_length=10, choices=Ownership.choices)
    landlord_allows_pets = models.BooleanField("ที่พักอนุญาตให้เลี้ยงสัตว์ (กรณีเช่า)", default=False)
    household_members = models.PositiveSmallIntegerField(
        "จำนวนคนในบ้าน", validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    all_agree = models.BooleanField("ทุกคนในบ้านเห็นด้วยกับการรับเลี้ยง", default=False)
    has_other_pets = models.BooleanField("มีสัตว์เลี้ยงอื่นอยู่แล้ว", default=False)
    other_pets_detail = models.CharField("สัตว์เลี้ยงที่มีอยู่ (ถ้ามี)", max_length=200, blank=True)
    experience = models.TextField("ประสบการณ์การเลี้ยงสัตว์")
    hours_alone = models.PositiveSmallIntegerField(
        "ชั่วโมงที่น้องต้องอยู่คนเดียวต่อวัน", validators=[MaxValueValidator(24)]
    )
    monthly_budget = models.CharField("งบดูแลต่อเดือน", max_length=10, choices=Budget.choices)
    reason = models.TextField("เหตุผลที่อยากรับเลี้ยง")
    agree_terms = models.BooleanField("ยืนยันว่าจะดูแลตลอดชีวิต ไม่ทอดทิ้ง และพาไปฉีดวัคซีนตามกำหนด", default=False)

    status = models.CharField("สถานะ", max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["pet", "applicant"],
                condition=Q(status__in=["pending", "verified", "approved"]),
                name="unique_active_request",
            )
        ]

    def __str__(self):
        return f"{self.applicant.username} → {self.pet.name} ({self.get_status_display()})"