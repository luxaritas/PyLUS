from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    lego_club = models.BooleanField()
    free_to_play = models.BooleanField()
    new_subscriber = models.BooleanField()

class Session(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    token = models.BinaryField()
    ip = models.GenericIPAddressField()
    port = models.SmallIntegerField()
    clone = models.IntegerField(null=True)
    created = models.DateTimeField()

class Character(models.Model):
    def save(self, *args, **kwargs):
        if self.is_front:
            old_front = self.account.character_set.get(is_front=True)
            old_front.is_front = False
            old_front.save()
        super().save(*args, **kwargs)
    
    objid = models.BigIntegerField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    is_front = models.BooleanField(default=True)
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

class Mission(models.Model):
    mission = models.SmallIntegerField()
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    state = models.SmallIntegerField()
    times_completed = models.SmallIntegerField()
    last_completion = models.IntegerField()
    progress = models.IntegerField()
