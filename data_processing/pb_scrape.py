import csv
import json
import time
import requests
import pb_station
import pb_bike
# import mapbox_utilities
from datetime import datetime, timedelta
from logger import logger
import os

partner_url = 'https://api.publibike.ch/v1/public/partner/stations/'

stations = pb_station.get_station_dict()


# For each station in data obtained via partner_url we extract the
# parked bikes. We create a dictionary, where each entry (station) 
# contains a set wihth all bikes parked there
def get_and_process_stations_to_idmap(file_path):
    # response = requests.get(partner_url)
    with open(file_path, 'r') as f:
        processed = json.loads(f.read())


        station_map = {}
        for station in processed['data']['stations']:
            parkedVehicles = set()
            for vehicle in station['vehicles']:
                parkedVehicles.add(vehicle['name'])
            station_map[station['id']] = parkedVehicles
        return station_map

class Transit_Information():
    def __init__(self, bike, start_id, start_time):
        self.bike = bike
        self.start_id = start_id
        self.start_time = start_time


# next_update = datetime.now()+timedelta(minutes=1) # now+1 minute
in_transit = {} # TODO make it a 2d list with start time, bike id as axes

directory_path = 'json'
files = sorted(os.listdir(directory_path))
files_paths = []

for file in files:
    file_path = os.path.join(directory_path, file)
    if os.path.isfile(file_path):
        files_paths.append(file_path)

json_trips = []

for i in range(len(files_paths)-1):
    old_status = get_and_process_stations_to_idmap(files_paths[i])
    new_status = get_and_process_stations_to_idmap(files_paths[i+1])

    #FIXME DO THIS BETTER
    with open(files_paths[i+1], 'r') as f:
        processed = json.loads(f.read())
        current_time = processed['date']

    for station_id in stations.keys():
        joined = old_status[station_id] & new_status[station_id]

        departed_join = old_status[station_id]-joined
        if(len(departed_join)>0):
            for bike_id in departed_join:
                in_transit[bike_id]=(Transit_Information(bike_id, station_id, current_time))
                logger.info(f"{bike_id} has just departed")

            # print("---")

        arrived_join = new_status[station_id]-joined


        if(len(arrived_join)>0):
            for bike_id in arrived_join:
                logger.info(f"{bike_id} just arrived")
                if bike_id in in_transit:
                    start_lat = float(stations[in_transit[bike_id].start_id].latitude)
                    start_lon = float(stations[in_transit[bike_id].start_id].longitude)
                    end_lat = float(stations[station_id].latitude)
                    end_lon = float(stations[station_id].longitude)
                    start_time = in_transit[bike_id].start_time #datetime.strptime(in_transit[bike_id].start_time, "%Y%m%d_%H%M%S")
                    end_time = current_time #datetime.strptime(current_time, "%Y%m%d_%H%M%S")
                    # if in_transit[bike].start_id == station_id:
                    #     # print("no trip")
                    #     break #TODO check cases where no trip occurred or instances where trp was too long?
                    # if trip_lat[0]==trip_lat[1] and trip_lon[0]==trip_lon[1]:
                    #     break


                    # route = mapbox_utilities.get_route(start_lat, start_lon, end_lat, end_lon) #FIXME my route

                    #logger.info(f"TRIP COMPLETED from {in_transit[bike_id].start_id} to {station_id} | {end_time-start_time}")
                    in_transit.pop(bike_id)

                    json_trip = {"start_lat":start_lat, "start_lon":start_lon,
                                 "end_lat":end_lat, "end_lon":end_lon,
                                 "start_time":start_time, "end_time":end_time}
                    json_trips.append(json_trip)

                    # TODO save start and end times as well
                    #FIXME write as json file start_time, end_time, start_location, end_location
                    # with open('routes.csv', 'a', newline='') as csvfile:
                    #     writer = csv.writer(csvfile)
                    #     writer.writerow(route)


    logger.info(f"... completed one scraping loop | bikes in transit: {len(in_transit)}")
    # next_update = datetime.now()+timedelta(minutes=1)
    # old_status = new_status
    # new_status = get_and_process_stations_to_idmap()


    #TODO remove slow trips

json_filename = "completed_trips.json"
with open(json_filename, "w") as json_file:
    json.dump(json_trips, json_file, indent=2)


