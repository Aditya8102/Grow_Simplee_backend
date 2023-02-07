from django.db import models
from login.models import *
# Create your models here.


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    latitude = models.FloatField(default = 23.0707)#change the actual default value
    longitude = models.FloatField(default = 80.0982)#change the actual default value
    address = models.TextField(default="")


class Order(models.Model):
    driver = models.ForeignKey(Account, on_delete = models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    estimatedDeliveryDate = models.DateTimeField()
    calulatedDeliveryDate = models.DateTimeField()
    awb_no = models.CharField(max_length=20)
    deliveryNumber = models.IntegerField()
    timeDuration = models.IntegerField()
    loadWeight = models.IntegerField()
    sheetNumber = models.IntegerField()

