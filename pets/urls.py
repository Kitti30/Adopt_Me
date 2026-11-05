from django.urls import path

from . import views

app_name = "pets"
urlpatterns = [
    path("", views.pet_list, name="list"),
    path("new/", views.create, name="create"),
    path("<int:pk>/", views.pet_detail, name="detail"),
]