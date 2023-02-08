from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from login.models import USER_CHOICES, Account
from .models import *


@api_view(['POST']) 
@permission_classes((IsAuthenticated, )) 
def LocationPointers(request):
    cuser = request.user
    if cuser == None: 
        return Response(status=status.HTTP_404_NOT_FOUND, )
    else:
        if cuser.userType == USER_CHOICES[1][0]:
            orders = Order.objects.filter(driver = cuser)
            day = request.data.get('calculated_date', None),
            orderList = []
            for order in orders:
                if order.calulatedDeliveryDate == day:
                    orderList.append(order)
            serializedOrders = OrderSerializer(orderList, many = True)

            ResponseData = {
                    'Data' : serializedOrders.data,
                    }
            return Response(data = ResponseData, status = 200)
        elif cuser.userType == USER_CHOICES[2][0]:
            orders = Order.objects.all()
            day = request.data.get('calculated_date', None),
            orderList = []
            for order in orders:
                if order.calulatedDeliveryDate == day:
                    orderList.append(order)
            serializedOrders = OrderSerializer(orderList, many = True)
            ResponseData = {
                    'Data' : serializedOrders.data,
                    }
            return Response(data = ResponseData, status = 200)



@api_view(['POST']) 
@permission_classes((IsAuthenticated, )) 
def AddDeliveryData(request):
    cuser = request.user
    if cuser != None and cuser.userType == USER_CHOICES[2][0]: 
        # run the script and then read csv 
        return Response(data = "The csv files have been read", status=200)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND, )

