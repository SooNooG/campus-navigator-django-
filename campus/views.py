from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from .models import Building, FavoritePoi, Room, Poi
from django.contrib.auth.decorators import login_required
import json


def map_view(request):
    poi_id = request.GET.get("poi_id")
    selected_poi = None

    if poi_id:
        try:
            selected_poi = Poi.objects.get(id=poi_id)
            center_lat = selected_poi.lat
            center_lng = selected_poi.lng
        except Poi.DoesNotExist:
            building = Building.objects.first()
            if building:
                center_lat = building.lat
                center_lng = building.lng
            else:
                center_lat = 55.75
                center_lng = 37.61
    else:
        building = Building.objects.first()
        if building:
            center_lat = building.lat
            center_lng = building.lng
        else:
            center_lat = 55.75
            center_lng = 37.61

    context = {
        "center_lat": center_lat,
        "center_lng": center_lng,
        "selected_poi_id": selected_poi.id if selected_poi else None,
    }
    return render(request, "campus/map.html", context)


def pois_json(request):
    pois = Poi.objects.all().values("id", "title", "type", "lat", "lng", "info")
    return JsonResponse(list(pois), safe=False)


def search_view(request):
    query = request.GET.get("q", "").strip()
    buildings = rooms = pois = []

    if query:
        buildings = Building.objects.filter(name__icontains=query)
        rooms = Room.objects.filter(number__icontains=query)
        pois = Poi.objects.filter(title__icontains=query)

    context = {
        "query": query,
        "buildings": buildings,
        "rooms": rooms,
        "pois": pois,
    }
    return render(request, "campus/search_results.html", context)


@require_http_methods(["POST"])
@user_passes_test(lambda u: u.is_superuser)
def create_poi(request):
    try:
        data = json.loads(request.body)
        building_id = data.get("building_id")
        building = None
        if building_id:
            building = Building.objects.get(id=building_id)

        poi = Poi.objects.create(
            building=building,
            title=data["title"],
            type=data["type"],
            lat=data["lat"],
            lng=data["lng"],
            info=data.get("info", ""),
        )
        return JsonResponse({"id": poi.id, "success": True})
    except (KeyError, ValueError, json.JSONDecodeError, Building.DoesNotExist) as e:
        return JsonResponse({"error": "Invalid data", "details": str(e)}, status=400)


@login_required
def toggle_favorite(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        data = json.loads(request.body)
        poi_id = data["poi_id"]
        poi = Poi.objects.get(id=poi_id)
        favorite, created = FavoritePoi.objects.get_or_create(user=request.user, poi=poi)
        if not created:
            favorite.delete()
            return JsonResponse({"favorited": False, "message": "Удалено из избранного"})
        return JsonResponse({"favorited": True, "message": "Добавлено в избранное"})
    except (Poi.DoesNotExist, KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Неверные данные"}, status=400)


@login_required
def favorites_json(request):
    favorites = FavoritePoi.objects.filter(user=request.user).values(
        "poi__id", "poi__title", "poi__type", "poi__lat", "poi__lng", "poi__info"
    )
    return JsonResponse(list(favorites), safe=False)
