from django.db import models
from django.contrib.auth.models import User


class Building(models.Model):
    name = models.CharField("Название корпуса", max_length=255)
    code = models.CharField(
        "Код корпуса",
        max_length=50,
        blank=True,
        help_text="Например: Гл, А, Б, ИИТ и т.п.",
    )
    address = models.CharField("Адрес", max_length=255, blank=True)

    lat = models.FloatField("Широта", help_text="Для отображения на карте")
    lng = models.FloatField("Долгота", help_text="Для отображения на карте")

    def __str__(self):
        return self.name or self.code or f"Корпус #{self.pk}"


class Room(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name="Корпус",
    )
    number = models.CharField("Номер аудитории", max_length=50)
    floor = models.IntegerField("Этаж", default=1)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return f"{self.building.code or self.building.name} – {self.number}"


class Poi(models.Model):
    """Точки интереса: столовые, деканаты, входы, лифты и т.п."""
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="pois",
        verbose_name="Корпус",
        null=True,
        blank=True,
    )
    title = models.CharField("Название объекта", max_length=255)
    type = models.CharField(
        "Тип",
        max_length=50,
        help_text="Например: столовая, деканат, вход, туалет",
    )

    lat = models.FloatField("Широта")
    lng = models.FloatField("Долгота")

    info = models.TextField("Доп. информация", blank=True)

    def __str__(self):
        return self.title


class FavoritePoi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_pois")
    poi = models.ForeignKey(Poi, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "poi")  # нельзя добавить одно и то же дважды

    def __str__(self):
        return f"{self.user.username} → {self.poi.title}"