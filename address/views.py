from rest_framework import serializers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
# from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle
from login.models import USER_CHOICES, Account
from django.http import HttpResponse
# Create your views here.
# according to date, latitdue and longitude. 
#  and all csvs to be transmitted for a paticular driver. 

@api_view(['POST']) 
@permission_classes((IsAuthenticated, )) 
def LocationPointers(request):

    cuser = request.user
    if cuser == None: 
        return Response(status=status.HTTP_404_NOT_FOUND, )
    else:
        if cuser.userType == USER_CHOICES[1][0]:
            
