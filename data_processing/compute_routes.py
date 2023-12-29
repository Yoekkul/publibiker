import json
import osmnx as ox
import networkx as nx
from datetime import datetime, timedelta
from geopy import distance as ds
from tqdm import tqdm

north= 47.48491912973499
south = 47.27592058762251
east= 8.64781718022883
west=8.418490587437761


graph = ox.graph_from_bbox(north, south, east, west, network_type='bike', simplify=True)
initial_time = datetime.strptime("20231226_140001", '%Y%m%d_%H%M%S')


def subdivide_path(path, start_time, end_time):
     # Convert start_time and end_time to datetime objects
    start_datetime = datetime.strptime(start_time, '%Y%m%d_%H%M%S')
    end_datetime = datetime.strptime(end_time, '%Y%m%d_%H%M%S')

    start_datetime = start_datetime-initial_time
    end_datetime = end_datetime-initial_time

    total_time_delta = end_datetime - start_datetime
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += ds.distance(tuple(path[i]), tuple(path[i+1])).meters

    total_speed = total_distance/(total_time_delta+timedelta(seconds=1)).total_seconds()

    json_result = {"vendor":0, "path":[], "timestamps":[]}

    crossed_distance = 0
    current_time = start_datetime

    for i in range(len(path) - 1):
        # Calculate distance between consecutive points
        coords1 = tuple(path[i])
        coords2 = tuple(path[i + 1])
        distance = ds.distance(coords1, coords2).meters

        crossed_distance += distance

        segment_time = int(crossed_distance/total_speed)
        current_time =current_time+timedelta(seconds=segment_time)

        json_result['path'].append([path[i][1], path[i][0]])
        json_result['timestamps'].append(int(current_time.total_seconds()))

    # Add the last point
    # json_result['path'].append([path[-1][0], path[-1][1]])
    # json_result['timestamps'].append(int((end_datetime-initial_time).total_seconds()))

    return json_result

def get_bicycle_route(start_lat_lon, end_lat_lon):
    # Get the nearest nodes to the start and end points
    start_node = ox.distance.nearest_nodes(graph, start_lat_lon[1], start_lat_lon[0])
    end_node = ox.distance.nearest_nodes(graph, end_lat_lon[1], end_lat_lon[0])

    # Find the shortest path using Dijkstra's algorithm
    try:
        route = nx.shortest_path(graph, start_node, end_node, weight='length')
    except:
        return []
    route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]
    return route_coordinates

final_file = "segmented_routes.json"
with open(final_file, "a") as json_file:
    json_file.write("[\n")

# 1. read completed_trips.json
with open("completed_trips.json", 'r') as f:
    processed = json.loads(f.read())

    # total_routes = []

    tmp = 0

    for trip in tqdm(processed):
        # Check if within bounding area:
        if (trip['start_lat'] >= south and trip['start_lat'] <= north and
            trip['end_lat'] >= south and trip['end_lat'] <= north and
            trip['start_lon'] >= west and trip['start_lon'] <= east and
            trip['end_lon'] >= west and trip['end_lon'] <= east):
                
                if(trip["start_time"]==trip["end_time"]): #FIXME get to the root of this issue
                     continue
                
                # print(trip)
                # print(trip['start_lat'])
                # print("accepted")
                route = get_bicycle_route((trip['start_lat'], trip['start_lon']),(trip['end_lat'], trip['end_lon']))
                if len(route)==0:
                    continue
                timed_route = subdivide_path(route, trip['start_time'], trip['end_time'])
                # total_routes.append(timed_route)
                # print(timed_route)
                with open("segmented_routes.json", "a") as json_file:
                    json.dump(timed_route, json_file, indent=2)
                    json_file.write(',\n') 

        #         tmp+=1
        # if tmp == 10:
        #      break


    with open(final_file, "a") as json_file:
        json_file.write('\n]') 

    # json_filename = "segmented_routes.json"
    # with open(json_filename, "w") as json_file:
    #     json.dump(total_routes, json_file, indent=2)
        # break
# 2. check if trip within bounding box
# 3. plot trips

# 4. subdivide trips into time sections