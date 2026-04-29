import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer, useMapEvents } from "react-leaflet";

import { formatMetric } from "../../utils/formatters.js";
import StatusBadge from "../common/StatusBadge.jsx";

const makeIcon = (riskLevel) =>
  L.divIcon({
    className: "",
    html: `
      <div style="
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: ${riskLevel === "KRITIK" ? "#f97316" : riskLevel === "DIKKAT" ? "#facc15" : "#4da2ff"};
        box-shadow: 0 0 0 6px rgba(77,162,255,0.15);
        border: 2px solid #081222;
      "></div>
    `,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

function MapEventHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      if (onMapClick) onMapClick(e.latlng);
    },
  });
  return null;
}

export default function LiveMap({ stations, latestReadings, onMapClick }) {
  return (
    <div className="map-shell">
      <MapContainer
        center={[39.0, 35.0]}
        zoom={6}
        style={{ width: "100%", height: "100%" }}
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; OpenStreetMap &copy; CARTO'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {stations.map((station) => {
          const reading = latestReadings.find((item) => item.station.id === station.id);
          return (
            <Marker
              key={station.id}
              position={[station.latitude, station.longitude]}
              icon={makeIcon(reading?.risk_level)}
            >
              <Popup>
                <div style={{ minWidth: 180 }}>
                  <strong>{station.name}</strong>
                  <p style={{ margin: "8px 0", color: "#64748b" }}>{station.city}</p>
                  <p style={{ margin: "6px 0" }}>
                    Su seviyesi: {formatMetric(reading?.reading?.water_level_cm)} cm
                  </p>
                  <p style={{ margin: "6px 0" }}>
                    Basınç: {formatMetric(reading?.reading?.air_pressure_hpa)} hPa
                  </p>
                  <div style={{ marginTop: 10 }}>
                    <StatusBadge label={reading?.risk_level ?? "NORMAL"} />
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
        <MapEventHandler onMapClick={onMapClick} />
      </MapContainer>
    </div>
  );
}
