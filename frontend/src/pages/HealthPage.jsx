import { Database, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import HealthPanel from "../components/panels/HealthPanel.jsx";
import { healthApi, readingsApi } from "../services/api.js";

export default function HealthPage() {
  const { token, stations } = useOutletContext();
  const [health, setHealth] = useState(null);
  const [externalRows, setExternalRows] = useState([]);

  async function load() {
    const [healthPayload, externalPayload] = await Promise.all([
      healthApi.snapshot(token),
      readingsApi.external(token),
    ]);
    setHealth(healthPayload);
    setExternalRows(externalPayload.items);
  }

  useEffect(() => {
    load();
  }, [token]);

  async function handleRefreshExternal() {
    await readingsApi.external(token, { refresh: "true" });
    load();
  }

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Sistem Durumu</h1>
          <p className="page-description">
            Kayıt merkezi, canlı bağlantılar, yapay zeka ve otomatik görevlerin anlık sağlık durumu.
          </p>
        </div>
      </div>

      <HealthPanel health={health} />

      <section className="card colorful-panel">
        <div className="split" style={{ marginBottom: 18 }}>
          <div>
            <h3 className="panel-title">Son Gelen Veriler</h3>
            <p className="helper-text">Sisteme kaydedilmiş en güncel gerçek ölçümler ve simülasyonlar.</p>
          </div>
          <span className="badge badge--warning">
            <Database size={14} />
            {externalRows.length} kayıt
          </span>
        </div>

        <div className="table-scroll">
          <table className="table">
            <thead>
              <tr>
                <th>İstasyon</th>
                <th>Zaman</th>
                <th>Seviye</th>
                <th>Kaynak</th>
              </tr>
            </thead>
            <tbody>
              {externalRows.slice(0, 12).map((row, index) => (
                <tr key={`${row.station_id}-${row.recorded_at}-${index}`}>
                  <td>
                    <strong>{stations?.find((s) => s.id === row.station_id)?.name || `İstasyon ${row.station_id}`}</strong>
                  </td>
                  <td>{new Date(row.recorded_at).toLocaleString("tr-TR")}</td>
                  <td>{row.water_level_cm} cm</td>
                  <td>{row.raw_payload.mode === 'mock-fallback' ? 'Simülasyon' : row.raw_payload.provider === 'tidecheck' || row.raw_payload.provider === 'noaa' ? 'Gerçek İstasyon' : 'Sistem'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
