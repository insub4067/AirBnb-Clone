from django.db import models
from core import models as core_models

# Create your models here.
class Conversation(core_models.TimeStampedModel):
    """List Model Definition"""

    participants = models.ManyToManyField("users.User", blank=True)

    def __str__(self):
        usernames = []
        for user in self.participants.all():
            usernames.append(user.username)
        return ", ".join(usernames)

    def count_messages(self):
        return self.messages.count()

    count_messages.short_description = "Number of Messages"

    def count_participants(self):
        return self.participants.count()

    count_participants.short_description = "Number of Participants"


class Message(core_models.TimeStampedModel):
    """Message Model Definition"""

    message = models.TextField()
    user = models.ForeignKey(
        "users.user", related_name="messages", on_delete=models.CASCADE
    )
    conversation = models.ForeignKey(
        "Conversation", related_name="messages", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.user} says : {self.message}"