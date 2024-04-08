from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor, TheatreHall, Performance
from theatre.serializers import PlayListSerializer, PlayRetrieveSerializer

PLAY_URL = reverse("theatre:play-list")


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }

    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Blue", rows=20, seats_in_row=20
    )

    defaults = {
        "play": None,
        "show_time": "2024-06-02 14:00:00",
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        sample_play()
        actor = sample_actor()
        play_with_actor = sample_play()
        play_with_actor.actors.add(actor)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_plays_by_title(self):
        play1 = sample_play(title="Play1")
        play2 = sample_play(title="Play2")

        res = self.client.get(PLAY_URL, {"title": f"{play1.title}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_plays_by_actors(self):
        play1 = sample_play(title="Play1")
        play2 = sample_play(title="Play2")

        actor1 = sample_actor(
            first_name="FirstNameActor1",
            last_name="LastNameActor1"
        )
        actor2 = sample_actor(
            first_name="FirstNameActor2",
            last_name="LastNameActor2"
        )

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        play_with_out_actors = sample_play(title="Play With Out Actors")

        res = self.client.get(PLAY_URL, {"actors": f"{actor1.id},{actor2.id}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play_with_out_actors)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_genres(self):
        play1 = sample_play(title="Play1")
        play2 = sample_play(title="Play2")

        genre1 = sample_genre(name="genre1")
        genre2 = sample_genre(name="genre2")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        play_with_out_genres = sample_play(title="Play With Out Genres")

        res = self.client.get(PLAY_URL, {"genres": f"{genre1.id},{genre2.id}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play_with_out_genres)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_play(self):
        play = sample_play()
        play.actors.add(sample_actor())
        play.genres.add(sample_genre())

        url = detail_url(play.id)
        res = self.client.get(url)

        serializer = PlayRetrieveSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie_forbidden(self):
        payload = {
            "title": "Sample play",
            "description": "Sample description",
        }

        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        payload = {
            "title": "Sample play",
            "description": "Sample description",
        }

        res = self.client.post(PLAY_URL, payload)
        movie = Play.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))

    def test_create_play_with_actors(self):
        actor1 = sample_actor(
            first_name="FirstNameActor1",
            last_name="LastNameActor1"
        )
        actor2 = sample_actor(
            first_name="FirstNameActor2",
            last_name="LastNameActor2"
        )

        payload = {
            "title": "Sample play",
            "description": "Sample description",
            "actors": [actor1.id, actor2.id]
        }

        res = self.client.post(PLAY_URL, payload)
        play = Play.objects.get(id=res.data["id"])
        actors = play.actors.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(actors.count(), 2)
        self.assertIn(actor1, actors)
        self.assertIn(actor2, actors)

    def test_put_play(self):
        payload = {
            "title": "changed title",
            "description": "changed description",
        }

        play = sample_play()
        url = detail_url(play.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_play(self):
        movie = sample_play()
        url = detail_url(movie.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
