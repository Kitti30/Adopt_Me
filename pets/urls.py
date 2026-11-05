from django.urls import path

from . import views

app_name = "pets"
urlpatterns = [
    path("new/", views.create, name="create"),
]