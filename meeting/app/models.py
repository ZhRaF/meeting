from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RoomMember(models.Model):
    uid = models.CharField(max_length=200)
    room_name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
# he used name
    def __str__(self):
        return f'{self.user.username} in {self.room_name}'