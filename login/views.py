from rest_framework import serializers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
# from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle
from .models import USER_CHOICES, Account
from django.http import HttpResponse
# Create your views here.

# Create your views here.



@api_view(['POST',])
# @throttle_classes([ScopedRateThrottle, AnonRateThrottle])
def registration(request):
    if request.method == 'POST':
        requester = {
            'email': request.data['email'],
            'username': request.data['username'],
            'password' : request.data['password']
        }
        UserLevel = request.data['level']
        # password = request.data['password']
        level = ""
        if UserLevel == 'DP':
            level = USER_CHOICES[0][0]
        elif UserLevel == 'AD':
            level = USER_CHOICES[1][0]
        elif UserLevel == 'PA':
            level = USER_CHOICES[2][0]
        
        requester['userType'] = level
        serializer = RegistrationSerializer(data = requester)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "successfully registed a new user"
            status = 200
            # data['email'] = account.email
            # data['username'] = account.username
            # token = Token.objects.get(user=account).key
            # data['token'] = token
        else:
            data = serializer.errors 
            status = 422
        return Response(data, status)


@api_view(['GET',])   # you will only recieve token, and email adress
@permission_classes((IsAuthenticated, ))
def GetCurrentUserInfo(request):
    cuser = request.user
    cuserSerialized = UserSerializer(cuser)
    return Response(data = cuserSerialized.data, status=200)

