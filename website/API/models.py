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
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
