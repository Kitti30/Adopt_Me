from django.urls import reverse

from core.testing import MediaTestCase, make_pet, make_request, make_user
from pets.models import Pet

from .models import AdoptionRequest

S = AdoptionRequest.Status


class ReviewTests(MediaTestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.staff = make_user("staff", staff=True)
        self.applicant = make_user("applicant")
        self.pet = make_pet(self.owner, name="มะลิ")
        self.req = make_request(self.pet, self.applicant)
        self.pk = self.req.pk

    def reload(self):
        self.req.refresh_from_db()
        self.pet.refresh_from_db()

    # --- สิทธิ์การเข้าถึง ---
    def test_anonymous_redirected_to_login(self):
        url = reverse("adoptions:review_list")
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={url}")

    def test_non_staff_forbidden(self):
        self.client.force_login(self.applicant)
        self.assertEqual(self.client.get(reverse("adoptions:review_list")).status_code, 403)
        self.assertEqual(
            self.client.get(reverse("adoptions:review_detail", args=[self.pk])).status_code, 403
        )
        self.assertEqual(
            self.client.post(reverse("adoptions:approve", args=[self.pk])).status_code, 403
        )

    # --- หน้าดูรายการ/รายละเอียด ---
    def test_staff_sees_open_requests(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("adoptions:review_list"))
        self.assertContains(resp, "มะลิ")

    def test_staff_can_view_detail_even_without_profile(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("adoptions:review_detail", args=[self.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "applicant")

    # --- ตรวจสอบผู้ขอ ---
    def test_verify_needs_both_checkboxes(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("adoptions:verify", args=[self.pk]), {"phone_verified": "on"})
        self.reload()
        self.assertEqual(self.req.status, S.PENDING)
        self.assertFalse(self.req.phone_verified)

    def test_verify_success(self):
        self.client.force_login(self.staff)
        self.client.post(
            reverse("adoptions:verify", args=[self.pk]),
            {"phone_verified": "on", "home_verified": "on"},
        )
        self.reload()
        self.assertEqual(self.req.status, S.VERIFIED)
        self.assertEqual(self.req.reviewed_by, self.staff)
        self.assertIsNotNone(self.req.reviewed_at)

    # --- อนุมัติ ---
    def test_approve_requires_verification_first(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("adoptions:approve", args=[self.pk]))
        self.reload()
        self.assertEqual(self.req.status, S.PENDING)
        self.assertEqual(self.pet.status, Pet.Status.AVAILABLE)

    def test_approve_flow_marks_pet_adopted_and_rejects_others(self):
        other = make_user("other")
        other_req = make_request(self.pet, other)
        self.client.force_login(self.staff)
        self.client.post(
            reverse("adoptions:verify", args=[self.pk]),
            {"phone_verified": "on", "home_verified": "on"},
        )
        self.client.post(reverse("adoptions:approve", args=[self.pk]), {"note": "นัดรับวันเสาร์"})
        self.reload()
        other_req.refresh_from_db()
        self.assertEqual(self.req.status, S.APPROVED)
        self.assertEqual(self.req.staff_note, "นัดรับวันเสาร์")
        self.assertEqual(self.pet.status, Pet.Status.ADOPTED)
        self.assertEqual(other_req.status, S.REJECTED)
        self.assertTrue(other_req.staff_note)

    def test_approve_blocked_when_pet_not_available(self):
        self.req.status = S.VERIFIED
        self.req.save()
        self.pet.status = Pet.Status.ADOPTED
        self.pet.save()
        self.client.force_login(self.staff)
        self.client.post(reverse("adoptions:approve", args=[self.pk]))
        self.reload()
        self.assertEqual(self.req.status, S.VERIFIED)

    # --- ไม่อนุมัติ ---
    def test_reject_requires_reason(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("adoptions:reject", args=[self.pk]), {"note": ""})
        self.reload()
        self.assertEqual(self.req.status, S.PENDING)

    def test_reject_with_reason(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("adoptions:reject", args=[self.pk]), {"note": "ที่พักไม่เหมาะสม"})
        self.reload()
        self.assertEqual(self.req.status, S.REJECTED)
        self.assertEqual(self.req.staff_note, "ที่พักไม่เหมาะสม")