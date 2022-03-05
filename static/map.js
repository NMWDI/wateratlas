// import * as nmbg_locations from './nmbg_locations.json'

var map = L.map('map',
    {preferCanvas: true}).setView([34.359593, -106.906871], 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

