console.log("Loading CSS files");
// CSS dependencies
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
console.log("CSS loaded, moving on to JS");

// Main JavaScript loads dependencies
console.log("Attempting weird reexport of jquery");
import $ from 'jquery';
console.log("Didn't explode from jquery");
var leaflet = require('leaflet');
var marker_cluster = require('leaflet.markercluster');
console.log("Loaded leaflet and marker-cluster");
