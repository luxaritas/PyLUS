from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    token = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now=True)
    address = models.GenericIPAddressField()
    port = models.IntegerField()
    objid = models.BigIntegerField()

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    lego_club = models.BooleanField()
    free_to_play = models.BooleanField()
    new_subscriber = models.BooleanField()
    front_character = models.SmallIntegerField()

class Character(models.Model):
    slot = models.SmallIntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=33)
    unapproved_name = models.CharField(max_length=33)
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
