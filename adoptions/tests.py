from django.urls import reverse

from core.testing import MediaTestCase, make_pet, make_request, make_user
from pets.models import Pet

from .models import AdoptionRequest

FORM = {
    "housing_type": "house",
    "ownership": "own",
    "household_members": 2,
    "all_agree": "on",
    "other_pets_detail": "",
    "experience": "เคยเลี้ยงแมวมาหลายปี ดูแลเองตลอด",
    "hours_alone": 4,
    "monthly_budget": "mid",
    "reason": "อยากมีเพื่อนคู่ใจ",
    "agree_terms": "on",
}


class ApplyTests(MediaTestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.applicant = make_user("applicant")
        self.pet = make_pet(self.owner)
        self.url = reverse("adoptions:apply", args=[self.pet.pk])

    def test_apply_requires_login(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={self.url}")

    def test_apply_success(self):
        self.client.force_login(self.applicant)
        resp = self.client.post(self.url, FORM)
        self.assertRedirects(resp, reverse("adoptions:mine"))
        req = AdoptionRequest.objects.get()
        self.assertEqual(req.status, AdoptionRequest.Status.PENDING)
        self.assertEqual(req.pet, self.pet)
        self.assertEqual(req.applicant, self.applicant)

    def test_owner_cannot_apply_for_own_pet(self):
        self.client.force_login(self.owner)
        resp = self.client.post(self.url, FORM)
        self.assertRedirects(resp, reverse("pets:detail", args=[self.pet.pk]))
        self.assertEqual(AdoptionRequest.objects.count(), 0)

    def test_cannot_apply_when_pet_not_available(self):
        self.pet.status = Pet.Status.ADOPTED
        self.pet.save()
        self.client.force_login(self.applicant)
        resp = self.client.post(self.url, FORM)
        self.assertRedirects(resp, reverse("pets:detail", args=[self.pet.pk]))
        self.assertEqual(AdoptionRequest.objects.count(), 0)

    def test_duplicate_active_request_blocked(self):
        self.client.force_login(self.applicant)
        self.client.post(self.url, FORM)
        self.client.post(self.url, FORM)
        self.assertEqual(AdoptionRequest.objects.count(), 1)

    def test_renter_without_landlord_permission_rejected(self):
        self.client.force_login(self.applicant)
        resp = self.client.post(self.url, {**FORM, "ownership": "rent"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ต้องได้รับอนุญาตจากเจ้าของที่พัก")
        self.assertEqual(AdoptionRequest.objects.count(), 0)

    def test_renter_with_landlord_permission_accepted(self):
        self.client.force_login(self.applicant)
        data = {**FORM, "ownership": "rent", "landlord_allows_pets": "on"}
        self.client.post(self.url, data)
        self.assertEqual(AdoptionRequest.objects.count(), 1)

    def test_must_accept_terms(self):
        self.client.force_login(self.applicant)
        data = {k: v for k, v in FORM.items() if k != "agree_terms"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(AdoptionRequest.objects.count(), 0)


class CancelTests(MediaTestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.applicant = make_user("applicant")
        self.pet = make_pet(self.owner)
        self.req = make_request(self.pet, self.applicant)

    def test_applicant_can_cancel_own_request(self):
        self.client.force_login(self.applicant)
        resp = self.client.post(reverse("adoptions:cancel", args=[self.req.pk]))
        self.assertRedirects(resp, reverse("adoptions:mine"))
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, AdoptionRequest.Status.CANCELLED)

    def test_cannot_cancel_someone_elses_request(self):
        self.client.force_login(self.owner)
        resp = self.client.post(reverse("adoptions:cancel", args=[self.req.pk]))
        self.assertEqual(resp.status_code, 404)
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, AdoptionRequest.Status.PENDING)

    def test_can_reapply_after_cancel(self):
        self.client.force_login(self.applicant)
        self.client.post(reverse("adoptions:cancel", args=[self.req.pk]))
        self.client.post(reverse("adoptions:apply", args=[self.pet.pk]), FORM)
        self.assertEqual(AdoptionRequest.objects.count(), 2)
        active = AdoptionRequest.objects.filter(status=AdoptionRequest.Status.PENDING)
        self.assertEqual(active.count(), 1)


class RiskFlagTests(MediaTestCase):
    def test_risk_flags(self):
        owner, applicant = make_user("owner"), make_user("applicant")
        pet = make_pet(owner)
        risky = make_request(
            pet, applicant, hours_alone=10, monthly_budget="low",
            ownership="rent", experience="สั้น",
        )
        self.assertEqual(len(risky.risk_flags), 4)

    def test_no_flags_for_good_applicant(self):
        owner, applicant = make_user("owner"), make_user("applicant")
        req = make_request(make_pet(owner), applicant)
        self.assertEqual(req.risk_flags, [])