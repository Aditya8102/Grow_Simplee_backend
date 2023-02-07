from login.models import *
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxValueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Account
        fields = ['id', 'email', 'username', 'userType']


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['email', 'username', 'userType', 'password']
        extra_kwargs = {
            'password': {'write_only':True}
        }

    def save(self):
        account = Account(
            email = self.validated_data['email'],
            username = self.validated_data['username'],
            userType = self.validated_data['userType'],

        )
        password = self.validated_data['password']
        account.set_password(password)
        account.save()
        return account