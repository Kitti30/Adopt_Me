from django.urls import path

from . import review_views, views

app_name = "adoptions"
urlpatterns = [
    path("mine/", views.my_requests, name="mine"),
    path("apply/<int:pet_pk>/", views.apply, name="apply"),
    path("<int:pk>/cancel/", views.cancel, name="cancel"),
    path("review/", review_views.review_list, name="review_list"),
    path("review/<int:pk>/", review_views.review_detail, name="review_detail"),
    path("review/<int:pk>/verify/", review_views.verify, name="verify"),
    path("review/<int:pk>/approve/", review_views.approve, name="approve"),
    path("review/<int:pk>/reject/", review_views.reject, name="reject"),
]