from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_view, name="map"),
    path("api/pois/", views.pois_json, name="pois_json"),
    path("search/", views.search_view, name="search"),
    path("api/poi/create/", views.create_poi, name="create_poi"),
    path("api/favorite/toggle/", views.toggle_favorite, name="toggle_favorite"),
    path("api/favorites/", views.favorites_json, name="favorites_json"),
]
 