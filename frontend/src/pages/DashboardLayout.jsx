import { Outlet } from "react-router-dom";
import { useEffect, useState } from "react";

import Sidebar from "../components/layout/Sidebar.jsx";
import Topbar from "../components/layout/Topbar.jsx";
import { useAuth } from "../contexts/AuthContext.jsx";
import { useLiveSocket } from "../hooks/useLiveSocket.js";
import { alertsApi, sensorApi, stationsApi } from "../services/api.js";

export default function DashboardLayout() {
  const { token, user, logout } = useAuth();
  const [stations, setStations] = useState([]);
  const [selectedStationId, setSelectedStationId] = useState(null);
  const [latestReadings, setLatestReadings] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  async function refreshOverview() {
    if (!token) return;
    setIsRefreshing(true);
    try {
      const [stationsResponse, latestResponse, alertsResponse] = await Promise.all([
        stationsApi.list(token),
        sensorApi.latest(token),
        alertsApi.list(token, { limit: 8 }),
      ]);
      setStations(stationsResponse.items);
      setLatestReadings(latestResponse.items);
      setAlerts(alertsResponse.items);
      if (!selectedStationId && stationsResponse.items.length) {
        setSelectedStationId(stationsResponse.items[0].id);
      }
    } finally {
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    refreshOverview();
  }, [token]);

  const socketStatus = useLiveSocket({
    token,
    enabled: Boolean(token),
    onMessage(event) {
      if (event.type === "reading") {
        setLatestReadings((current) =>
          current.map((item) =>
            item.station.id === event.payload.station_id
              ? {
                  ...item,
                  risk_level: event.payload.risk_level,
                  reading: {
                    ...item.reading,
                    station_id: event.payload.station_id,
                    recorded_at: event.payload.recorded_at,
                    water_level_cm: event.payload.water_level_cm,
                    air_pressure_hpa: event.payload.air_pressure_hpa,
                    temperature_c: event.payload.temperature_c,
                    data_source: "mqtt",
                  },
                }
              : item,
          ),
        );
      }
      if (event.type === "alert") {
        setAlerts((current) => [
          {
            id: Math.random(),
            station: stations.find((station) => station.id === event.payload.station_id) ?? {
              id: event.payload.station_id,
              name: `Station ${event.payload.station_id}`,
            },
            severity: event.payload.severity,
            message: event.payload.message,
            triggered_at: event.payload.triggered_at,
            is_acknowledged: false,
          },
          ...current,
        ]);
      }
    },
  });

  const selectedStation =
    stations.find((station) => station.id === selectedStationId) ?? stations[0] ?? null;

  return (
    <div className="page-shell">
      <Sidebar user={user} onLogout={logout} />

      <main className="main-content">
        <Topbar
          user={user}
          stations={stations}
          selectedStationId={selectedStationId}
          onStationChange={setSelectedStationId}
          onRefresh={refreshOverview}
          socketStatus={socketStatus}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        <div className="content-panel">
          <Outlet
            context={{
              user,
              token,
              stations,
              selectedStation,
              selectedStationId,
              latestReadings,
              alerts,
              refreshOverview,
              socketStatus,
              isRefreshing,
              theme,
              toggleTheme,
            }}
          />
        </div>
      </main>
    </div>
  );
}
