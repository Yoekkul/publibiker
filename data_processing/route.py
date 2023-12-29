#%%
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

def get_graph():
    padding = 0.1
    north, south, east, west = (
        max(start_lat_lon[0], end_lat_lon[0]) + padding,
        min(start_lat_lon[0], end_lat_lon[0]) - padding,
        max(start_lat_lon[1], end_lat_lon[1]) + padding,
        min(start_lat_lon[1], end_lat_lon[1]) - padding
    )
    print(north, south, east, west)
    graph = ox.graph_from_bbox(north, south, east, west, network_type='all', simplify=True)
    return graph




# Example usage
start_lat_lon = (47.38491912973499, 8.547817180228831) 
end_lat_lon = (47.37592058762251, 8.51849058743776) 


graph = get_graph()

#%%
import osmnx.distance as oxd
start_lat_lon = (47.38491, 8.54781) 
end_lat_lon =   (47.37592, 8.51849) 


def get_bicycle_route(start_lat_lon, end_lat_lon, graph):
    # Get the bicycle network for the given bounding box
    


    # Get the nearest nodes to the start and end points
    start_node = oxd.nearest_nodes(graph, start_lat_lon[1], start_lat_lon[0])

    end_node = oxd.nearest_nodes(graph, end_lat_lon[1], end_lat_lon[0])


    print("Started routing")
    # Find the shortest path using Dijkstra's algorithm
    route = nx.shortest_path(graph, start_node, end_node, weight='length')

    length = nx.shortest_path_length(graph, start_node, end_node, weight='length')

    # Calculate total distance and time estimation
    #total_distance = sum(ox.utils_graph.route_to_gdf(graph, route, 'length'))
    #total_time = total_distance / 15.0  # Assuming an average speed of 15 km/h

    # Get the route coordinates
    print(route)
    print(length)
    route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]

    print("--")
    fig, ax = ox.plot_graph_route(graph, route,bgcolor='w', node_color='#999999', edge_color='#999999', node_size=0)
    print("ST", start_node)
    print(graph.nodes[start_node]['x'], graph.nodes[start_node]['y'])
    print(start_lat_lon[1], start_lat_lon[0])
    print("--")


    return route_coordinates #, total_time, total_distance

route= get_bicycle_route(start_lat_lon, end_lat_lon, graph)

print("Route Coordinates:", route)
# %%
from datetime import datetime
from geopy import distance as ds



initial_time = datetime.strptime("20231226_022935", '%Y%m%d_%H%M%S')


def subdivide_path(path, start_time, end_time, time_step):
    result = []

    # Convert start_time and end_time to datetime objects
    start_datetime = datetime.strptime(start_time, '%Y%m%d_%H%M%S')
    end_datetime = datetime.strptime(end_time, '%Y%m%d_%H%M%S')

    total_time_delta = end_datetime - start_datetime
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += ds.distance(tuple(path[i]), tuple(path[i+1])).meters

    total_speed = total_distance/total_time_delta.total_seconds()

    json_result = {"vendor":0, "path":[], "timestamps":[]}

    crossed_distance = 0

    for i in range(len(path) - 1):
        # Calculate distance between consecutive points
        coords1 = tuple(path[i])
        coords2 = tuple(path[i + 1])
        distance = ds.distance(coords1, coords2).meters

        crossed_distance += distance

        segment_time = int(crossed_distance/total_speed)

        # print(coords1, coords2, distance)

        # # Calculate time needed to traverse the distance based on the average speed
        # speed = distance / total_time_delta.total_seconds()
        # time_needed = distance / speed

        # # Calculate the number of segments for the given time step
        # num_segments = int(time_needed / time_step) + 1

        # # Calculate the time step for each segment
        # segment_time_step = total_time_delta / num_segments

        # Subdivide the segment and add to the result
        # num_segments #FIXME
        for j in range(1):
            # segment_time = start_datetime + j * segment_time_step
            # (segment_time-initial_time).total_seconds()//60
            json_result['path'].append([path[i][0], path[i][1]])
            json_result['timestamps'].append(segment_time)# segment_time.strftime('%Y-%m-%d %H:%M:%S'))
            # result.append({
            #     'point': path[i],
            #     'time': segment_time.strftime('%Y-%m-%d %H:%M:%S')
            # })

    # Add the last point
    # json_result['path'].append([path[-1][0], path[-1][1]])
    
    # json_result['timestamps'].append(int((end_datetime-initial_time).total_seconds()))
    # result.append({
    #     'point': path[-1],
    #     'time': end_time
    # })

    return json_result


{"vendor":0, "path":[[8.20986, 47.81773], [8.20986, 47.81773]], "timestamps":[1191, 1195]}
start_time = "20231226_102935"
end_time = "20231226_112935"

subdivide_path(route, start_time, end_time, 10)