from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PetForm


@login_required
def create(request):
    form = PetForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        pet = form.save(commit=False)
        pet.posted_by = request.user
        pet.save()
        messages.success(request, f"ลงทะเบียน {pet.name} เรียบร้อยแล้ว 🐾")
        return redirect("core:home")
    return render(request, "pets/pet_form.html", {"form": form})