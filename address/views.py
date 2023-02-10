from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from login.models import USER_CHOICES, Account
from .models import *
from datetime import datetime


@api_view(['POST']) 
@permission_classes((IsAuthenticated, )) 
def LocationPointers(request):
    cuser = request.user
    if cuser == None: 
        return Response(status=status.HTTP_404_NOT_FOUND, data = "Wrong user ")
    else:

        if cuser.userType == "DP":
            orders = Order.objects.filter(driver = cuser)
            day = str(request.data['calculated_date']),
            daystr = ''
            for item in day:
                daystr = daystr + item
            format = '%Y/%m/%d'
            dayDate = datetime.strptime(daystr, format).date()
            orderList = []
            for order in orders:
                if order.calulatedDeliveryDate.date() == dayDate:
                    orderList.append(order)
            serializedOrders = OrderSerializer(orderList, many = True)

            ResponseData = {
                    'resp' : serializedOrders.data,
                    }
            return Response(data = ResponseData, status = 200)
        elif cuser.userType == "DA":
            orders = Order.objects.all()
            day = str(request.data['calculated_date']),
            daystr = ''
            for item in day:
                daystr = daystr + item
            format = '%Y/%m/%d'
            dayDate = datetime.strptime(daystr, format).date()
            orderList = []
            for order in orders:
                if order.calulatedDeliveryDate.date() == dayDate:
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

