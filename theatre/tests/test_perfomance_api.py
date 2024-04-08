from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import TheatreHall, Performance, Play
from theatre.serializers import (
    PerformanceListSerializer,
    PerformanceDetailSerializer
)

PERFORMANCE_URL = reverse("theatre:performance-list")


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="TestHall", rows=10, seats_in_row=10
    )

    play = Play.objects.create(
        title="PlayTitle",
        description="PlayDescription"
    )

    defaults = {
        "play": play,
        "theatre_hall": theatre_hall,
        "show_time": "2024-06-07T00:00:00Z"
    }

    defaults.update(params)

    return Performance.objects.create(**defaults)


def detail_url(play_id):
    return reverse("theatre:performance-detail", args=[play_id])


class UnauthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_performances(self):
        sample_performance()
        sample_performance()

        res = self.client.get(PERFORMANCE_URL)
        performances = Performance.objects.all()
        serializer = PerformanceListSerializer(performances, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for obj in res.data:
            self.assertIn(obj, serializer.data)

    def test_filter_performances_by_date(self):
        performance1 = sample_performance(show_time="2024-03-02T00:00:00Z")
        performance2 = sample_performance(show_time="2025-03-02T00:00:00Z")

        res = self.client.get(PERFORMANCE_URL, {"date": "2024-03-02"})

        serializer1 = PerformanceListSerializer(performance1)
        serializer2 = PerformanceListSerializer(performance2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_performances_by_play_id(self):
        play2 = Play.objects.create(
            title="PlayTitle2",
            description="PlayDescription2"
        )

        performance1 = sample_performance()
        performance2 = sample_performance(play=play2)

        res = self.client.get(
            PERFORMANCE_URL, {"play": f"{performance2.play.id}"}
        )

        serializer1 = PerformanceListSerializer(performance1)
        serializer2 = PerformanceListSerializer(performance2)

        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_retrieve_performance(self):
        performance = sample_performance()

        url = detail_url(performance.id)

        res = self.client.get(url)
        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_performance_forbidden(self):
        theatre_hall = TheatreHall.objects.create(
            name="TestHall", rows=10, seats_in_row=10
        )

        play = Play.objects.create(
            title="PlayTitle",
            description="PlayDescription"
        )

        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": "2024-06-07T00:00:00Z"
        }

        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPerformanceApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_performance(self):
        theatre_hall = TheatreHall.objects.create(
            name="TestHall", rows=10, seats_in_row=10
        )

        play = Play.objects.create(
            title="PlayTitle",
            description="PlayDescription"
        )

        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": "2024-06-07T00:00:00Z"
        }

        res = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        performance = Performance.objects.get(id=res.data["id"])

        self.assertEqual(payload["play"], performance.play.id)
        self.assertEqual(payload["theatre_hall"], performance.theatre_hall.id)
        self.assertEqual(
            payload["show_time"][:10], str(performance.show_time)[:10]
        )

    def test_patch_performance(self):
        payload = {
            "show_time": "2029-06-07T00:00:00Z"
        }

        performance = sample_performance()
        url = detail_url(performance.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_performance(self):
        performance = sample_performance()
        url = detail_url(performance.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
