from django.core.management.base import BaseCommand
from rooms import models as room_models
from rooms.models import Facility


class Command(BaseCommand):
    help = "This command creates facilities"

    # def add_arguments(self, parser) -> None:

    #     parser.add_argument(
    #         "--times",
    #         help="How many time do you want me to tell you that I love you?",
    #     )

    def handle(self, *args, **options):
        facilities = [
            "Private entrance",
            "Paid parking on premises",
            "Paid parking off premises",
            "Elevator",
            "Parking",
            "Gym",
        ]
        for f in facilities:
            Facility.objects.create(name=f)
        self.stdout.write(self.style.SUCCESS(f"{len(facilities)} Facilities Created!"))
