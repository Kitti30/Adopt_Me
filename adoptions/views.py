from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from pets.models import Pet

from .forms import AdoptionForm
from .models import AdoptionRequest


@login_required
def apply(request, pet_pk):
    pet = get_object_or_404(Pet, pk=pet_pk, is_published=True)

    if pet.posted_by == request.user:
        messages.error(request, "ไม่สามารถยื่นคำขอรับเลี้ยงสัตว์ที่คุณลงประกาศเองได้")
        return redirect("pets:detail", pk=pet.pk)
    if pet.status != Pet.Status.AVAILABLE:
        messages.error(request, "น้องตัวนี้ไม่เปิดรับคำขอแล้ว")
        return redirect("pets:detail", pk=pet.pk)
    if AdoptionRequest.objects.filter(
        pet=pet, applicant=request.user, status__in=AdoptionRequest.ACTIVE_STATUSES
    ).exists():
        messages.info(request, "คุณยื่นคำขอสำหรับน้องตัวนี้ไว้แล้ว ดูสถานะได้ที่นี่")
        return redirect("adoptions:mine")

    form = AdoptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        req = form.save(commit=False)
        req.pet = pet
        req.applicant = request.user
        req.save()
        messages.success(request, f"ส่งคำขอรับเลี้ยง {pet.name} เรียบร้อยแล้ว รอทีมงานตรวจสอบนะ 💌")
        return redirect("adoptions:mine")
    return render(request, "adoptions/apply.html", {"form": form, "pet": pet})


@login_required
def my_requests(request):
    requests_qs = request.user.adoption_requests.select_related("pet")
    return render(request, "adoptions/my_requests.html", {"requests": requests_qs})


@login_required
@require_POST
def cancel(request, pk):
    req = get_object_or_404(AdoptionRequest, pk=pk, applicant=request.user)
    if req.status in (AdoptionRequest.Status.PENDING, AdoptionRequest.Status.VERIFIED):
        req.status = AdoptionRequest.Status.CANCELLED
        req.save()
        messages.success(request, "ยกเลิกคำขอเรียบร้อยแล้ว")
    return redirect("adoptions:mine")