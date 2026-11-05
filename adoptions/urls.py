from django.urls import path

from . import views

app_name = "adoptions"
urlpatterns = [
    path("mine/", views.my_requests, name="mine"),
    path("apply/<int:pet_pk>/", views.apply, name="apply"),
    path("<int:pk>/cancel/", views.cancel, name="cancel"),
]