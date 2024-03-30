from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Reservation, TheatreHall, Play, Performance
from theatre.serializers import ReservationListSerializer


RESERVATION_URL = reverse("theatre:reservation-list")


class UnauthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_reservations(self):
        Reservation.objects.create(user=self.user)
        Reservation.objects.create(user=self.user)

        res = self.client.get(RESERVATION_URL)

        reservations = Reservation.objects.all()
        serializer = ReservationListSerializer(reservations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["results"], serializer.data)

    def test_create_reservation(self):
        theatre_hall = TheatreHall.objects.create(
            name="TestHall", rows=10, seats_in_row=10
        )

        play = Play.objects.create(
            title="PlayTitle",
            description="PlayDescription"
        )

        performance = Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time="2024-06-07T00:00:00Z"
        )

        payload = {
            "tickets": [
                {"row": 1, "seat": 1, "performance": performance.id},
            ]
        }

        res = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
