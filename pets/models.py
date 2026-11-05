from django.conf import settings
from django.db import models


class Pet(models.Model):
    class Species(models.TextChoices):
        DOG = "dog", "สุนัข"
        CAT = "cat", "แมว"
        OTHER = "other", "อื่น ๆ"

    class Gender(models.TextChoices):
        MALE = "male", "ตัวผู้"
        FEMALE = "female", "ตัวเมีย"
        UNKNOWN = "unknown", "ไม่ทราบ"

    class Status(models.TextChoices):
        AVAILABLE = "available", "รอบ้าน"
        PENDING = "pending", "กำลังพิจารณา"
        ADOPTED = "adopted", "ได้บ้านแล้ว"

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pets"
    )
    name = models.CharField("ชื่อ", max_length=100)
    species = models.CharField("ชนิด", max_length=10, choices=Species.choices)
    breed = models.CharField("สายพันธุ์", max_length=100, blank=True)
    gender = models.CharField(
        "เพศ", max_length=10, choices=Gender.choices, default=Gender.UNKNOWN
    )
    age_months = models.PositiveIntegerField("อายุ (เดือน)", help_text="1 ปี = 12 เดือน")
    province = models.CharField("จังหวัด/พื้นที่", max_length=100)
    description = models.TextField("เรื่องราวและนิสัย")
    photo = models.ImageField("รูปภาพ", upload_to="pets/%Y/%m/")
    is_vaccinated = models.BooleanField("ฉีดวัคซีนแล้ว", default=False)
    is_neutered = models.BooleanField("ทำหมันแล้ว", default=False)
    status = models.CharField(
        "สถานะ", max_length=10, choices=Status.choices, default=Status.AVAILABLE
    )
    is_published = models.BooleanField("แสดงประกาศ", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

    @property
    def age_display(self):
        years, months = divmod(self.age_months, 12)
        if years and months:
            return f"{years} ปี {months} เดือน"
        if years:
            return f"{years} ปี"
        return f"{months} เดือน"