import csv
import re 
from datetime import datetime
import pytz
from address.models import *
from login.models import *
def createEntry(driverNo, index, nodes, time, load, awb_no, address, latitude, longitude): 
    location = Location.objects.create(
        latitude = latitude, 
        longitude = longitude,
        address = address
    )
    driver = Account.objects.filter(id = driverNo)[0]
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    order = Order.objects.create(
        driver = driver,
        location = location, 
        awb_no = awb_no,
        deliveryNumber = int(nodes),
        timeDuration = int(time),
        loadWeight = int(load),
        sheetNumber = 1,
        calulatedDeliveryDate = today
    )
def csvFileReader(path_to_csv):
    driverNo = path_to_csv.split('/')[-1].split('.')[0].split(' ')[-1]
    with open(path_to_csv, 'r') as file_obj:
        read_obj = csv.reader(file_obj)
        header = next(read_obj)
        count = 0
        for row in read_obj:
                index = row[0]
                nodes = row[1]
                time = row[2]
                load = row[3]
                awb_no = row[4]
                address = row[5]
                latitude = row[6]
                longitude = row[7]
                try:
                    createEntry(driverNo, index, nodes, time, load, awb_no, address, latitude, longitude)
                    count +=1
                except:
                    print("Entry for "+ str(index) + " not creatd. Row  ")
        print("total entries "+str(count))

csvFileReader("/home/parwaan/Desktop/InterIIT_2021/h2c_backend/delivery/output_files/Initial_Driver 1.csv")