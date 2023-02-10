from django.urls import path
from .views import *
urlpatterns = [
 path('csvDetails/', LocationPointers, name = 'location pointers'),
 path('feeder/', AddDeliveryData, name = 'Adding Route Data'),
]