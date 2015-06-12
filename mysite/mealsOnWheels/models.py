import datetime
from django.db import models
from django.utils import timezone

## The above will deleted later

## Definitions for Food Truck-related classes

class Position(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return "(" + str(self.lat) + "," + str(self.lon) + ")"

class FoodTruck(models.Model):
    key = models.CharField('Key',max_length=50)
    key.primary_key = True
    name = models.CharField('Truck Name', max_length=200)
    foodType = models.CharField('Truck Food Type', max_length=200)
    position = models.ForeignKey(Position)

    def __str__(self):
        return "Truck " + self.key + ": " + self.name

## Needed for authentifiation
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40,blank=True)
    key_expires = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'User profiles'



