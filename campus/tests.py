import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from campus.models import Building, FavoritePoi, Poi, Room


class ModelsTestCase(TestCase):
    def test_create_building(self):
        b = Building.objects.create(
            name="Главный корпус",
            code="Гл",
            address="Университетская, 1",
            lat=55.755,
            lng=37.617,
        )
        self.assertEqual(Building.objects.count(), 1)
        self.assertEqual(str(b), "Главный корпус")

    def test_room_belongs_to_building(self):
        b = Building.objects.create(
            name="Корпус А",
            code="А",
            lat=55.75,
            lng=37.6,
        )
        r = Room.objects.create(
            building=b,
            number="101",
            floor=1,
            description="Лекционная аудитория",
        )
        self.assertEqual(r.building, b)
        self.assertIn("101", str(r))

    def test_poi_creation(self):
        b = Building.objects.create(
            name="Корпус Б",
            code="Б",
            lat=55.76,
            lng=37.61,
        )
        p = Poi.objects.create(
            building=b,
            title="Главный вход",
            type="entrance",
            lat=55.7601,
            lng=37.6101,
            info="Основной вход со стороны двора",
        )
        self.assertEqual(Poi.objects.count(), 1)
        self.assertEqual(str(p), "Главный вход")


class MapViewTestCase(TestCase):
    def test_map_view_without_buildings(self):
        url = reverse("map")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("center_lat", response.context)
        self.assertIn("center_lng", response.context)

    def test_map_view_with_building(self):
        b = Building.objects.create(
            name="Корпус Тест",
            code="Т",
            lat=55.77,
            lng=37.62,
        )
        url = reverse("map")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.context["center_lat"], b.lat)
        self.assertAlmostEqual(response.context["center_lng"], b.lng)


class PoisJsonTestCase(TestCase):
    def test_pois_json_returns_data(self):
        b = Building.objects.create(
            name="Корпус В",
            code="В",
            lat=55.78,
            lng=37.63,
        )
        Poi.objects.create(
            building=b,
            title="Вход",
            type="entrance",
            lat=55.7801,
            lng=37.6301,
        )
        url = reverse("pois_json")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertIn("id", data[0])
        self.assertIn("title", data[0])
        self.assertIn("lat", data[0])
        self.assertIn("lng", data[0])


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.building = Building.objects.create(
            name="Главный корпус",
            code="Гл",
            address="Университетская, 1",
            lat=55.75,
            lng=37.61,
        )
        self.room = Room.objects.create(
            building=self.building,
            number="101",
            floor=1,
            description="Лекционная 101",
        )
        self.poi = Poi.objects.create(
            building=self.building,
            title="Главный вход",
            type="entrance",
            lat=55.7505,
            lng=37.6105,
        )

    def test_search_empty_query(self):
        url = reverse("search")
        response = self.client.get(url, {"q": ""})
        self.assertEqual(response.status_code, 200)

    def test_search_by_building_name(self):
        url = reverse("search")
        response = self.client.get(url, {"q": "Главный"})
        self.assertContains(response, "Главный корпус")

    def test_search_by_room_number(self):
        url = reverse("search")
        response = self.client.get(url, {"q": "101"})
        self.assertContains(response, "101")

    def test_search_by_poi_title(self):
        url = reverse("search")
        response = self.client.get(url, {"q": "вход"})
        self.assertContains(response, "Главный вход")


class PoiManagementTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass1234"
        )
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="pass1234"
        )
        self.building = Building.objects.create(name="A", code="A", lat=1, lng=2)
        self.poi = Poi.objects.create(
            building=self.building,
            title="Столовая",
            type="canteen",
            lat=1.1,
            lng=2.2,
        )

    def test_create_poi_as_superuser(self):
        self.client.force_login(self.superuser)
        payload = {
            "building_id": self.building.id,
            "title": "Лифт",
            "type": "elevator",
            "lat": 1.2,
            "lng": 2.3,
            "info": "У центрального входа",
        }
        response = self.client.post(
            reverse("create_poi"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertTrue(Poi.objects.filter(id=data.get("id"), title="Лифт").exists())

    def test_create_poi_with_invalid_payload_returns_400(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("create_poi"),
            data="{}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Poi.objects.count(), 1)

    def test_toggle_favorite_flow(self):
        self.client.force_login(self.user)
        toggle_url = reverse("toggle_favorite")

        response = self.client.post(
            toggle_url,
            data=json.dumps({"poi_id": self.poi.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FavoritePoi.objects.filter(user=self.user, poi=self.poi).count(), 1)
        self.assertTrue(response.json()["favorited"])

        response = self.client.post(
            toggle_url,
            data=json.dumps({"poi_id": self.poi.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["favorited"])
        self.assertEqual(FavoritePoi.objects.filter(user=self.user, poi=self.poi).count(), 0)

    def test_toggle_favorite_non_post_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("toggle_favorite"))
        self.assertEqual(response.status_code, 405)

    def test_favorites_json_returns_only_user_entries(self):
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass1234"
        )
        FavoritePoi.objects.create(user=self.user, poi=self.poi)
        FavoritePoi.objects.create(
            user=other_user,
            poi=Poi.objects.create(
                building=self.building,
                title="Лаборатория",
                type="lab",
                lat=1.3,
                lng=2.4,
            ),
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("favorites_json"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["poi__title"], "Столовая")


class SearchTemplateTestCase(TestCase):
    def setUp(self):
        self.building = Building.objects.create(
            name="Учебный корпус",
            code="УК",
            lat=55.2,
            lng=37.2,
        )
        self.room = Room.objects.create(
            building=self.building,
            number="202",
            floor=2
        )
        self.poi = Poi.objects.create(
            building=self.building,
            title="Буфет",
            type="canteen",
            lat=55.2005,
            lng=37.2005
        )

    def test_search_results_context(self):
        response = self.client.get(reverse("search"), {"q": "202"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("rooms", response.context)
        self.assertGreater(len(response.context["rooms"]), 0)

    def test_search_template_renders_objects(self):
        response = self.client.get(reverse("search"), {"q": "Буфет"})
        self.assertContains(response, "Буфет")
