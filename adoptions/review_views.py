from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from pets.models import Pet

from .models import AdoptionRequest

S = AdoptionRequest.Status
OPEN_STATUSES = [S.PENDING, S.VERIFIED]
TABS = [("open", "รอดำเนินการ"), ("approved", "อนุมัติแล้ว"), ("rejected", "ไม่อนุมัติ")]


def staff_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def _stamp(req, user):
    req.reviewed_by = user
    req.reviewed_at = timezone.now()


@staff_required
def review_list(request):
    tab = request.GET.get("status", "open")
    if tab not in dict(TABS):
        tab = "open"
    qs = AdoptionRequest.objects.select_related("pet", "applicant")
    if tab == "open":
        qs = qs.filter(status__in=OPEN_STATUSES).order_by("created_at")
    else:
        qs = qs.filter(status=tab)
    return render(request, "adoptions/review_list.html", {"requests": qs, "tabs": TABS, "tab": tab})


@staff_required
def review_detail(request, pk):
    req = get_object_or_404(
        AdoptionRequest.objects.select_related("pet", "applicant"), pk=pk
    )
    return render(request, "adoptions/review_detail.html", {"req": req})


@staff_required
@require_POST
def verify(request, pk):
    req = get_object_or_404(AdoptionRequest, pk=pk)
    if req.status != S.PENDING:
        messages.error(request, "คำขอนี้ไม่ได้อยู่ในสถานะรอตรวจสอบ")
    elif not (request.POST.get("phone_verified") and request.POST.get("home_verified")):
        messages.error(request, "ต้องติ๊กยืนยันการตรวจสอบให้ครบทั้ง 2 ข้อ")
    else:
        req.phone_verified = True
        req.home_verified = True
        req.status = S.VERIFIED
        _stamp(req, request.user)
        req.save()
        messages.success(request, "บันทึกผลการตรวจสอบแล้ว พร้อมพิจารณาอนุมัติ ✅")
    return redirect("adoptions:review_detail", pk=pk)


@staff_required
@require_POST
def approve(request, pk):
    note = request.POST.get("note", "").strip()
    with transaction.atomic():
        req = get_object_or_404(AdoptionRequest.objects.select_for_update(), pk=pk)
        pet = Pet.objects.select_for_update().get(pk=req.pet_id)
        if req.status != S.VERIFIED:
            messages.error(request, "ต้องตรวจสอบผู้ขอให้เสร็จก่อนจึงจะอนุมัติได้")
        elif pet.status != Pet.Status.AVAILABLE:
            messages.error(request, "น้องตัวนี้ไม่อยู่ในสถานะรอบ้านแล้ว")
        else:
            req.status = S.APPROVED
            req.staff_note = note
            _stamp(req, request.user)
            req.save()
            pet.status = Pet.Status.ADOPTED
            pet.save(update_fields=["status"])
            AdoptionRequest.objects.filter(
                pet=pet, status__in=OPEN_STATUSES
            ).exclude(pk=req.pk).update(
                status=S.REJECTED,
                staff_note="น้องได้บ้านใหม่แล้ว ขอบคุณที่สนใจนะคะ",
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
            )
            messages.success(request, f"อนุมัติแล้ว 🎉 {pet.name} ได้บ้านใหม่")
    return redirect("adoptions:review_detail", pk=pk)


@staff_required
@require_POST
def reject(request, pk):
    note = request.POST.get("note", "").strip()
    req = get_object_or_404(AdoptionRequest, pk=pk)
    if req.status not in OPEN_STATUSES:
        messages.error(request, "คำขอนี้ดำเนินการเสร็จแล้ว")
    elif not note:
        messages.error(request, "กรุณาใส่เหตุผลที่ไม่อนุมัติ")
    else:
        req.status = S.REJECTED
        req.staff_note = note
        _stamp(req, request.user)
        req.save()
        messages.success(request, "บันทึกการไม่อนุมัติแล้ว")
    return redirect("adoptions:review_detail", pk=pk)