from django.test import TestCase
from campus.models import Building, Room, Poi
from django.db.models import Q
from campus.views import search_view
from django.urls import reverse


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
