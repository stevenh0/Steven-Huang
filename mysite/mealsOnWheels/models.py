import datetime
from django.db import models
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField('My Question Text',max_length = 200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    was_published_recently.short_description ='Published recently?'
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True

class Choice(models.Model):
    ## ForeignKey: many to one relationship
    question = models.ForeignKey(Question)
    choice_text = models.CharField('My Choice Text',max_length = 200)
    votes = models.IntegerField("My Votes",default=0)

    def __str__(self):
        return self.choice_text

## The above will deleted later

class Position(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

class FoodTruck(models.Model):
    key = models.CharField('Key',max_length=50)
    key.primary_key = True
    name = models.CharField('Truck Name', max_length=200)
    foodType = models.CharField('Truck Food Type', max_length=200)
    position = Position()

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



