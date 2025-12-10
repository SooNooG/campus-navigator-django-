from django.contrib import admin
from .models import Building, Room, Poi


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "address", "lat", "lng")
    search_fields = ("name", "code", "address")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "building", "number", "floor")
    list_filter = ("building", "floor")
    search_fields = ("number", "description")


@admin.register(Poi)
class PoiAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "building", "lat", "lng")
    list_filter = ("type", "building")
    search_fields = ("title", "info")
