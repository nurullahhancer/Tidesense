import { Thermometer, Waves, Gauge, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { motion } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { readingsApi, sensorApi } from "../services/api.js";
import { formatMetric } from "../utils/formatters.js";

// İstasyona özel renk paleti
const STATION_COLORS = [
  { stroke: "#f97316", fill: "#f97316", gradient: "tempGrad0" }, // İskenderun - turuncu
  { stroke: "#22d3ee", fill: "#22d3ee", gradient: "tempGrad1" }, // İzmir - cyan
  { stroke: "#a78bfa", fill: "#a78bfa", gradient: "tempGrad2" }, // İstanbul - mor
  { stroke: "#34d399", fill: "#34d399", gradient: "tempGrad3" }, // Trabzon - yeşil
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.12 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 280, damping: 22 } },
};

function TrendIcon({ current, prev }) {
  if (!current || !prev) return <Minus size={14} />;
  if (current > prev + 0.5) return <TrendingUp size={14} style={{ color: "#f97316" }} />;
  if (current < prev - 0.5) return <TrendingDown size={14} style={{ color: "#22d3ee" }} />;
  return <Minus size={14} style={{ color: "#94a3b8" }} />;
}

function CustomTooltip({ active, payload, label, color }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#0d1525",
      border: `1px solid ${color}44`,
      borderRadius: 10,
      padding: "8px 14px",
      fontSize: "0.82rem",
    }}>
      <p style={{ margin: "0 0 4px", color: "#64748b" }}>{label}</p>
      <p style={{ margin: 0, color, fontWeight: 700 }}>
        {Number(payload[0]?.value ?? 0).toFixed(1)} °C
      </p>
    </div>
  );
}

function StationTempCard({ station, latestItem, colorCfg, index }) {
  const [history, setHistory] = useState([]);
  const { token } = useOutletContext();

  useEffect(() => {
    if (!station) return;
    readingsApi.history(token, station.id, { hours: 24 }).then((res) => {
      setHistory(res.items ?? []);
    }).catch(() => {});
  }, [token, station?.id]);

  const chartData = history.slice(-24).map((item) => ({
    label: new Date(item.recorded_at).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }),
    temp: Number(item.temperature_c ?? 0),
  }));

  const currentTemp = latestItem?.reading?.temperature_c;
  const prevTemp = chartData.length >= 2 ? chartData[chartData.length - 2]?.temp : null;
  const currentPressure = latestItem?.reading?.air_pressure_hpa;
  const currentWater = latestItem?.reading?.water_level_cm;

  const minTemp = chartData.length ? Math.min(...chartData.map((d) => d.temp)) : null;
  const maxTemp = chartData.length ? Math.max(...chartData.map((d) => d.temp)) : null;

  const { stroke, gradient } = colorCfg;

  return (
    <motion.article
      variants={cardVariants}
      className="card"
      style={{
        overflow: "hidden",
        borderTop: `3px solid ${stroke}`,
        position: "relative",
        padding: 0,
      }}
    >
      {/* Dekoratif arka plan glow */}
      <div style={{
        position: "absolute", top: -40, right: -40,
        width: 140, height: 140, borderRadius: "50%",
        background: `radial-gradient(circle, ${stroke}18, transparent 70%)`,
        pointerEvents: "none",
      }} />

      {/* Kart başlık */}
      <div style={{ padding: "18px 20px 12px", display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
        <div>
          <p style={{ margin: 0, color: "#64748b", fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>
            {station.city || `İstasyon ${index + 1}`}
          </p>
          <h3 style={{ margin: "3px 0 0", color: "var(--text-primary)", fontSize: "1rem", fontWeight: 760 }}>
            {station.name}
          </h3>
          <span style={{ color: "#64748b", fontSize: "0.76rem", display: "none" }}>{station.code}</span>
        </div>
        <div style={{
          width: 42, height: 42, borderRadius: 10,
          background: `linear-gradient(135deg, ${stroke}33, ${stroke}18)`,
          border: `1px solid ${stroke}44`,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: stroke, flexShrink: 0,
        }}>
          <Thermometer size={20} />
        </div>
      </div>

      {/* Ana metrik */}
      <div style={{ padding: "0 20px 14px", display: "flex", alignItems: "baseline", gap: 10 }}>
        <span style={{ fontSize: "2.6rem", fontWeight: 850, color: stroke, lineHeight: 1 }}>
          {formatMetric(currentTemp, 1)}
        </span>
        <span style={{ color: "#64748b", fontSize: "1rem", fontWeight: 700 }}>°C</span>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5, color: "#94a3b8", fontSize: "0.8rem" }}>
          <TrendIcon current={currentTemp} prev={prevTemp} />
          {prevTemp != null ? (
            <span>{currentTemp > prevTemp ? "+" : ""}{(currentTemp - prevTemp).toFixed(1)}°C</span>
          ) : null}
        </div>
      </div>

      {/* Mini grafik */}
      <div style={{ height: 90, padding: "0 0 0 0" }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={gradient} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={stroke} stopOpacity={0.35} />
                <stop offset="95%" stopColor={stroke} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.08)" strokeDasharray="3 3" horizontal={true} vertical={false} />
            <XAxis dataKey="label" hide />
            <YAxis hide domain={["auto", "auto"]} />
            <Tooltip content={(props) => <CustomTooltip {...props} color={stroke} />} />
            <Area
              type="monotone"
              dataKey="temp"
              stroke={stroke}
              strokeWidth={2}
              fill={`url(#${gradient})`}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Alt metrikler */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: 0,
        borderTop: "1px solid var(--border-soft)",
        padding: "12px 20px",
        background: "rgba(148,163,184,0.03)",
      }}>
        {[
          { icon: <Gauge size={13} />, label: "Basınç", value: currentPressure != null ? `${formatMetric(currentPressure, 0)} hPa` : "-" },
          { icon: <Waves size={13} />, label: "Su Seviyesi", value: currentWater != null ? `${formatMetric(currentWater, 1)} cm` : "-" },
          {
            icon: <TrendingUp size={13} />, label: "24s Min/Max",
            value: minTemp != null ? `${minTemp.toFixed(1)} / ${maxTemp.toFixed(1)}°` : "-",
          },
        ].map(({ icon, label, value }) => (
          <div key={label} style={{ display: "flex", flexDirection: "column", gap: 3, alignItems: "center", textAlign: "center" }}>
            <span style={{ color: "#64748b", display: "flex", alignItems: "center", gap: 4, fontSize: "0.72rem" }}>
              {icon} {label}
            </span>
            <strong style={{ color: "var(--text-primary)", fontSize: "0.82rem" }}>{value}</strong>
          </div>
        ))}
      </div>
    </motion.article>
  );
}

