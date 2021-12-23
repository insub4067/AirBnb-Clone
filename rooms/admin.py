from django.contrib import admin
from django.utils.html import mark_safe
from . import models

# Register your models here.


# class PhotoInline(admin.TabularInline):
#     """Photo Inline Definition"""

#     model = models.Photo
#     classes = ["collapse"]


class PhotoInline(admin.StackedInline):
    """Photo Inline Definition"""

    model = models.Photo
    classes = ["collapse"]


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    """Room Admin Definition"""

    inlines = (PhotoInline,)

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "description", "country", "city", "address", "price")},
        ),
        (
            "Times",
            {
                "fields": (
                    "check_in",
                    "check_out",
                    "instant_book",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "Spaces",
            {
                "fields": (
                    "beds",
                    "bedrooms",
                    "baths",
                    "guests",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "More about the space",
            {
                "fields": (
                    "amenities",
                    "facilities",
                    "house_rules",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "Last Details",
            {
                "fields": ("host",),
                "classes": ["collapse"],
            },
        ),
    )

    list_display = (
        "name",
        "country",
        "city",
        "price",
        "beds",
        "bedrooms",
        "baths",
        "guests",
        "check_in",
        "check_out",
        "instant_book",
        "count_amenities",
        "count_photos",
        "total_rating",
    )

    list_filter = (
        "instant_book",
        "host__superhost",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
        "city",
        "country",
    )

    raw_id_fields = ("host",)

    search_fields = ("city",)

    filter_horizontal = (
        "amenities",
        "facilities",
        "house_rules",
    )

    def count_amenities(self, obj):
        return obj.amenities.count()

    def count_photos(self, obj):
        return obj.photos.count()

    count_photos.short_description = "photo count"


@admin.register(models.Amenity, models.Facility, models.HouseRule, models.RoomType)
class ItemAdim(admin.ModelAdmin):
    """Item Admin Definition"""

    list_display = (
        "name",
        "used_by",
    )

    def used_by(self, obj):
        return obj.rooms.count()


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Photo Admin Definition"""

    list_display = [
        "__str__",
        "get_thumbnail",
    ]

    def get_thumbnail(self, obj):
        return mark_safe(f"<img width='50px' src='{obj.file.url}'/>")

    get_thumbnail.short_description = "Thumbnail"
