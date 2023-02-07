from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
 path('AHixaC4MkH8isURsvZ8GvzdRG4G4r1Up/', registration, name = 'register'),
    path('IKkS5YPBWP6GPZiuvPB91hk0Qbm0JNsn/', obtain_auth_token, name = 'login'),
    path('EvpKkUGhjL2ciIsyfSgGa6P2qJrwE3RI/', GetCurrentUserInfo, name = 'AllUserData'),   
]