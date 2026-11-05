from django.shortcuts import render

from pets.models import Pet


def home(request):
    latest_pets = Pet.objects.filter(is_published=True)[:6]
    return render(request, "core/home.html", {"latest_pets": latest_pets})