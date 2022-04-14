from pyexpat import model
from turtle import update
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractUser
)

# Create your models here.
class MyUser(AbstractUser):
    email = models.EmailField(unique=True)
    account_updated = models.DateTimeField(auto_now=True)
    account_created = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class UserPicture (models.Model):
    file_name = models.CharField(max_length=256)
    id = models.IntegerField(unique=True,primary_key=True)
    url = models.CharField(max_length=256)
    upload_date = models.DateField()
    user_id = models.IntegerField(unique=True)


    def __str__(self):
        return self.file_name

