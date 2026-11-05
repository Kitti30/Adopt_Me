from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField("เบอร์โทร", max_length=20, blank=True)
    province = models.CharField("จังหวัด", max_length=100, blank=True)

    def __str__(self):
        return f"โปรไฟล์ของ {self.user.username}"