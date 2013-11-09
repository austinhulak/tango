from django.db import models
import urllib
#importing the User model
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

class UserProfile(models.Model):
    #this next line links this class to the User model instance in the models file
    user = models.OneToOneField(User)

    #here we are adding additional attributes
    website = models.URLField(blank=True)
    #'upload_to' automatically places all uploaded files into MEDIA/{upload_to value}.. so in this case MEDIA/profile_images/
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Overide the __unicode__() method to return out something meanginful?
    def __unicode__(self):
        return self.user.username
