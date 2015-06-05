import datetime
from django.db import models
from django.utils import timezone

# Create your models here.
## class temp(models.Model):
##    str = models.IntegerField(default=1);


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



## Authentification
from django.contrib.auth.models import User

class UserProfile(models.Model):
    #"This"line"is"required."Links"UserProfile"to"a"User"model"instance.
    user = models.OneToOneField(User)

    ## the additional attribute that we wish to include
    website= models.URLField(blank=True)
    ## picture =models.ImageField(upload_to='profile_images',blank=True)

    def __unicode__(self):
        return self.user.username


