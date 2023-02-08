from __future__ import print_function
import ortools
import googlemaps
import pandas as pd
import numpy as np
import requests
import urllib.request
import json
import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def delivery(delivery_addlink,delivery_demandslink,API_KEY):
  def read_address(delivery_addlink):
    dfd = pd.read_csv(delivery_addlink)
    datalistd= dfd['address'].to_list()
    dfd1 = pd.read_csv(delivery_addlink)
    add= dfd1['address'].to_list()
    dfd2 = pd.read_csv(delivery_addlink)
    awb= dfd2['AWB'].to_list()
    delivery_add=datalistd # list of addreses->delivery_add
    
    #convert addresses to lat and long
    latitude_delivery=[]
    longitude_delivery=[]
    for i in range(len(datalistd)):
      datalistd[i] = datalistd[i].replace(" ","+")
    for i in range(len(datalistd)):
      r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + datalistd[i] +'&key=' + API_KEY)
      resp = json.loads(r.text)
      lat = resp['results'][0]['geometry']['location']['lat']
      lon = resp['results'][0]['geometry']['location']['lng']
      latitude_delivery.append(lat)
      longitude_delivery.append(lon)
    
    # return(latitude_delivery)
    return delivery_add,add,awb,datalistd,latitude_delivery,longitude_delivery

  def time_calculator(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2
    dist = 2 * np.arcsin(np.sqrt(haver_formula ))
    m = 6367 * dist *1000
    time=m/6.11
    return int(math.floor(time))

  #creating time matrix from disptach loctions 
  def create_time_matrix(latitude_delivery,longitude_delivery):
    time_matrix = np.zeros((len(latitude_delivery),len(longitude_delivery)))
    for i in range(len(longitude_delivery)):
      for j in range(len(longitude_delivery)):
        # calculate the distance using the distance matrix function
        time_matrix[i, j] = time_calculator(longitude_delivery[i], latitude_delivery[i],longitude_delivery[j],latitude_delivery[j])
    return time_matrix

  # creating time_windows:
  def create_time_windows(delivery_add):
      time_windows = []
      for i in range(len(delivery_add)):
         time_windows.append((0,360*60))
      return time_windows
  

  # creating demands list
  # file needs to be uploaded
  def read_demands(delivery_demandslink):
    demands=[]  
    dd=pd.read_csv(delivery_demandslink)
    demands1=dd['demand'].to_list()
    for i in range(len(demands1)):
      demands.append(demands1[i])
    return demands

  def vehicles_number(delivery_add):
      num_vehicles=math.floor(len(delivery_add)/20)
      return num_vehicles

  # adding vehicle capacities
  def delivery_capacity(num_vehicles):
    vehicle_capacities=[640000]*num_vehicles
    return vehicle_capacities

  def delivery_vrp(time_matrix1,initial_route_of_delivery,time_windows,num_vehicles,demands,vehicle_capacities,depot_index):
    
    time_limit_seconds = 300 # time limit for calculation #could be calculated later
    def create_data_model(time_matrix, time_windows, num_vehicles, demands, vehicle_capacities, depot_index):
        """Stores the data for the problem."""
        
        data = {}
        data['time_matrix'] = time_matrix1
        data['time_windows'] = time_windows
        data['num_vehicles'] = num_vehicles
        data['demands'] = demands
        data['vehicle_capacities'] =vehicle_capacities
        data['depot'] = depot_index
        return data
    """Capacitated Vehicles Routing Problem (CVRP) with Time Windows."""
       #For getting the list of final time of each delivery man
    #Route of each driver with its node number,time of delivery and quantity it is carrying 
    def print_solution(data, manager, routing, solution):
        """Prints solution on console."""
        total_distance = 0
        total_load = 0
        time_dimension = routing.GetDimensionOrDie('Time')
        total_time = 0
        time_ss = []
        
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                route_load += data['demands'][node_index]
                plan_output += 'Place {0:>2} Arrive at {2:>2}sec Depart at {3:>2}sec (Load {1:>2})\n'.format(manager.IndexToNode(index), route_load,solution.Min(time_var), solution.Max(time_var))
                time_ss.append([manager.IndexToNode(index),solution.Max(time_var),route_load])
                # output_list.append('{0}'.format(manager.IndexToNode(index)))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                
           
            initial_route_of_delivery[vehicle_id]=time_ss
            # time_list2.append(time_ss)
            # time_list.append(solution.Max(time_var))  
            # time_ss = []  
            time_var = time_dimension.CumulVar(index)
            total_time += solution.Min(time_var)
            
            plan_output +="Place {0:>2} Arrive at {2:>2}sec \n\n".format(manager.IndexToNode(index), route_load,(solution.Min(time_var)),solution.Max(time_var))
            
            # route output
            plan_output += 'Load of the route: {}\n'.format(route_load)
            plan_output += 'Time of the route: {}sec\n'.format(solution.Min(time_var))
            plan_output += "--------------------"
            
            #print(l1)
            time_ss.append([manager.IndexToNode(index),solution.Max(time_var),route_load])
            # time_list[vehicle_id]=time_ss
            time_ss=[]
            # output_list.append(-1)
            print(plan_output)
            total_load += route_load

        print('Total load of all routes: {}'.format(total_load))
        print('Total time of all routes: {}sec'.format(total_time))
      

        
    def main2():
        """Solve the VRP with time windows."""
        # Instantiate the data problem.
        # time_windows = create_time_windows()
        # num_vehicles = vehicles_number()
        # demands = read_demands()
        # vehicle_capacities = delivery_capacity()
        data = create_data_model(time_matrix1, time_windows, num_vehicles, demands, vehicle_capacities, depot_index)
        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                               data['num_vehicles'], data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)


        # Create and register a transit callback.
        def time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            # Convert from routing variable Index to time matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['time_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(time_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add Capacity constraint.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],  # vehicle maximum capacities
            False,  # start cumul to zero
            'Capacity')
        penalty = 1000
        for node in range(1, len(data['time_matrix'])):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
        
        # Add Time Windows constraint.
        time = 'Time'
        routing.AddDimension(
            transit_callback_index,
            0,  # allow waiting time
            360*60,  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            time)
        time_dimension = routing.GetDimensionOrDie(time)
        
        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == 0:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # Add time window constraints for each vehicle start node.
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
                                                    data['time_windows'][0][1])

        # Instantiate route start and end times to produce feasible times.
        for i in range(data['num_vehicles']):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.End(i)))

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.time_limit.seconds = time_limit_seconds
        search_parameters.local_search_metaheuristic =(
        routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
        search_parameters.time_limit.seconds = time_limit_seconds
        
        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        # Print solution on console.
        if solution:
            print_solution(data, manager, routing, solution)
        return solution
    solution = main2()
  def route_carry_forward(initial_route_of_delivery):
     index=0
     maxload_per_rider=[]
     updated_initial_route_of_delivery={}
     for key,value in dict(initial_route_of_delivery).items():
       if(value!=[[0, 0, 0], [0, 0, 0]]):
         updated_initial_route_of_delivery.update({index:value})
         maxload_per_rider.append(value[len(value)-1][2])
         index+=1
     for key,value in dict(updated_initial_route_of_delivery).items():
       for i in value:
         i[2]=maxload_per_rider[key]-i[2]
     return updated_initial_route_of_delivery,maxload_per_rider

  def create_final_route(updated_initial_route_of_delivery):
     final_route_of_delivery={}
     for key, value in dict(updated_initial_route_of_delivery).items():
       temp_outer_list = []
       for small_list in value:
         temp_inner_list = []
         for i in small_list:
           temp_inner_list.append(i)
         temp_outer_list.append(temp_inner_list)
       final_route_of_delivery[key] = temp_outer_list
       print(final_route_of_delivery)
     return final_route_of_delivery

  def update_final_route(final_route_of_delivery,maxload_per_rider,awb,add,latitude_delivery,longitude_delivery):
    for key,value in dict(final_route_of_delivery).items():
      for j in value:
        # j[2]=maxload_per_rider
        j.append(awb[j[0]])
        j.append(add[j[0]])
        j.append(latitude_delivery[j[0]])
        j.append(longitude_delivery[j[0]])
    return final_route_of_delivery

  def create_delivery_csv(final_route_of_delivery): 
    for key,value in dict(final_route_of_delivery).items():
      Nodes=[]
      Time=[]
      Load=[]
      Address=[]
      AWB_NO=[]
      latitude=[]
      longitude=[]
      for j in value:
        Nodes.append(j[0])
        Time.append(j[1])
        Load.append(j[2])
        Address.append(j[4])
        AWB_NO.append(j[3])
        latitude.append(j[5])
        longitude.append(j[6])
      initial_dict = {'Nodes': Nodes, 'Time': Time, 'Load': Load,'AWB_NO':AWB_NO,'Address':Address,'latitude':latitude,'longitude':longitude}  
      df = pd.DataFrame(initial_dict)
      df.to_csv(f'Initial_Driver {key}.csv')

    # calling of above functions starts from this point on: 


  delivery_add,add,awb,datalistd,latitude_delivery,longitude_delivery=read_address(delivery_addlink)
  time_matrix=create_time_matrix(latitude_delivery,longitude_delivery)
  time_windows=create_time_windows(delivery_add)
#   demands=read_demands(delivery_demandslink)
  np.random.seed(101)
  demands = np.random.randint(27,32000,size= (215))
  demands[0] = 0
  
  num_vehicles=vehicles_number(delivery_add)
  vehicle_capacities=delivery_capacity(num_vehicles)
  initial_route_of_delivery={}
  # delivery_vrp(time_matrix,initial_route_of_delivery)
  depot_index=0


  delivery_vrp(time_matrix,initial_route_of_delivery,time_windows,num_vehicles,demands,vehicle_capacities,depot_index)

  updated_initial_route_of_delivery,maxload_per_rider=route_carry_forward(initial_route_of_delivery)
  print(maxload_per_rider)
  final_route_of_delivery=create_final_route( updated_initial_route_of_delivery)
  final_route_of_delivery=update_final_route(final_route_of_delivery,maxload_per_rider,awb,add,latitude_delivery,longitude_delivery)
  create_delivery_csv(final_route_of_delivery)
  print(delivery_add)
  print(add)
  print(awb)
  print(datalistd)
  print(latitude_delivery)       
  print(longitude_delivery)
  print(demands)
  print(time_matrix)
  print(initial_route_of_delivery)
  print(maxload_per_rider)
  print(final_route_of_delivery)
  print(updated_initial_route_of_delivery)
  return initial_route_of_delivery,updated_initial_route_of_delivery,add,awb


def pickup(updated_initial_route_of_delivery,add,awb,pickup_add_link,pickup_demand_link,API_KEY):
  # time_list4={}
  

  def create_delivery_add(add):
    delivery_add=[]
    for i in add:
      i=i.replace(" ","+")
      delivery_add.append(i)
    return delivery_add
  # the previous data used 1st pickup (using few functions for 1st pickup)
  # not general
  def merge(pickup_add_link,add,awb):
    merge2add=[]
    merge2awb=[]
    dfp = pd.read_csv(pickup_add_link)
    merge2add= dfp['address'].to_list()
    merge2awb=dfp['AWB'].to_list()
    add=add+merge2add
    awb=awb+merge2awb
    # print(add,awb)
    return add,awb


  


  # general pickup
  def add_pickup(pickup_add_link):
    dfp = pd.read_csv(pickup_add_link)
    pickupadd_list= dfp['address'].to_list()
    for i in range(len(pickupadd_list)):
      pickupadd_list[i]=pickupadd_list[i].replace(" ","+")
    pickup_add=pickupadd_list
    # print(pickup_add)
    return pickup_add 

  #general pickup
  def pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery):
    list1=[]
    list2=[]
    time_listupdate=[]
    
    time_listupdate.append(0)
    
    list1.append(0)
    list2.append(0)
    for key,value in dict(updated_initial_route_of_delivery).items():
      for i in range (len(value)):
        if(i==len(value)-2):
          list1.append(value[i][0])
          list2.append(value[i][0])
          time_listupdate.append(value[i][1])
          # load_listupdate.append(value[i][2])
    # print(list1,list2,time_listupdate)
    return list1,list2,time_listupdate


    #general pickup
  def address(delivery_add,list1):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    adresses=[]
    for i in list1:
      adresses.append(delivery_add[int(i)])
    # print(adresses)
    return adresses


  

  #general pickup
  def lat_long_pickup(add):
    latitude_total=[]
    longitude_total=[]
    for i in range(len(add)):
      r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + add[i] +'&key=' + API_KEY)
      resp = json.loads(r.text)
      print(resp)
      lat = resp['results'][0]['geometry']['location']['lat']
      lon = resp['results'][0]['geometry']['location']['lng']
      latitude_total.append(lat)
      longitude_total.append(lon)
      # print(latitude_total,longitude_total)
    return latitude_total,longitude_total

  # #not general pickup
  def appending_list1_forpickup(pickup_add,list1,delivery_add):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    size= len(delivery_add)
    for i in range(len(pickup_add)):
      list1.append(size+i)
    # print(list1)
    return list1
  def update_address(adresses,pickup_add):
    for i in pickup_add:
      adresses.append(i)
    return adresses

  def lat_long_pickup1(adresses):
    latitude_partial=[]
    longitude_partial=[]
    for i in range(len(adresses)):
      r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + add[i] +'&key=' + API_KEY)
      resp = json.loads(r.text)
      lat = resp['results'][0]['geometry']['location']['lat']
      lon = resp['results'][0]['geometry']['location']['lng']
      latitude_partial.append(lat)
      longitude_partial.append(lon)
      # print(latitude_total,longitude_total)
    return latitude_partial,longitude_partial

  def time_calculator(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2
    dist = 2 * np.arcsin(np.sqrt(haver_formula ))
    m = 6367 * dist *1000
    time=m/6.11
    return int(math.floor(time))

  #general pickup
  def time_matrix(latitude_partial,longitude_partial):
    # def create_time_matrix(latitude_delivery,longitude_delivery):
    time_matrix = np.zeros((len(latitude_partial),len(longitude_partial)))
    for i in range(len(latitude_partial)):
      for j in range(len(longitude_partial)):
        # calculate the distance using the distance matrix function
        time_matrix[i, j] = time_calculator(longitude_partial[i], latitude_partial[i],longitude_partial[j],latitude_partial[j])
    return time_matrix
    
 #general pickup
  def multi_end_and_depot(list2):
  #  list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
   multi_depot=[]
   multi_endhub=[]
   for i in range(1,len(list2)):
     multi_depot.append(i)
   for i in range(len(multi_depot)):
     multi_endhub.append(0)   
  #  print(multi_depot,multi_endhub)
   return multi_depot,multi_endhub


  def pickup_demands(pickup_demand_link,multi_depot):
    # multi_depot,multi_endhub=multi_end_and_depot(updated_initial_route_of_delivery)
    demands_multidepot=[]
    demands_multidepot.append(0)
    for i in range(len(multi_depot)):
      demands_multidepot.append(0)
    pickupdemands_list=[]
    dfpd = pd.read_csv(pickup_demand_link)
    pickupdemands_list= dfpd['demand'].to_list()
    for i in pickupdemands_list:
      demands_multidepot.append(i)
    # print(demands_multidepot)
    return demands_multidepot

  def numvech_max_and_vehiclecap(list2):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    num_vehiclemax=len(list2)-1
    vehicle_capacitys=[]
    for i in range(num_vehiclemax):
      vehicle_capacitys.append(640000)
    print(num_vehiclemax,vehicle_capacitys)
    return num_vehiclemax,vehicle_capacitys


  def creating_timewindow_new(pickup_add_link,time_listupdate):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    time_windows_new=[]
    pickup_add=add_pickup(pickup_add_link)
    for i in range(len(time_listupdate)):
      time_windows_new.append((time_listupdate[i],300*60))
    for i in range(len(pickup_add)):
      time_windows_new.append((0,300*60))
    print(time_windows_new)
    return time_windows_new


  def pickup_vrp(time_windows_new,time_matrix2,multi_depot,multi_endhub,demands_multidepot,num_vehiclemax,vehicle_capacitys,time_list4):
    time_limit_seconds = 60 # time limit for calculation
    # time_windows_new=creating_timewindow_new(pickup_add_link,updated_initial_route_of_delivery)
    # time_matrix2=time_matrix(address)
    # multi_depot,multi_endhub=multi_end_and_depot(updated_initial_route_of_delivery)
    # demands_multidepot=pickup_demands(pickup_demand_link,updated_initial_route_of_delivery)
    # num_vehiclemax,vehicle_capacitys=numvech_max_and_vehiclecap(updated_initial_route_of_delivery)
    # time_list4={}
    # [START data_model]
    def create_data_model():
      """Stores the data for the problem."""
    
      data1 = {}
      data1['time_windows'] =time_windows_new
      data1['time_matrix'] = time_matrix2
      # [START starts_ends]
      data1['starts'] =multi_depot
      data1['ends'] =multi_endhub
      data1['num_vehicles']=num_vehiclemax;
      data1['demands']=demands_multidepot
      data1['vehicle_capacities'] =vehicle_capacitys
      # [END starts_ends]
      return data1
      # [END data_model]
      
    # [START solution_printer]
    def print_solution(data1, manager, routing, solution):
      total_distance = 0
      total_load = 0
      time_dimension = routing.GetDimensionOrDie('Time')
      total_time = 0
      time_ss=[]
      for vehicle_id in range(data1['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_load = 0      
        while not routing.IsEnd(index):
          node_index = manager.IndexToNode(index)
          time_var = (time_dimension.CumulVar(index))
          route_load += data1['demands'][node_index]
          plan_output += 'Place {0:>2} Arrive at {2:>2}sec Depart at {3:>2}sec (Load {1:>2})\n'.format(manager.IndexToNode(index),  route_load,solution.Min(time_var),solution.Max(time_var))
          # output_list1.append('{0}'.format(manager.IndexToNode(index)))
          time_ss.append([manager.IndexToNode(index),solution.Max(time_var),route_load])
          previous_index = index
          index = solution.Value(routing.NextVar(index))
        
        time_var = time_dimension.CumulVar(index)
        total_time += solution.Min(time_var)
        plan_output +="Place {0:>2} Arrive at {2:>2}sec \n\n".format(manager.IndexToNode(index), route_load,solution.Min(time_var),solution.Max(time_var))
        plan_output += 'Load of the route: {}\n'.format(route_load)
        plan_output += 'Time of the route: {}sec\n'.format(solution.Min(time_var))
        plan_output += "--------------------"
        time_ss.append([manager.IndexToNode(index),solution.Min(time_var),route_load])
        time_list4[vehicle_id]=time_ss
        time_ss=[]
        
        
        
        # output_list1.append(-1)
        print(plan_output)
        total_load += route_load


      print('Total load of all routes: {}'.format(total_load))
      print('Total time of all routes: {}sec'.format(total_time))
      # [END solution_printer]
    def main4():
      """Entry point of the program."""
      # Instantiate the data problem.
      # [START data]
      data1 = create_data_model()
      # [END data]
      # Create the routing index manager.
      # [START index_manager]
      manager = pywrapcp.RoutingIndexManager(len(data1['time_matrix']),
                                           data1['num_vehicles'], data1['starts'],
                                           data1['ends'])
      # [END index_manager]

      # Create Routing Model.
      # [START routing_model]
      routing = pywrapcp.RoutingModel(manager)

      # [END routing_model]

      # Create and register a transit callback.
      # [START transit_callback]
      def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data1['time_matrix'][from_node][to_node]

      transit_callback_index = routing.RegisterTransitCallback(time_callback)
      routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)#
      
      
      # [END transit_callback]
      # Add Capacity constraint.
      def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data1['demands'][from_node]

      demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
      routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data1['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
      
      # Define cost of each arc.
      # [START arc_cost]
      routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
      # [END arc_cost]

      # Add Distance constraint.
      # [START distance_constraint]
      time = 'Time'
      routing.AddDimension(
        transit_callback_index,
        0,  # allow waiting time
        300*60,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
      time_dimension = routing.GetDimensionOrDie(time)

      for location_idx, time_window in enumerate(data1['time_windows']):
        if location_idx == 0:
          continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        
      # Add time window constraints for each vehicle start node.
      for vehicle_id in range(data1['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data1['time_windows'][0][0],
                                                data1['time_windows'][0][1])

      # Instantiate route start and end times to produce feasible times.
      for i in range(data1['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
  
      # Setting first solution heuristic.
      # [START parameters]
      search_parameters = pywrapcp.DefaultRoutingSearchParameters()
      search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
      search_parameters.time_limit.seconds = time_limit_seconds
      search_parameters.local_search_metaheuristic =(
      routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
      search_parameters.time_limit.seconds = time_limit_seconds
    
      # [END parameters]

      # Solve the problem.
      # [START solve]
      solution = routing.SolveWithParameters(search_parameters)
      # [END solve]

      # Print solution on console.
      # [START print_solution]
      if solution:
        print_solution(data1, manager, routing, solution)
      return solution
    # [END print_solution]
    solution = main4()
    
  # def assigning_value_to_time_list4(pickup_add_link,add,pickup_demand_link,pickup_add):
  #   global time_list4
  #   pickup_vrp(pickup_add_link,add,pickup_demand_link)

  def update_time_list(time_list4,list1):
    
    for key,value in dict(time_list4).items():
      for j in value:
        j[0]=list1[int(j[0])]
    return time_list4


  def update_updated_initial_route_of_delivery(time_list4,updated_initial_route_of_delivery,add,awb,latitude_total,longitude_total):
    # add,awb=merge(pickup_add_link,add,awb)
    # latitude_total,longitude_total=lat_long_pickup(add)
    for key,value in dict(updated_initial_route_of_delivery).items():
      del value[len(value)-1]
    for key,value in dict(time_list4).items():
      del value[0]
      for j in value:
        updated_initial_route_of_delivery[key].append(j)
    for key,value in dict(updated_initial_route_of_delivery).items():
      for j in value:
        j.append(awb[j[0]])
        j.append(add[j[0]])
        j.append(latitude_total[j[0]])
        j.append(longitude_total[j[0]])
    return updated_initial_route_of_delivery
  def create_final_csv(updated_initial_route_of_delivery):
    for key,value in dict(updated_initial_route_of_delivery).items():
      Nodes=[]
      Time=[]
      Load=[]
      Address=[]
      AWB_NO=[]
      latitude=[]
      longitude=[]
      for j in value:
        Nodes.append(j[0])
        Time.append(j[1])
        Load.append(j[2])
        Address.append(j[4])
        AWB_NO.append(j[3])
        latitude.append(j[5])
        longitude.append(j[6])
      final_dict = {'Nodes': Nodes, 'Time': Time, 'Load': Load,'AWB_NO':AWB_NO,'Address':Address,'latitude':latitude,'longitude':longitude}  
      df = pd.DataFrame(final_dict)
      df.to_csv(f'Final_Driver{key}.csv')


  delivery_add=create_delivery_add(add)
  print(delivery_add)
  add,awb=merge(pickup_add_link,add,awb)
  print(add,awb)
  print(len(add))
  
  pickup_add=add_pickup(pickup_add_link)
  print(pickup_add)
  list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
  print(list1)
  print(list2)
  print(time_listupdate)
  address=address(delivery_add,list1)
  print(address)
  latitude_total,longitude_total=lat_long_pickup(add)
  print(latitude_total)
  print(longitude_total)
  list1=appending_list1_forpickup(pickup_add,list1,delivery_add)
  print(list1)
  address=update_address(address,pickup_add)
  print(address)
  latitude_partial,longitude_partial=lat_long_pickup1(address)
  time_matrix2=time_matrix(latitude_partial,longitude_partial)
  print(time_matrix2)
  multi_depot,multi_endhub=multi_end_and_depot(list2)
  print(multi_depot,multi_endhub)
  demands_multidepot=pickup_demands(pickup_demand_link,multi_depot)
  print(demands_multidepot)
  num_vehiclemax,vehicle_capacitys=numvech_max_and_vehiclecap(list2)
  print(num_vehiclemax,vehicle_capacitys)
  time_windows_new=creating_timewindow_new(pickup_add_link,time_listupdate)
  print(time_windows_new)
  time_list4={} 
  pickup_vrp(time_windows_new,time_matrix2,multi_depot,multi_endhub,demands_multidepot,num_vehiclemax,vehicle_capacitys,time_list4)
  print(time_list4)
  time_list4=update_time_list(time_list4,list1)
  print(time_list4)
  updated_initial_route_of_delivery=update_updated_initial_route_of_delivery(time_list4,updated_initial_route_of_delivery,add,awb,latitude_total,longitude_total)
  print(updated_initial_route_of_delivery)
  create_final_csv(updated_initial_route_of_delivery)
  print(updated_initial_route_of_delivery)
  return updated_initial_route_of_delivery,add,awb


def second_pickup(updated_initial_route_of_delivery,add,awb,pickup_add_link,pickup_demand_link,API_KEY):
  # time_list4={}
  

  def create_delivery_add(add):
    delivery_add=[]
    for i in add:
      i=i.replace(" ","+")
      delivery_add.append(i)
    return delivery_add
  # the previous data used 1st pickup (using few functions for 1st pickup)
  # not general
  def merge(pickup_add_link,add,awb):
    merge2add=[]
    merge2awb=[]
    dfp = pd.read_csv(pickup_add_link)
    merge2add= dfp['address'].to_list()
    merge2awb=dfp['AWB'].to_list()
    add=add+merge2add
    awb=awb+merge2awb
    # print(add,awb)
    return add,awb


  


  # general pickup
  def add_pickup(pickup_add_link):
    dfp = pd.read_csv(pickup_add_link)
    pickupadd_list= dfp['address'].to_list()
    for i in range(len(pickupadd_list)):
      pickupadd_list[i]=pickupadd_list[i].replace(" ","+")
    pickup_add=pickupadd_list
    # print(pickup_add)
    return pickup_add 

  #general pickup
  def pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery):
    list1=[]
    list2=[]
    time_listupdate=[]
    load_listupdate=[]
    time_listupdate.append(0)
    load_listupdate.append(0)
    list1.append(0)
    list2.append(0)
    for key,value in dict(updated_initial_route_of_delivery).items():
      for i in range (len(value)):
        if(i==len(value)-2):
          list1.append(value[i][0])
          list2.append(value[i][0])
          time_listupdate.append(value[i][1])
          load_listupdate.append(value[i][2])
    # print(list1,list2,time_listupdate)
    return list1,list2,time_listupdate,load_listupdate


    #general pickup
  def address(delivery_add,list1):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    adresses=[]
    for i in list1:
      adresses.append(delivery_add[int(i)])
    # print(adresses)
    return adresses


  

  #general pickup
  def lat_long_pickup(add):
    latitude_total=[]
    longitude_total=[]
    for i in range(len(add)):
      r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + add[i] +'&key=' + API_KEY)
      resp = json.loads(r.text)
      print(resp)
      lat = resp['results'][0]['geometry']['location']['lat']
      lon = resp['results'][0]['geometry']['location']['lng']
      latitude_total.append(lat)
      longitude_total.append(lon)
      # print(latitude_total,longitude_total)
    return latitude_total,longitude_total

  # #not general pickup
  def appending_list1_forpickup(pickup_add,list1,delivery_add):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    size= len(delivery_add)
    for i in range(len(pickup_add)):
      list1.append(size+i)
    # print(list1)
    return list1
  def update_address(adresses,pickup_add):
    for i in pickup_add:
      adresses.append(i)
    return adresses

  def lat_long_pickup1(adresses):
    latitude_partial=[]
    longitude_partial=[]
    for i in range(len(adresses)):
      r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + add[i] +'&key=' + API_KEY)
      resp = json.loads(r.text)
      lat = resp['results'][0]['geometry']['location']['lat']
      lon = resp['results'][0]['geometry']['location']['lng']
      latitude_partial.append(lat)
      longitude_partial.append(lon)
      # print(latitude_total,longitude_total)
    return latitude_partial,longitude_partial

  def time_calculator(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1
    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2
    dist = 2 * np.arcsin(np.sqrt(haver_formula ))
    m = 6367 * dist *1000
    time=m/6.11
    return int(math.floor(time))

  #general pickup
  def time_matrix(latitude_partial,longitude_partial):
    # def create_time_matrix(latitude_delivery,longitude_delivery):
    time_matrix = np.zeros((len(latitude_partial),len(longitude_partial)))
    for i in range(len(latitude_partial)):
      for j in range(len(longitude_partial)):
        # calculate the distance using the distance matrix function
        time_matrix[i, j] = time_calculator(longitude_partial[i], latitude_partial[i],longitude_partial[j],latitude_partial[j])
    return time_matrix
    
 #general pickup
  def multi_end_and_depot(list2):
  #  list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
   multi_depot=[]
   multi_endhub=[]
   for i in range(1,len(list2)):
     multi_depot.append(i)
   for i in range(len(multi_depot)):
     multi_endhub.append(0)   
  #  print(multi_depot,multi_endhub)
   return multi_depot,multi_endhub


  def pickup_demands(pickup_demand_link,multi_depot,load_listupdate):
    # multi_depot,multi_endhub=multi_end_and_depot(updated_initial_route_of_delivery)
    demands_multidepot=[]
    # demands_multidepot.append(0)
    for i in range(len(multi_depot)+1):
      demands_multidepot.append(load_listupdate[i])
    pickupdemands_list=[]
    dfpd = pd.read_csv(pickup_demand_link)
    pickupdemands_list= dfpd['demand'].to_list()
    for i in pickupdemands_list:
      demands_multidepot.append(i)
    # print(demands_multidepot)
    return demands_multidepot

  def numvech_max_and_vehiclecap(list2):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    num_vehiclemax=len(list2)-1
    vehicle_capacitys=[]
    for i in range(num_vehiclemax):
      vehicle_capacitys.append(640000)
    print(num_vehiclemax,vehicle_capacitys)
    return num_vehiclemax,vehicle_capacitys


  def creating_timewindow_new(pickup_add_link,time_listupdate):
    # list1,list2,time_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
    time_windows_new=[]
    pickup_add=add_pickup(pickup_add_link)
    for i in range(len(time_listupdate)):
      time_windows_new.append((time_listupdate[i],300*60))
    for i in range(len(pickup_add)):
      time_windows_new.append((0,300*60))
    print(time_windows_new)
    return time_windows_new


  def pickup_vrp(time_windows_new,time_matrix2,multi_depot,multi_endhub,demands_multidepot,num_vehiclemax,vehicle_capacitys,time_list4):
    time_limit_seconds = 60 # time limit for calculation
    # time_windows_new=creating_timewindow_new(pickup_add_link,updated_initial_route_of_delivery)
    # time_matrix2=time_matrix(address)
    # multi_depot,multi_endhub=multi_end_and_depot(updated_initial_route_of_delivery)
    # demands_multidepot=pickup_demands(pickup_demand_link,updated_initial_route_of_delivery)
    # num_vehiclemax,vehicle_capacitys=numvech_max_and_vehiclecap(updated_initial_route_of_delivery)
    # time_list4={}
    # [START data_model]
    def create_data_model():
      """Stores the data for the problem."""
    
      data1 = {}
      data1['time_windows'] =time_windows_new
      data1['time_matrix'] = time_matrix2
      # [START starts_ends]
      data1['starts'] =multi_depot
      data1['ends'] =multi_endhub
      data1['num_vehicles']=num_vehiclemax;
      data1['demands']=demands_multidepot
      data1['vehicle_capacities'] =vehicle_capacitys
      # [END starts_ends]
      return data1
      # [END data_model]
      
    # [START solution_printer]
    def print_solution(data1, manager, routing, solution):
      total_distance = 0
      total_load = 0
      time_dimension = routing.GetDimensionOrDie('Time')
      total_time = 0
      time_ss=[]
      for vehicle_id in range(data1['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_load = 0      
        while not routing.IsEnd(index):
          node_index = manager.IndexToNode(index)
          time_var = (time_dimension.CumulVar(index))
          route_load += data1['demands'][node_index]
          plan_output += 'Place {0:>2} Arrive at {2:>2}sec Depart at {3:>2}sec (Load {1:>2})\n'.format(manager.IndexToNode(index),  route_load,solution.Min(time_var),solution.Max(time_var))
          # output_list1.append('{0}'.format(manager.IndexToNode(index)))
          time_ss.append([manager.IndexToNode(index),solution.Max(time_var),route_load])
          previous_index = index
          index = solution.Value(routing.NextVar(index))
        
        time_var = time_dimension.CumulVar(index)
        total_time += solution.Min(time_var)
        plan_output +="Place {0:>2} Arrive at {2:>2}sec \n\n".format(manager.IndexToNode(index), route_load,solution.Min(time_var),solution.Max(time_var))
        plan_output += 'Load of the route: {}\n'.format(route_load)
        plan_output += 'Time of the route: {}sec\n'.format(solution.Min(time_var))
        plan_output += "--------------------"
        time_ss.append([manager.IndexToNode(index),solution.Min(time_var),route_load])
        time_list4[vehicle_id]=time_ss
        time_ss=[]
        
        
        
        # output_list1.append(-1)
        print(plan_output)
        total_load += route_load


      print('Total load of all routes: {}'.format(total_load))
      print('Total time of all routes: {}sec'.format(total_time))
      # [END solution_printer]
    def main4():
      """Entry point of the program."""
      # Instantiate the data problem.
      # [START data]
      data1 = create_data_model()
      # [END data]
      # Create the routing index manager.
      # [START index_manager]
      manager = pywrapcp.RoutingIndexManager(len(data1['time_matrix']),
                                           data1['num_vehicles'], data1['starts'],
                                           data1['ends'])
      # [END index_manager]

      # Create Routing Model.
      # [START routing_model]
      routing = pywrapcp.RoutingModel(manager)

      # [END routing_model]

      # Create and register a transit callback.
      # [START transit_callback]
      def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data1['time_matrix'][from_node][to_node]

      transit_callback_index = routing.RegisterTransitCallback(time_callback)
      routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)#
      
      
      # [END transit_callback]
      # Add Capacity constraint.
      def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data1['demands'][from_node]

      demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
      routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data1['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
      
      # Define cost of each arc.
      # [START arc_cost]
      routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
      # [END arc_cost]

      # Add Distance constraint.
      # [START distance_constraint]
      time = 'Time'
      routing.AddDimension(
        transit_callback_index,
        0,  # allow waiting time
        300*60,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
      time_dimension = routing.GetDimensionOrDie(time)

      for location_idx, time_window in enumerate(data1['time_windows']):
        if location_idx == 0:
          continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        
      # Add time window constraints for each vehicle start node.
      for vehicle_id in range(data1['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data1['time_windows'][0][0],
                                                data1['time_windows'][0][1])

      # Instantiate route start and end times to produce feasible times.
      for i in range(data1['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
  
      # Setting first solution heuristic.
      # [START parameters]
      search_parameters = pywrapcp.DefaultRoutingSearchParameters()
      search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
      search_parameters.time_limit.seconds = time_limit_seconds
      search_parameters.local_search_metaheuristic =(
      routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
      search_parameters.time_limit.seconds = time_limit_seconds
    
      # [END parameters]

      # Solve the problem.
      # [START solve]
      solution = routing.SolveWithParameters(search_parameters)
      # [END solve]

      # Print solution on console.
      # [START print_solution]
      if solution:
        print_solution(data1, manager, routing, solution)
      return solution
    # [END print_solution]
    solution = main4()
    
  # def assigning_value_to_time_list4(pickup_add_link,add,pickup_demand_link,pickup_add):
  #   global time_list4
  #   pickup_vrp(pickup_add_link,add,pickup_demand_link)

  def update_time_list(time_list4,list1):
    
    for key,value in dict(time_list4).items():
      for j in value:
        j[0]=list1[int(j[0])]
    return time_list4


  def update_updated_initial_route_of_delivery(time_list4,updated_initial_route_of_delivery,add,awb,latitude_total,longitude_total):
    # add,awb=merge(pickup_add_link,add,awb)
    # latitude_total,longitude_total=lat_long_pickup(add)
    for key,value in dict(updated_initial_route_of_delivery).items():
      del value[len(value)-1]
    for key,value in dict(time_list4).items():
      del value[0]
      for j in value:
        updated_initial_route_of_delivery[key].append(j)
    for key,value in dict(updated_initial_route_of_delivery).items():
      for j in value:
        j.append(awb[j[0]])
        j.append(add[j[0]])
        j.append(latitude_total[j[0]])
        j.append(longitude_total[j[0]])
    return updated_initial_route_of_delivery
  def create_final_csv(updated_initial_route_of_delivery):
    for key,value in dict(updated_initial_route_of_delivery).items():
      Nodes=[]
      Time=[]
      Load=[]
      Address=[]
      AWB_NO=[]
      latitude=[]
      longitude=[]
      for j in value:
        Nodes.append(j[0])
        Time.append(j[1])
        Load.append(j[2])
        Address.append(j[4])
        AWB_NO.append(j[3])
        latitude.append(j[5])
        longitude.append(j[6])
      final_dict = {'Nodes': Nodes, 'Time': Time, 'Load': Load,'AWB_NO':AWB_NO,'Address':Address,'latitude':latitude,'longitude':longitude}  
      df = pd.DataFrame(final_dict)
      df.to_csv(f'Final_Driver{key}.csv')


  delivery_add=create_delivery_add(add)
  print(delivery_add)
  add,awb=merge(pickup_add_link,add,awb)
  print(add,awb)
  print(len(add))
  
  pickup_add=add_pickup(pickup_add_link)
  print(pickup_add)
  list1,list2,time_listupdate,load_listupdate=pickup_start_takinglast_nodeandtime(updated_initial_route_of_delivery)
  print(list1)
  print(list2)
  print(time_listupdate)
  print(load_listupdate)
  address=address(delivery_add,list1)
  print(address)
  latitude_total,longitude_total=lat_long_pickup(add)
  print(latitude_total)
  print(longitude_total)
  list1=appending_list1_forpickup(pickup_add,list1,delivery_add)
  print(list1)
  address=update_address(address,pickup_add)
  print(address)
  latitude_partial,longitude_partial=lat_long_pickup1(address)
  time_matrix2=time_matrix(latitude_partial,longitude_partial)
  print(time_matrix2)
  multi_depot,multi_endhub=multi_end_and_depot(list2)
  print(multi_depot,multi_endhub)
  demands_multidepot=pickup_demands(pickup_demand_link,multi_depot,load_listupdate)
  print(demands_multidepot)
  num_vehiclemax,vehicle_capacitys=numvech_max_and_vehiclecap(list2)
  print(num_vehiclemax,vehicle_capacitys)
  time_windows_new=creating_timewindow_new(pickup_add_link,time_listupdate)
  print(time_windows_new)
  time_list4={} 
  pickup_vrp(time_windows_new,time_matrix2,multi_depot,multi_endhub,demands_multidepot,num_vehiclemax,vehicle_capacitys,time_list4)
  print(time_list4)
  time_list4=update_time_list(time_list4,list1)
  print(time_list4)
  updated_initial_route_of_delivery=update_updated_initial_route_of_delivery(time_list4,updated_initial_route_of_delivery,add,awb,latitude_total,longitude_total)
  print(updated_initial_route_of_delivery)
  create_final_csv(updated_initial_route_of_delivery)
  print(updated_initial_route_of_delivery)
  return updated_initial_route_of_delivery,add,awb

def main():
    APIKEY="AIzaSyCtfZjJ6cJO1EkdIpDSX_o1CPELWV456Sc"
    initial_route_of_delivery,updated_initial_route_of_delivery,add,awb=delivery("/content/bangalore dispatch address (1).csv",APIKEY)
 
    pickup_demand_link="/content/7_pickup_demand.csv"   
    pickup_add_link="/content/7_pickup.csv"

    updated_initial_route_of_delivery,add,awb=pickup(updated_initial_route_of_delivery,add,awb,pickup_add_link,pickup_demand_link,API_KEY)

    pickup_add_link="/content/pickup2_delivery.csv"
    pickup_demand_link="/content/pickup2_demands.csv"   

    updated_initial_route_of_delivery,add,awb=second_pickup(updated_initial_route_of_delivery,add,awb,pickup_add_link,pickup_demand_link,API_KEY)