/* global window */
import React, {useState, useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import {Map} from 'react-map-gl';
import maplibregl from 'maplibre-gl';
import {AmbientLight, PointLight, LightingEffect} from '@deck.gl/core';
import DeckGL from '@deck.gl/react';
import {PolygonLayer} from '@deck.gl/layers';
import {TripsLayer} from '@deck.gl/geo-layers';
import {HeatmapLayer} from '@deck.gl/aggregation-layers';


// Source data CSV
const DATA_URL = {
  BUILDINGS:
    'https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/trips/buildings.json', // eslint-disable-line
  TRIPS: 'segmented_routes.json' // eslint-disable-line
};
// TRIPS: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/trips/trips-v7.json' // eslint-disable-line

const ambientLight = new AmbientLight({
  color: [255, 255, 255],
  intensity: 1
});

const pointLight = new PointLight({
  color: [255, 255, 255],
  intensity: 2,
  position: [8.5338278, 47.39784, 8000] //[-74.05, 40.7, 8000]
});

const lightingEffect = new LightingEffect({ambientLight, pointLight});

const material = {
  ambient: 0.1,
  diffuse: 0.6,
  shininess: 32,
  specularColor: [60, 64, 70]
};

const DEFAULT_THEME = {
  buildingColor: [74, 80, 87],
  trailColor0: [138,15,102],
  trailColor1: [33, 150, 243],
  trailColor2: [255, 179, 0],

  material,
  effects: [lightingEffect]
};

const INITIAL_VIEW_STATE = {
  longitude: 8.5338278, //-74,
  latitude: 47.39784,//40.72,
  zoom: 13,
  pitch: 45,
  bearing: 0
};


//'https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json';
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json'
//'https://api.mapbox.com/styles/v1/yoekkul/clqr4prji00y901qw4w2eafb7?access_token=pk.eyJ1IjoieW9la2t1bCIsImEiOiJjazZ6MzIxcm0wN3l1M2RsM3RlZDJxajFwIn0.3hgsJ9re2Y0jAi_sX0_O7Q'

const landCover = [
  [
    [-74.0, 40.7],
    [-74.02, 40.7],
    [-74.02, 40.72],
    [-74.0, 40.72]
  ]
];

function get_frame_time(elapsedSeconds){
  const initialDateTimeObj = new Date('2023-12-26T14:00:00');

  const newDateTime = new Date(initialDateTimeObj.getTime() + elapsedSeconds * 1000);

  // Format the resulting date and time
  const formattedDateTime =
    newDateTime.toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, '');

  return formattedDateTime;
}

export default function App({
  buildings = DATA_URL.BUILDINGS,
  trips = DATA_URL.TRIPS,
  trailLength = 6000,
  initialViewState = INITIAL_VIEW_STATE,
  mapStyle = MAP_STYLE,
  theme = DEFAULT_THEME,
  loopLength = 313232, // unit corresponds to the timestamp in source data
  //animationSpeed = 60
}) {
  const [time, setTime] = useState(0);
  const [animation] = useState({});

  let initialSpeed = 60;
  let initialTime = 0;

  const [animationState, setAnimationState] = useState({
    isPlaying: true,
    animationSpeed: initialSpeed,
    time: initialTime,
  });

  const animate = () => {
    setAnimationState((prevAnimationState) => {
      if(prevAnimationState.isPlaying){
        setTime(t => (t + prevAnimationState.animationSpeed) % loopLength);

      }
      animation.id = window.requestAnimationFrame(animate);
      return prevAnimationState;}
    );
  };
  
  useEffect(() => {
    animation.id = window.requestAnimationFrame(animate);
    return () => window.cancelAnimationFrame(animation.id);
  }, [animation]);

  const layers = [
    // This is only needed when using shadow effects
    new PolygonLayer({
      id: 'ground',
      data: landCover,
      getPolygon: f => f,
      stroked: false,
      getFillColor: [0, 0, 0, 0]
    }),
    new TripsLayer({
      id: 'trips',
      data: trips,
      getPath: d => d.path,
      getTimestamps: d => d.timestamps,
      getColor: d => (d.vendor === 1 ? theme.trailColor0 : d.vendor === 2? theme.trailColor1 : theme.trailColor2),//[138,15,102], //#8a0f66 //getColor: d => (d.vendor === 0 ? theme.trailColor0 : theme.trailColor1),
      opacity: 0.3, //0.3,
      widthMinPixels: 2,
      rounded: true,
      trailLength,
      currentTime: time,

      shadowEnabled: false
    }),
    new PolygonLayer({
      id: 'buildings',
      data: buildings,
      extruded: true,
      wireframe: false,
      opacity: 0.5,
      getPolygon: f => f.polygon,
      getElevation: f => f.height,
      getFillColor: theme.buildingColor,
      material: theme.material
    }),
    // new HeatmapLayer({
    //   id: 'heatmapLayer',
    //   data: trips,
    //   getPosition: d => d.path,
    //   getWeight: 10,
    //   aggregation: 'SUM'
    // })
  ];

  const handlePlayPauseClick = () => {
    setAnimationState((prevState) => ({ ...prevState, isPlaying: !prevState.isPlaying }));
  };

  const setSpeed = (newSpeed) => {
    setAnimationState((prevState) => ({ ...prevState, animationSpeed: newSpeed }));
  };

  return (

    <div>
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '4em', background: '#37474F', zIndex: 3 }}>
        <div style={{ position: 'absolute', top: 5, left: 150, color: 'red'}}>
          
        </div>

        <div style={{ position: 'absolute', top: 10, left: 10 }}>
          <button className={'button-4'} onClick={handlePlayPauseClick}>
            {animationState.isPlaying ? <img src="icons/pause.png" style={{ maxWidth: '1.5em', maxHeight: '1.5em' }} /> : <img src="icons/play.png" style={{ maxWidth: '1.5em', maxHeight: '1.5em' }}/> }
          </button>


          <button className={'button-4'} onClick={(event) => setSpeed(1)} style= {{marginLeft: '8px', height: '3em' }} >
            1x
          </button>
          <button className={'button-4'} onClick={(event) => setSpeed(60)} style= {{marginLeft: '8px', height: '3em' }}>
            60x
          </button>
          <button className={'button-4'} onClick={(event) => setSpeed(1200)} style= {{marginLeft: '8px', height: '3em' }}>
            1200x
          </button>

          <p>Current Time: {get_frame_time(time)}</p>



        </div>
        <div style={{ position: 'absolute', top:'25%', right: 5 }}>
          <a style={{color: 'blue', background: 'yellow', fontSize: '22px'}} href='https://tibaldo.ch'>Info</a>

        </div>

        <input
          type="range"
          min="0"
          max={loopLength}
          step="1"
          value={time}
          onChange={(event) => setTime(parseInt(event.target.value, 10))}
          style={{ position: 'absolute', top: 85, left: 10, width: '280px'}}
        />

      </div>

      <DeckGL
        layers={layers}
        effects={theme.effects}
        initialViewState={initialViewState}
        controller={true}
      >
        <Map reuseMaps mapLib={maplibregl} mapStyle={mapStyle} preventStyleDiffing={true} />

        {/* <input
            type="range"
            min="1"
            max="100"
            step="1"
            value={animationSpeed}
            onChange={(event) => setSpeed(parseInt(event.target.value, 10))}
          /> */}
      </DeckGL>
    </div>
  );
}

export function renderToDOM(container) {
  createRoot(container).render(<App />);
}
