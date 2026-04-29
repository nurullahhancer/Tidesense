import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import AlertPanel from "../components/panels/AlertPanel.jsx";
import { alertsApi } from "../services/api.js";

export default function AlertsPage() {
  const { token, refreshOverview } = useOutletContext();
  const [alerts, setAlerts] = useState([]);

  async function load() {
    const payload = await alertsApi.list(token, { limit: 50 });
    setAlerts(payload.items);
  }

  useEffect(() => {
    load();
  }, [token]);

  async function handleAcknowledge(alertId) {
    await alertsApi.acknowledge(token, alertId);
    await load();
    refreshOverview();
  }

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Alarm Geçmişi</h1>
          <p className="page-description">
            Risk eşiği aşımı durumunda oluşan kayıtlar burada listelenir ve onaylanabilir.
          </p>
        </div>
      </div>
      <AlertPanel alerts={alerts} onAcknowledge={handleAcknowledge} />
    </div>
  );
}
