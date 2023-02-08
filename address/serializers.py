from .models import *
from rest_framework import serializers
from login.serializers import UserSerializer

class LocationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Location
        fields = ['latitude', 'longitude', 'address']
class OrderSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    driver = UserSerializer()
    class Meta:
        model  = Order
        fields = ['driver','estimatedDeliveryDate', 'calulatedDeliveryDate', 'awb_no', 'deliveryNumber', 'timeDuration', 'loadWeight', 'sheetNumber', 'location']