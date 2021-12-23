import random
from django.core.management.base import BaseCommand
from django_seed import Seed
from rooms import models as room_models
from users import models as user_models
from reviews import models as review_models


class Command(BaseCommand):
    help = "This command creates reviews"

    def add_arguments(self, parser) -> None:

        parser.add_argument(
            "--numbers",
            default=1,
            type=int,
            help="How many reviews do you want to create?",
        )

    def handle(self, *args, **options):
        number = options.get("numbers")
        seeder = Seed.seeder()
        all_users = user_models.User.objects.all()
        all_rooms = room_models.Room.objects.all()
        seeder.add_entity(
            review_models.Review,
            number,
            {
                "user": lambda x: random.choice(all_users),
                "room": lambda x: random.choice(all_rooms),
                "accuracy": lambda x: random.randint(0, 6),
                "communication": lambda x: random.randint(0, 6),
                "cleanliness": lambda x: random.randint(0, 6),
                "location": lambda x: random.randint(0, 6),
                "check_in": lambda x: random.randint(0, 6),
                "value": lambda x: random.randint(0, 6),
            },
        )
        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number} Reviews Created!"))