export default function TemperaturePage() {
  const { token, stations, latestReadings } = useOutletContext();

  const avgTemp =
    latestReadings.length > 0
      ? (latestReadings.reduce((s, r) => s + (Number(r.reading?.temperature_c) || 0), 0) / latestReadings.length).toFixed(1)
      : null;
  const maxTempStation = latestReadings.reduce(
    (best, r) => (!best || (r.reading?.temperature_c > best.reading?.temperature_c) ? r : best),
    null,
  );

  return (
    <div className="section-stack">
      {/* Başlık */}
      <motion.div className="page-header" initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="page-title">Sıcaklık İzleme</h1>
          <p className="page-description">
            4 kıyı istasyonunun anlık sıcaklık ölçümü ve 24 saatlik eğrisi.
          </p>
        </div>
        {avgTemp && (
          <div style={{
            display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4,
          }}>
            <span style={{ color: "#64748b", fontSize: "0.78rem", fontWeight: 600 }}>Ağırlıklı Ortalama</span>
            <span style={{ fontSize: "1.9rem", fontWeight: 850, color: "#f97316", lineHeight: 1 }}>
              {avgTemp} °C
            </span>
            {maxTempStation && (
              <span style={{ color: "#64748b", fontSize: "0.75rem" }}>
                En yüksek: {maxTempStation.station.name}
              </span>
            )}
          </div>
        )}
      </motion.div>

      {/* 4 istasyon kartı */}
      <motion.div
        className="grid"
        style={{ gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {stations.map((station, idx) => {
          const latestItem = latestReadings.find((r) => r.station.id === station.id);
          return (
            <StationTempCard
              key={station.id}
              station={station}
              latestItem={latestItem}
              colorCfg={STATION_COLORS[idx % STATION_COLORS.length]}
              index={idx}
            />
          );
        })}
      </motion.div>
    </div>
  );
}
