from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PetForm
from .models import Pet

AGE_CHOICES = [
    ("baby", "ลูกสัตว์ (ต่ำกว่า 1 ปี)"),
    ("young", "วัยรุ่น (1-3 ปี)"),
    ("adult", "โตเต็มวัย (มากกว่า 3 ปี)"),
]


def pet_list(request):
    pets = Pet.objects.filter(is_published=True)

    q = request.GET.get("q", "").strip()
    species = request.GET.get("species", "")
    age = request.GET.get("age", "")
    area = request.GET.get("area", "").strip()

    if q:
        pets = pets.filter(Q(name__icontains=q) | Q(breed__icontains=q))
    if species in Pet.Species.values:
        pets = pets.filter(species=species)
    if age == "baby":
        pets = pets.filter(age_months__lt=12)
    elif age == "young":
        pets = pets.filter(age_months__gte=12, age_months__lte=36)
    elif age == "adult":
        pets = pets.filter(age_months__gt=36)
    if area:
        pets = pets.filter(province__icontains=area)

    page_obj = Paginator(pets, 9).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "pets/pet_list.html", {
        "page_obj": page_obj,
        "querystring": params.urlencode(),
        "species_choices": Pet.Species.choices,
        "age_choices": AGE_CHOICES,
        "f": {"q": q, "species": species, "age": age, "area": area},
    })


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk, is_published=True)
    return render(request, "pets/pet_detail.html", {"pet": pet})


@login_required
def create(request):
    form = PetForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        pet = form.save(commit=False)
        pet.posted_by = request.user
        pet.save()
        messages.success(request, f"ลงทะเบียน {pet.name} เรียบร้อยแล้ว 🐾")
        return redirect("pets:detail", pk=pet.pk)
    return render(request, "pets/pet_form.html", {"form": form})