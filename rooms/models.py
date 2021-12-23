from django.db import models
from django.urls import reverse
from django.db.models.deletion import CASCADE, SET_NULL

from django_countries.fields import CountryField


from core import models as core_models
from users import models as user_models


# Create your models here.


class AbstractItem(core_models.TimeStampedModel):
    """Abstract Item"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class RoomType(AbstractItem):
    """RoomType Object Definition"""

    class Meta:
        verbose_name_plural = "Room Type"


class Amenity(AbstractItem):
    """Amenity Object Definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):
    """Facility Model Definition"""

    class Meta:
        verbose_name_plural = "Facilitites"


class HouseRule(AbstractItem):
    """HouseRule Model Definition"""

    class Meta:
        verbose_name_plural = "House Rule"


class Photo(core_models.TimeStampedModel):

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey("Room", related_name="photos", on_delete=CASCADE)

    def __str__(self):
        return self.caption


class Room(core_models.TimeStampedModel):

    """Room Model Definition"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    guests = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        "users.User", related_name="rooms", on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        "RoomType", related_name="rooms", blank=True, on_delete=SET_NULL, null=True
    )
    amenities = models.ManyToManyField("Amenity", related_name="rooms", blank=True)
    facilities = models.ManyToManyField("Facility", related_name="rooms", blank=True)
    house_rules = models.ManyToManyField("HouseRule", related_name="rooms", blank=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def total_rating(self):
        try:
            all_reviews = self.reviews.all()
            all_ratings = 0
            for review in all_reviews:
                all_ratings += review.rating_average()

            return round(all_ratings / len(all_reviews), 2)
        except ZeroDivisionError:
            return 0

    def first_photo(self):
        (photo,) = self.photos.all()[:1]
        return photo.file.url
