import io
import os

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw

from accounts.models import Profile
from adoptions.models import AdoptionRequest
from pets.models import Pet

PASSWORD = "Demo12345!"

PETS = [
    ("มะลิ", "cat", "วิเชียรมาศ", "female", 6, "กรุงเทพฯ", "แมวน้อยขี้อ้อน ชอบนอนตักคน กินเก่ง", (255, 214, 153), (245, 245, 235), True, False),
    ("ทองหล่อ", "dog", "ไทยหลังอาน", "male", 24, "เชียงใหม่", "สุนัขร่าเริง เป็นมิตรกับเด็ก ชอบวิ่งเล่น", (186, 230, 253), (222, 160, 90), True, True),
    ("ถั่วดำ", "cat", "ไทย", "male", 60, "ขอนแก่น", "แมวสูงวัยใจเย็น เหมาะกับบ้านที่อยากได้เพื่อนเงียบ ๆ", (254, 205, 211), (60, 60, 70), True, True),
    ("ข้าวปั้น", "dog", "ผสม", "female", 3, "ภูเก็ต", "ลูกสุนัขกำลังซน ต้องการคนมีเวลาให้", (187, 247, 208), (235, 215, 180), False, False),
    ("โมจิ", "cat", "เปอร์เซีย", "female", 14, "นนทบุรี", "ขนฟู ต้องแปรงขนสม่ำเสมอ นิสัยสุภาพ", (233, 213, 255), (250, 240, 230), True, False),
    ("บราวนี่", "dog", "โกลเด้น", "male", 36, "กรุงเทพฯ", "สุนัขตัวใหญ่ใจดี ฉลาด เชื่อฟัง", (254, 240, 138), (210, 160, 80), True, True),
]


def make_png(bg, fur):
    img = Image.new("RGB", (480, 360), bg)
    d = ImageDraw.Draw(img)
    d.polygon([(170, 150), (190, 70), (240, 130)], fill=fur)
    d.polygon([(310, 150), (290, 70), (240, 130)], fill=fur)
    d.ellipse([160, 110, 320, 270], fill=fur)
    d.ellipse([205, 170, 225, 195], fill=(40, 40, 40))
    d.ellipse([255, 170, 275, 195], fill=(40, 40, 40))
    d.polygon([(232, 205), (248, 205), (240, 218)], fill=(240, 120, 140))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


class Command(BaseCommand):
    help = "สร้างบัญชีทดลองและข้อมูลสัตว์ตัวอย่าง (ข้ามถ้ามีข้อมูลสัตว์อยู่แล้ว)"

    def _user(self, username, phone, province, superuser=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "is_staff": superuser,
                "is_superuser": superuser,
            },
        )
        if created:
            user.set_password(PASSWORD)
            user.save()
        Profile.objects.get_or_create(user=user, defaults={"phone": phone, "province": province})
        return user

    def handle(self, *args, **options):
        if os.environ.get("SEED_DEMO", "1") == "0":
            self.stdout.write("seed_demo: ปิดไว้ (SEED_DEMO=0)")
            return
        if Pet.objects.exists():
            self.stdout.write("seed_demo: มีข้อมูลสัตว์อยู่แล้ว ข้ามการสร้างข้อมูลตัวอย่าง")
            return

        admin = self._user("admin", "0800000000", "กรุงเทพฯ", superuser=True)
        owner = self._user("owner1", "0811111111", "กรุงเทพฯ")
        applicant = self._user("somchai", "0822222222", "นนทบุรี")

        pets = []
        for name, species, breed, gender, age, province, desc, bg, fur, vacc, neut in PETS:
            pet = Pet(
                posted_by=owner, name=name, species=species, breed=breed, gender=gender,
                age_months=age, province=province, description=desc,
                is_vaccinated=vacc, is_neutered=neut,
            )
            pet.photo.save(f"{name}.png", ContentFile(make_png(bg, fur)), save=False)
            pet.save()
            pets.append(pet)

        base = dict(
            housing_type="house", ownership="own", landlord_allows_pets=False,
            household_members=2, all_agree=True, has_other_pets=False,
            experience="เคยเลี้ยงสัตว์มาหลายปี ดูแลเองตลอด พาไปหาหมอตามกำหนด",
            hours_alone=4, monthly_budget="mid",
            reason="อยากมีเพื่อนคู่ใจและพร้อมดูแลตลอดชีวิต", agree_terms=True,
        )
        AdoptionRequest.objects.create(
            pet=pets[0], applicant=applicant,
            **{**base, "ownership": "rent", "landlord_allows_pets": True,
               "hours_alone": 10, "monthly_budget": "low"},
        )
        pets[5].status = Pet.Status.ADOPTED
        pets[5].save(update_fields=["status"])
        AdoptionRequest.objects.create(
            pet=pets[5], applicant=applicant, status="approved",
            phone_verified=True, home_verified=True,
            staff_note="นัดรับน้องที่ศูนย์ วันเสาร์นี้ ขอบคุณที่ให้บ้านน้องนะคะ",
            reviewed_by=admin, reviewed_at=timezone.now(), **base,
        )

        self.stdout.write(self.style.SUCCESS(
            f"seed_demo: สร้างข้อมูลตัวอย่างแล้ว | admin / owner1 / somchai รหัสผ่าน {PASSWORD}"
        ))