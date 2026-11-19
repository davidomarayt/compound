const explorer = (() => {
  const el = id => document.getElementById(id);
  const places = {'Dublin':[53.3498,-6.2603],'Kells':[53.727,-6.879],'Cork':[51.8985,-8.4756],'Galway':[53.2707,-9.0568],'Limerick':[52.6638,-8.6267],'Waterford':[52.2593,-7.1101],'Athlone':[53.4239,-7.9407],'Sligo':[54.2697,-8.4694],'Letterkenny':[54.9558,-7.7343]};
  function setup(change,zoom) {
    const map=L.map('explorer-map',{maxBounds:[[50.9,-11.4],[56,-4.8]],maxBoundsViscosity:1,scrollWheelZoom:false,minZoom:6,maxZoom:19}).setView(places.Dublin,zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',maxZoom:19}).addTo(map);
    const pin=L.circleMarker(places.Dublin,{radius:7,color:'white',weight:3,fillColor:'#172d37',fillOpacity:1,pane:'markerPane',interactive:false}).addTo(map);
    const picker=el('place');
    for(const name of Object.keys(places))picker.add(new Option(name,name));
    picker.add(new Option('Custom pin','custom'));picker.lastElementChild.disabled=true;
    function move(point){pin.setLatLng(point);change(pin.getLatLng());}
    map.on('click',event=>{if(!L.latLngBounds([51.3,-10.8],[55.5,-5.3]).contains(event.latlng))return;picker.value='custom';move(event.latlng);});
    picker.onchange=()=>{const point=places[picker.value];map.setView(point,zoom);move(point);};
    return {map,pin};
  }
  return {el,setup};
})();
