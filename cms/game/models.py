from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now=True)


class Character(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(primary_key=True)
    character_name = models.CharField(max_length=33)
    character_unapproved_name = models.CharField(max_length=33)
    is_name_rejected = models.BooleanField()
    shirt_color = models.IntegerField()
    shirt_style = models.IntegerField()
    pants_color = models.IntegerField()
    hair_style = models.IntegerField()
    hair_color = models.IntegerField()
    lh = models.IntegerField()
    rh = models.IntegerField()
    eyebrows = models.IntegerField()
    eyes = models.IntegerField()
    mouth = models.IntegerField()
    last_zone = models.IntegerField()
    last_instance = models.IntegerField()
    last_clone = models.IntegerField()
    last_login = models.IntegerField()
