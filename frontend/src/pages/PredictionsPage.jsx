import { Download, RefreshCw, TrendingUp, Target, Activity, BarChart2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ComposedChart,
  Line,
  Bar,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

import { predictionApi, readingsApi } from "../services/api.js";
import { formatMetric } from "../utils/formatters.js";

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 280, damping: 22 } },
};

// Özel Tooltip
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#0d1525",
      border: "1px solid rgba(99,179,237,0.22)",
      borderRadius: 12,
      padding: "10px 16px",
      fontSize: "0.84rem",
      minWidth: 160,
      boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
    }}>
      <p style={{ margin: "0 0 6px", color: "#94a3b8", fontWeight: 700 }}>{label}</p>
      {payload.map((entry) => (
        <div key={entry.dataKey} style={{ display: "flex", justifyContent: "space-between", gap: 16, color: entry.color }}>
          <span>{entry.name}</span>
          <strong>{entry.value != null ? `${Number(entry.value).toFixed(1)} cm` : "-"}</strong>
        </div>
      ))}
    </div>
  );
}

// Risk seviyesi badge
function riskBadge(value) {
  if (value === null || value === undefined) return <span className="badge badge--offline">-</span>;
  if (value >= 150) return <span className="badge badge--critical">KRİTİK</span>;
  if (value >= 120) return <span className="badge badge--warning">DİKKAT</span>;
  return <span className="badge badge--normal">NORMAL</span>;
}

// Güven skoru rengi
function confidenceColor(score) {
  if (!score) return "#94a3b8";
  if (score >= 0.8) return "#22d3ee";
  if (score >= 0.6) return "#f59e0b";
  return "#ef4444";
}

