
Post describing project can also be found at [my personal blog](https://tibaldo.ch/web/2024/01/01/publibike-movement-tracking.html)

### What is Publibike
[PubliBike](https://www.publibike.ch/en/home) is a Swiss bike-sharing service, providing access to classical and electric bikes in multiple cities around Switzerland. Bikes are borrowed and returned at fixed locations. When bikes are returned they can be locked in the proximity of the stations. Data about the status of the stations is freely available [online](https://api.publibike.ch/v1/static/api.html).

This project focuses on visualizing the paths taken by bikes in the city of Zurich, around new year 2023/2024. Purple bikes are non-assisted, while blue bikes are electric.

![Preview of publiBike visualization](/assets/images/publibike_post/publibike-website.gif)


### How does the code work:
This project can be subdivided into three main modules:
1. Obtaining data from the public API
2. Processing data, estimating taken routes
3. Visualizing data

**1. Obtaining data**
This step can be accomplished by periodically fetching the status of all stations from the public PubliBike API. The JSON formatted data is saved into a new file and then passed on to the processing stage

Sample of the data:
```
{
  "id": 568,
  "latitude": 47.347701,
  "longitude": 8.528049,
  "state": {
    "id": 1,
    "name": "Active"
  },
  "name": "Jugendherberge",
  "address": "Mutschellenstrasse 114",
  "zip": "8038",
  "city": "Zürich",
  "vehicles": [
    {
      "id": 3371,
      "name": "501245",
      "ebike_battery_level": 50,
      "type": {
        "id": 2,
        "name": "E-Bike"
      }
    },
    {
      "id": 2822,
      "name": "501002",
      "ebike_battery_level": 87,
      "type": {
        "id": 2,
        "name": "E-Bike"
      }
    },
    ...
  ],
  "network": {
    "id": 6,
    "name": "Zürich",
    "background_img": null,
    "logo_img": "https://www.publibike.ch/static-content/Netz6.svg",
    "sponsors": []
  },
  "sponsors": [],
  "is_virtual_station": true,
  "capacity": 22
}
```

**2. Processsing data**
We now have a list of files, corresponding to the status of the stations for each minute. By comparing two consecutive files we can identify when bikes leave a station and arrive to a new one. By thus keeping track of bikes that are in transit we are able to extract the beginning and end location as well as the time of departure/arrival. This information is then saved in a temporary file. 

```
  {
    "start_lat": 46.023159,
    "start_lon": 8.959919,
    "end_lat": 46.023159,
    "end_lon": 8.959919,
    "start_time": "20231226_140101",
    "end_time": "20231226_140201",
    "bike_type": 1 # 1=classic bike, 2=electric bike
  },
  ...
```

We now take this file and filter the data within such that we only keep entries which fit in the Zurcih area bounding box. After this is done we obtain the road network of the city from Open Street Map. Having this information we can now estimate a shortest path between two stations and take this as a guess for the taken path. As a final step we need to estimate a timestamp for each intersection in the path. This will help us in creating a smooth animation. This process is done by linearly interpolating the time from the start location to the end location, based on the distance.

```
[
  {
    "vendor": 1, # Used to identify the bike type
    "path": [
      [
        8.5338278,
        47.39784
      ],
      [
        8.5340274,
        47.3978924
      ],
      [
        8.5342179,
        47.3981905
      ],
      [
        8.534199,
        47.3983042
      ],
        ...
    ],
    "timestamps": [
      64155,
      64202,
      64261,
      64376,
        ...
    ]
  },
  ...
]
```

**3. Visualizing data**
Having now a formatted Json file containing trip locations and times we can make use of the [Deck.gl]() javascript framework. More specifically I use the [TripsLayer](https://deck.gl/docs/api-reference/geo-layers/trips-layer), which allows me to animate the trips, given a JSON file and a time interval.

---
### F.A.Q.
* **Can the bike position be tracked during a ride?**
No! The track the bike follows is only an estimate. Only the start point, end point, start time and end time can be publicly accessed. Using this information I find the shortest path between the two PubliBike stations and use that to visualize the taken path.
* **Where was the data obtained?**
PubliBike offers a publicly visible API, if you are curious you can check it out here! [PubliBike API](https://api.publibike.ch/v1/static/api.html).
For this project I call this API once every minute, and save the results for further processing.
* **Where can I find the code for this project?**
The code can be found in my personal [GitHub repository](https://github.com/Yoekkul/publibiker)


### Notes

https://deck.gl/docs/api-reference/geo-layers/trips-layer
https://ckochis.com/deck-gl-time-frame-animations
https://www.cityjson.org/datasets/#simple-geometries

```npm start```