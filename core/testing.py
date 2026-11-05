import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from adoptions.models import AdoptionRequest
from pets.models import Pet

PASSWORD = "Sup3rSecret!pw"


def make_image(name="test.png"):
    buf = BytesIO()
    Image.new("RGB", (4, 4), "orange").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def make_user(username="user1", staff=False):
    return User.objects.create_user(username=username, password=PASSWORD, is_staff=staff)


def make_pet(owner, **overrides):
    data = {
        "posted_by": owner,
        "name": "มะลิ",
        "species": "cat",
        "gender": "female",
        "age_months": 6,
        "province": "กรุงเทพฯ",
        "description": "เชื่อง ขี้อ้อน",
        "photo": make_image(),
    }
    data.update(overrides)
    return Pet.objects.create(**data)


def make_request(pet, applicant, **overrides):
    data = {
        "pet": pet,
        "applicant": applicant,
        "housing_type": "house",
        "ownership": "own",
        "household_members": 2,
        "all_agree": True,
        "experience": "เคยเลี้ยงแมวมาหลายปี ดูแลเองตลอด",
        "hours_alone": 4,
        "monthly_budget": "mid",
        "reason": "อยากมีเพื่อนคู่ใจ",
        "agree_terms": True,
    }
    data.update(overrides)
    return AdoptionRequest.objects.create(**data)


class MediaTestCase(TestCase):
    """เก็บรูปที่อัปโหลดตอนเทสต์ไว้ในโฟลเดอร์ชั่วคราว ไม่ปนกับ media จริง"""

    @classmethod
    def setUpClass(cls):
        cls._tmp_media = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._tmp_media)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._tmp_media, ignore_errors=True)