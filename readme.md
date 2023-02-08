#  Grow Simplee Vehicle Routing Challenge
Grow Simplee Vehicle Routing Challenge

## Prerequisites
Install python3 to run the backend django server.
Install flutter and setup supported ide. For reference: https://docs.flutter.dev/get-started/install 

## Installation

### Frontend

### Backend
Python >= 3.7 recommended. Python 2 not supported.

**Installation**

```
extract backend folder
cd h2c_backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

**Generating optimized Route**:
1. Place the input files in the *input_files* folder. 
2. Add apikey in the scripts/route.py file from gcp in the main function. 
```
    APIKEY="INSERT API KEY HERE"
```
3. Add name of the files in the scripts/route.py file in the desired variable in the main function. 
```
pickup_demand_link="INSERT PICKUP DEMAND FILE HERE"   
pickup_add_link="INSERT PICKUP ADDRESS CSV FILE HERE"
```
4. Run the route.py file. 
```
cd scripts
python3 route.py
```
**Run backend server**:
```
python manage.py runserver
```

**Feeding optimized routes to backend**
This process is currently triggered through an api endpoint in the backend, and basically the output csv files are read and inputted into the database. 

The api endpoint to trigger the feeding is: `/address/feeder/`




## Algorithm used for solving VRP:
 We have used heuristic stratezied algorithms for solving VRP 
 i.e-Clarke and Wright SAVING amd path_cheapest_ARC where it's results are then enhanced by local search options such as simulated annealing,tabu_search and guided local search options


## Technologies Used:
- [Flutter Framework](https://docs.flutter.dev/get-started/install)
- [Django](https://www.djangoproject.com/)
- [Google Cloud Platform](https://cloud.google.com/)
- [Google Maps API](#)
- [Google OR-Tools](#)

