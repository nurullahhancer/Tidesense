import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute.jsx";
import AlertsPage from "./pages/AlertsPage.jsx";
import CamerasPage from "./pages/CamerasPage.jsx";
import DashboardLayout from "./pages/DashboardLayout.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import HealthPage from "./pages/HealthPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import MapPage from "./pages/MapPage.jsx";
import MoonPage from "./pages/MoonPage.jsx";
import PredictionsPage from "./pages/PredictionsPage.jsx";
import PressurePage from "./pages/PressurePage.jsx";
import TemperaturePage from "./pages/TemperaturePage.jsx";
import UsersPage from "./pages/UsersPage.jsx";
import ExportPage from "./pages/ExportPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/pressure" element={<PressurePage />} />
          <Route path="/temperature" element={<TemperaturePage />} />
          <Route path="/cameras" element={<CamerasPage />} />
          <Route path="/moon" element={<MoonPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route
            path="/predictions"
            element={
              <ProtectedRoute allowedRoles={["user", "researcher", "admin"]}>
                <PredictionsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/health"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <HealthPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/export"
            element={
              <ProtectedRoute allowedRoles={["researcher", "admin"]}>
                <ExportPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <UsersPage />
              </ProtectedRoute>
            }
          />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
