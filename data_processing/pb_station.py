import requests
import json

class Station():
    def __init__(self, id, latitude, longitude):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude



stations_url = 'https://api.publibike.ch/v1/public/stations/'
def get_station_dict():
    response = requests.get(stations_url)
    station_json = json.loads(response.text)
    stations = {}
    for station in station_json:
        stations[station["id"]] = Station(
            station["id"], 
            station["latitude"],
            station["longitude"],)
    
    return stations