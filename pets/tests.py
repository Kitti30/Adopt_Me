from django.urls import reverse

from core.testing import MediaTestCase, make_image, make_pet, make_user

from .models import Pet


class PetCreateTests(MediaTestCase):
    def setUp(self):
        self.user = make_user()

    def test_create_requires_login(self):
        url = reverse("pets:create")
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={url}")

    def test_create_pet_success(self):
        self.client.force_login(self.user)
        data = {
            "name": "มะลิ", "species": "cat", "breed": "วิเชียรมาศ", "gender": "female",
            "age_months": 8, "province": "กรุงเทพฯ", "description": "เชื่อง ขี้อ้อน",
            "photo": make_image(), "is_vaccinated": "on",
        }
        resp = self.client.post(reverse("pets:create"), data)
        pet = Pet.objects.get()
        self.assertRedirects(resp, reverse("pets:detail", args=[pet.pk]))
        self.assertEqual(pet.posted_by, self.user)
        self.assertTrue(pet.is_vaccinated)
        self.assertFalse(pet.is_neutered)
        self.assertEqual(pet.status, Pet.Status.AVAILABLE)

    def test_create_without_photo_fails(self):
        self.client.force_login(self.user)
        data = {
            "name": "มะลิ", "species": "cat", "gender": "female",
            "age_months": 8, "province": "กรุงเทพฯ", "description": "เชื่อง",
        }
        resp = self.client.post(reverse("pets:create"), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Pet.objects.count(), 0)


class PetListTests(MediaTestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.url = reverse("pets:list")

    def test_list_hides_unpublished(self):
        make_pet(self.owner, name="มะลิ")
        make_pet(self.owner, name="ถั่วดำ", is_published=False)
        resp = self.client.get(self.url)
        self.assertContains(resp, "มะลิ")
        self.assertNotContains(resp, "ถั่วดำ")

    def test_filter_by_species(self):
        make_pet(self.owner, name="มะลิ", species="cat")
        make_pet(self.owner, name="ทองหล่อ", species="dog")
        resp = self.client.get(self.url, {"species": "dog"})
        self.assertContains(resp, "ทองหล่อ")
        self.assertNotContains(resp, "มะลิ")

    def test_filter_by_age_range(self):
        make_pet(self.owner, name="มะลิ", age_months=6)
        make_pet(self.owner, name="ทองหล่อ", age_months=24)
        make_pet(self.owner, name="ถั่วดำ", age_months=60)

        baby = self.client.get(self.url, {"age": "baby"})
        self.assertContains(baby, "มะลิ")
        self.assertNotContains(baby, "ทองหล่อ")
        self.assertNotContains(baby, "ถั่วดำ")

        young = self.client.get(self.url, {"age": "young"})
        self.assertContains(young, "ทองหล่อ")
        self.assertNotContains(young, "มะลิ")

        adult = self.client.get(self.url, {"age": "adult"})
        self.assertContains(adult, "ถั่วดำ")
        self.assertNotContains(adult, "ทองหล่อ")

    def test_filter_by_area(self):
        make_pet(self.owner, name="มะลิ", province="กรุงเทพฯ")
        make_pet(self.owner, name="ทองหล่อ", province="เชียงใหม่")
        resp = self.client.get(self.url, {"area": "เชียงใหม่"})
        self.assertContains(resp, "ทองหล่อ")
        self.assertNotContains(resp, "มะลิ")

    def test_search_by_name_or_breed(self):
        make_pet(self.owner, name="ทองหล่อ", breed="ชิบะ")
        make_pet(self.owner, name="มะลิ")
        resp = self.client.get(self.url, {"q": "ชิบะ"})
        self.assertContains(resp, "ทองหล่อ")
        self.assertNotContains(resp, "มะลิ")

    def test_pagination_shows_nine_per_page(self):
        for i in range(10):
            make_pet(self.owner, name=f"น้อง{i}")
        page1 = self.client.get(self.url)
        self.assertEqual(len(page1.context["page_obj"]), 9)
        page2 = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(page2.context["page_obj"]), 1)


class PetDetailTests(MediaTestCase):
    def test_unpublished_pet_returns_404(self):
        pet = make_pet(make_user(), is_published=False)
        resp = self.client.get(reverse("pets:detail", args=[pet.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_published_pet_shows_profile(self):
        pet = make_pet(make_user(), name="มะลิ")
        resp = self.client.get(reverse("pets:detail", args=[pet.pk]))
        self.assertContains(resp, "มะลิ")


class AgeDisplayTests(MediaTestCase):
    def test_age_display(self):
        self.assertEqual(Pet(age_months=5).age_display, "5 เดือน")
        self.assertEqual(Pet(age_months=24).age_display, "2 ปี")
        self.assertEqual(Pet(age_months=18).age_display, "1 ปี 6 เดือน")