from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now=True)
