from django.urls import path, include
from rest_framework import routers

from theatre.views import TheatreHallViewSet


router = routers.DefaultRouter()
router.register("theatre_halls", TheatreHallViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "theatre"