export default function PredictionsPage() {
  const { token, stations, user } = useOutletContext();
  const [localStation, setLocalStation] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (stations?.length > 0 && !localStation) {
      setLocalStation(stations[0]);
    }
  }, [stations, localStation]);

  async function load(refresh = false) {
    if (!localStation) return;
    setLoading(true);
    try {
      const [predictionPayload, historyPayload] = await Promise.all([
        predictionApi.list(token, {
          station_id: localStation.id,
          ...(refresh ? { refresh: "true" } : {}),
        }),
        readingsApi.external(token, { station_id: localStation.id, limit: 24 }),
      ]);
      setPredictions(predictionPayload.items[0] ?? null);
      setHistory([...(historyPayload.items ?? [])].reverse());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(false);
  }, [token, localStation]);

  async function handleExport() {
    if (!localStation) return;
    const csv = await readingsApi.historyCsv(token, localStation.id);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${localStation.code.toLowerCase()}_history.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  // Gerçek veri — son 12 saat
  const actualPoints = history.slice(-12).map((item) => ({
    label: new Date(item.recorded_at).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }),
    actual: Number(item.water_level_cm),
    time: new Date(item.recorded_at),
  }));

  // Tahmin verisi — sonraki 24 saat
  const predPoints = (predictions?.items ?? []).slice(0, 24).map((item) => ({
    label: new Date(item.prediction_time).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }),
    predicted: Number(item.predicted_water_level_cm),
    confidence: Number(item.confidence_score ?? 0),
    time: new Date(item.prediction_time),
  }));

  // Grafik için birleştir — overlap noktası: son actual = predicted'ın başlangıcı
  const lastActual = actualPoints[actualPoints.length - 1];
  const chartData = [
    ...actualPoints.map((a, i) => {
      if (i === actualPoints.length - 1) {
        return { ...a, predicted: a.actual }; // Connect the lines
      }
      return a;
    }),
    ...predPoints.map((p) => ({
      ...p,
      actual: undefined,
    })),
  ];

  // Son gerçek seviye
  const lastActualVal = lastActual?.actual ?? null;
  // İlk tahmin
  const firstPredVal = predPoints[0]?.predicted ?? null;
  // Ortalama tahmin farkı
  const avgPred = predPoints.length
    ? predPoints.reduce((s, p) => s + p.predicted, 0) / predPoints.length
    : null;
  const rmse = predictions?.rmse ?? null;

  // Tablo verisi — sadece tahmin saatleri
  const tableData = predPoints.slice(0, 24);

  return (
    <div className="section-stack">
      {/* Başlık */}
      <motion.div
        className="page-header"
        variants={itemVariants}
        initial="hidden"
        animate="show"
      >
        <div>
          <h1 className="page-title">Tahmin Analizi</h1>
          <p className="page-description">
            Farklı coğrafi konumlardaki limanların ML tahminlerini inceleyin.
          </p>
        </div>
        <div className="inline-actions">
          {user?.role !== "user" && (
            <button className="button button--secondary" onClick={() => load(true)} disabled={loading}>
              <RefreshCw size={16} style={loading ? { animation: "spin 1s linear infinite" } : {}} />
              {loading ? "Yükleniyor..." : "Tahmini Yenile"}
            </button>
          )}
          {user?.role !== "user" && (
            <button className="button button--ghost" onClick={handleExport}>
              <Download size={16} />
              CSV Dışa Aktar
            </button>
          )}
        </div>
      </motion.div>

      {/* İstasyon Seçici Tablar */}
      <motion.div variants={itemVariants} initial="hidden" animate="show" style={{ display: "flex", gap: "8px", marginBottom: "16px", overflowX: "auto", paddingBottom: "4px" }}>
        {stations.map((station) => (
          <button
            key={station.id}
            onClick={() => setLocalStation(station)}
            style={{
              padding: "10px 18px",
              borderRadius: "8px",
              border: "1px solid",
              borderColor: localStation?.id === station.id ? "var(--accent-primary)" : "var(--border-soft)",
              background: localStation?.id === station.id ? "rgba(99,179,237,0.15)" : "var(--bg-secondary)",
              color: localStation?.id === station.id ? "var(--text-primary)" : "var(--text-secondary)",
              fontWeight: localStation?.id === station.id ? 700 : 500,
              cursor: "pointer",
              transition: "all 0.2s ease",
              whiteSpace: "nowrap"
            }}
          >
            {station.name}
          </button>
        ))}
      </motion.div>

      {/* Özet kartlar */}
      <motion.div
        className="grid grid--cards"
        initial="hidden"
        animate="show"
        variants={{ hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } }}
      >
        {[
          {
            icon: <Activity size={18} />,
            label: "Son Gerçek Seviye",
            value: lastActualVal != null ? `${formatMetric(lastActualVal)} cm` : "-",
            sub: "Ölçüm kaynağı: Sensör",
            color: "stat-card--teal",
          },
          {
            icon: <TrendingUp size={18} />,
            label: "İlk Tahmin",
            value: firstPredVal != null ? `${formatMetric(firstPredVal)} cm` : "-",
            sub: "Bir sonraki saatin öngörüsü",
            color: "stat-card--violet",
          },
          {
            icon: <Target size={18} />,
            label: "Ortalama Hata Payı",
            value: rmse != null ? `± ${formatMetric(rmse, 2)} cm` : "-",
            sub: "Geçmiş verilere göre sapma",
            color: rmse && rmse > 15 ? "stat-card--red" : "stat-card--amber",
          },
        ].map(({ icon, label, value, sub, color }) => (
          <motion.article key={label} variants={itemVariants} className={`stat-card ${color}`}>
            <div className="split">{icon}<strong style={{ fontSize: "0.82rem" }}>{label}</strong></div>
            <div className="metric" style={{ fontSize: "1.5rem", marginTop: 8 }}>{value}</div>
            <p className="helper-text">{sub}</p>
          </motion.article>
        ))}
      </motion.div>

      {/* Karşılaştırmalı Grafik */}
      <motion.section
        className="card"
        variants={itemVariants}
        initial="hidden"
        animate="show"
        transition={{ delay: 0.25 }}
      >
        <div className="split" style={{ marginBottom: 16 }}>
          <div>
          <h3 className="panel-title">Geçmiş Ölçüm + 24 Saatlik Tahmin</h3>
          <p className="helper-text">
            <span style={{ color: "#4da2ff", fontWeight: 700 }}>●</span> Son 12 saatin gerçek sensör verisi
            &nbsp;&nbsp;→&nbsp;&nbsp;
            <span style={{ color: "#a78bfa", fontWeight: 700 }}>●</span> Önümüzdeki 24 saatin ML tahmini
          </p>
        </div>
          {rmse && (
            <span
              className={`badge ${rmse > 15 ? "badge--critical" : rmse > 8 ? "badge--warning" : "badge--normal"}`}
            >
              RMSE: {formatMetric(rmse, 2)} cm
            </span>
          )}
        </div>
        <div className="chart-shell" style={{ height: 340 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ left: 0, right: 12 }}>
              <defs>
                <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4da2ff" stopOpacity={0.28} />
                  <stop offset="95%" stopColor="#4da2ff" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="predGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.24} />
                  <stop offset="95%" stopColor="#a78bfa" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(148,163,184,0.1)" strokeDasharray="4 4" />
              <XAxis dataKey="label" stroke="#64748b" tick={{ fontSize: 11 }} interval="preserveStartEnd" minTickGap={20} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} unit=" cm" width={62} domain={['auto', 'auto']} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => (
                  <span style={{ color: "#94a3b8", fontSize: "0.82rem" }}>{value}</span>
                )}
              />
              <Area
                type="monotone"
                dataKey="actual"
                name="Gerçek Veri"
                stroke="#4da2ff"
                strokeWidth={2.5}
                fill="url(#actualGrad)"
                dot={false}
                connectNulls={false}
              />
              <Area
                type="monotone"
                dataKey="predicted"
                name="Tahmin"
                stroke="#a78bfa"
                strokeWidth={2.5}
                strokeDasharray="6 3"
                fill="url(#predGrad)"
                dot={false}
                connectNulls={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </motion.section>

      {/* Tahmin Tablosu */}
      <motion.section
        className="card"
        variants={itemVariants}
        initial="hidden"
        animate="show"
        transition={{ delay: 0.35 }}
      >
        <div className="split" style={{ marginBottom: 16 }}>
          <div>
          <h3 className="panel-title">Önümüzdeki 24 Saat — ML Tahmin Tablosu</h3>
            <p className="helper-text">Tahmin saati, öngörülen seviye, güven skoru ve risk durumu.</p>
          </div>
        </div>
        {tableData.length === 0 ? (
          <div className="empty-state">Tahmin verisi bulunamadı.</div>
        ) : (
          <div className="table-scroll">
            <table className="table" style={{ minWidth: 640 }}>
              <thead>
                <tr style={{ background: "rgba(99,179,237,0.06)" }}>
                  <th style={{ color: "#94a3b8" }}>#</th>
                  <th style={{ color: "#94a3b8" }}>Tahmin Saati</th>
                  <th style={{ color: "#94a3b8" }}>Tahmini Seviye</th>
                  <th style={{ color: "#94a3b8" }}>Güven Skoru</th>
                  <th style={{ color: "#94a3b8" }}>Risk Durumu</th>
                  <th style={{ color: "#94a3b8" }}>Görsel Bar</th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, i) => (
                  <tr
                    key={i}
                    style={{
                      background: i % 2 === 0 ? "transparent" : "rgba(148,163,184,0.04)",
                      transition: "background 0.15s",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(99,179,237,0.07)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = i % 2 === 0 ? "transparent" : "rgba(148,163,184,0.04)")}
                  >
                    <td style={{ color: "#64748b", fontSize: "0.8rem" }}>{i + 1}</td>
                    <td style={{ fontWeight: 600 }}>
                      {new Date(row.time).toLocaleString("tr-TR", {
                        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
                      })}
                    </td>
                    <td>
                      <span style={{ fontWeight: 800, fontSize: "1.1rem", color: "#a78bfa" }}>
                        {formatMetric(row.predicted, 1)}
                      </span>
                      <span style={{ color: "#64748b", marginLeft: 4, fontSize: "0.8rem" }}>cm</span>
                      {rmse != null && (
                        <div style={{ fontSize: "0.75rem", color: "#f59e0b", marginTop: "2px" }}>
                          (± {formatMetric(rmse, 1)} cm hata payı)
                        </div>
                      )}
                    </td>
                    <td>
                      <span style={{ color: confidenceColor(row.confidence), fontWeight: 700 }}>
                        {row.confidence ? `%${(row.confidence * 100).toFixed(0)}` : "-"}
                      </span>
                    </td>
                    <td>{riskBadge(row.predicted)}</td>
                    <td style={{ minWidth: 120 }}>
                      <div style={{
                        height: 8, borderRadius: 999,
                        background: "rgba(148,163,184,0.12)",
                        overflow: "hidden",
                      }}>
                        <div style={{
                          height: "100%",
                          width: `${Math.min((row.predicted / 200) * 100, 100)}%`,
                          background: row.predicted >= 150
                            ? "linear-gradient(90deg,#ef4444,#f97316)"
                            : row.predicted >= 120
                              ? "linear-gradient(90deg,#f59e0b,#fbbf24)"
                              : "linear-gradient(90deg,#22d3ee,#a78bfa)",
                          borderRadius: 999,
                          transition: "width 0.5s ease",
                        }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.section>
    </div>
  );
}
