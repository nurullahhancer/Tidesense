import { Gauge, Thermometer, Waves, TrendingUp, TrendingDown, Minus, BarChart2 } from "lucide-react";
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
  ReferenceLine,
} from "recharts";

import { readingsApi } from "../services/api.js";
import { formatMetric } from "../utils/formatters.js";

// Normal atmosfer basıncı referansı
const NORMAL_PRESSURE = 1013.25;

// İstasyona özel renk paleti (basınç için mavi/yeşil tonları)
const STATION_COLORS = [
  { stroke: "#38bdf8", gradient: "presGrad0" }, // İskenderun - açık mavi
  { stroke: "#818cf8", gradient: "presGrad1" }, // İzmir - indigo
  { stroke: "#2dd4bf", gradient: "presGrad2" }, // İstanbul - teal
  { stroke: "#60a5fa", gradient: "presGrad3" }, // Trabzon - mavi
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.12 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 280, damping: 22 } },
};

// Basıncın normale göre durumu
function pressureStatus(hpa) {
  if (!hpa) return { label: "-", color: "#64748b" };
  if (hpa > 1020) return { label: "Yüksek", color: "#f97316" };
  if (hpa < 1000) return { label: "Düşük", color: "#a78bfa" };
  return { label: "Normal", color: "#22d3ee" };
}

function TrendIcon({ current, prev }) {
  if (!current || !prev) return <Minus size={14} />;
  if (current > prev + 0.5) return <TrendingUp size={14} style={{ color: "#f97316" }} />;
  if (current < prev - 0.5) return <TrendingDown size={14} style={{ color: "#818cf8" }} />;
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
        {Number(payload[0]?.value ?? 0).toFixed(1)} hPa
      </p>
    </div>
  );
}

function StationPressureCard({ station, latestItem, colorCfg, index }) {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const { token } = useOutletContext();

  useEffect(() => {
    if (!station) return;
    Promise.all([
      readingsApi.history(token, station.id, { hours: 24 }),
      readingsApi.stats(token, station.id, 48),
    ]).then(([histRes, statRes]) => {
      setHistory(histRes.items ?? []);
      setStats(statRes);
    }).catch(() => {});
  }, [token, station?.id]);

  const chartData = history.slice(-24).map((item) => ({
    label: new Date(item.recorded_at).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }),
    pressure: Number(item.air_pressure_hpa ?? 0),
  }));

  const currentPressure = latestItem?.reading?.air_pressure_hpa;
  const prevPressure = chartData.length >= 2 ? chartData[chartData.length - 2]?.pressure : null;
  const currentTemp = latestItem?.reading?.temperature_c;
  const currentWater = latestItem?.reading?.water_level_cm;

  const minP = chartData.length ? Math.min(...chartData.map((d) => d.pressure)) : null;
  const maxP = chartData.length ? Math.max(...chartData.map((d) => d.pressure)) : null;
  const status = pressureStatus(currentPressure);

  const { stroke, gradient } = colorCfg;
  const diff = currentPressure && prevPressure ? (currentPressure - prevPressure).toFixed(1) : null;

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
      {/* Dekoratif glow */}
      <div style={{
        position: "absolute", top: -40, right: -40,
        width: 140, height: 140, borderRadius: "50%",
        background: `radial-gradient(circle, ${stroke}18, transparent 70%)`,
        pointerEvents: "none",
      }} />

      {/* Kart başlık */}
      <div style={{ padding: "18px 20px 10px", display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
        <div>
          <p style={{ margin: 0, color: "#64748b", fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>
            {station.city || `İstasyon ${index + 1}`}
          </p>
          <h3 style={{ margin: "3px 0 0", color: "var(--text-primary)", fontSize: "1rem", fontWeight: 760 }}>
            {station.name}
          </h3>
          <span style={{ color: "#64748b", fontSize: "0.76rem", display: "none" }}>{station.code}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <div style={{
            width: 42, height: 42, borderRadius: 10,
            background: `linear-gradient(135deg, ${stroke}33, ${stroke}18)`,
            border: `1px solid ${stroke}44`,
            display: "flex", alignItems: "center", justifyContent: "center",
            color: stroke,
          }}>
            <Gauge size={20} />
          </div>
          <span style={{
            fontSize: "0.68rem", fontWeight: 800, textTransform: "uppercase",
            color: status.color,
            background: `${status.color}18`,
            border: `1px solid ${status.color}44`,
            borderRadius: 999, padding: "2px 8px",
          }}>
            {status.label}
          </span>
        </div>
      </div>

      {/* Ana metrik */}
      <div style={{ padding: "0 20px 12px", display: "flex", alignItems: "baseline", gap: 10 }}>
        <span style={{ fontSize: "2.6rem", fontWeight: 850, color: stroke, lineHeight: 1 }}>
          {formatMetric(currentPressure, 1)}
        </span>
        <span style={{ color: "#64748b", fontSize: "1rem", fontWeight: 700 }}>hPa</span>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5, color: "#94a3b8", fontSize: "0.8rem" }}>
          <TrendIcon current={currentPressure} prev={prevPressure} />
          {diff !== null && (
            <span>{currentPressure > prevPressure ? "+" : ""}{diff} hPa</span>
          )}
        </div>
      </div>

      {/* Normal referans göstergesi */}
      {currentPressure && (
        <div style={{ padding: "0 20px 10px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "#64748b", marginBottom: 4 }}>
            <span>Normale göre fark</span>
            <span style={{ color: status.color, fontWeight: 700 }}>
              {(currentPressure - NORMAL_PRESSURE) > 0 ? "+" : ""}
              {(currentPressure - NORMAL_PRESSURE).toFixed(1)} hPa
            </span>
          </div>
          <div style={{ height: 6, borderRadius: 999, background: "rgba(148,163,184,0.12)", overflow: "hidden" }}>
            <div style={{
              height: "100%",
              width: `${Math.min(Math.abs((currentPressure - NORMAL_PRESSURE) / 30) * 100, 100)}%`,
              background: `linear-gradient(90deg, ${stroke}, ${stroke}aa)`,
              borderRadius: 999,
              transition: "width 0.5s ease",
              marginLeft: currentPressure < NORMAL_PRESSURE ? 0 : undefined,
            }} />
          </div>
        </div>
      )}

      {/* Mini grafik */}
      <div style={{ height: 80 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={gradient} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={stroke} stopOpacity={0.3} />
                <stop offset="95%" stopColor={stroke} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.08)" strokeDasharray="3 3" horizontal vertical={false} />
            <XAxis dataKey="label" hide />
            <YAxis hide domain={["auto", "auto"]} />
            <ReferenceLine y={NORMAL_PRESSURE} stroke="rgba(148,163,184,0.3)" strokeDasharray="3 3" />
            <Tooltip content={(props) => <CustomTooltip {...props} color={stroke} />} />
            <Area type="monotone" dataKey="pressure" stroke={stroke} strokeWidth={2}
              fill={`url(#${gradient})`} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Alt metrikler */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        borderTop: "1px solid var(--border-soft)",
        padding: "12px 20px",
        background: "rgba(148,163,184,0.03)",
      }}>
        {[
          { icon: <Thermometer size={13} />, label: "Sıcaklık", value: currentTemp != null ? `${formatMetric(currentTemp, 1)} °C` : "-" },
          { icon: <Waves size={13} />, label: "Su Seviyesi", value: currentWater != null ? `${formatMetric(currentWater, 1)} cm` : "-" },
          { icon: <BarChart2 size={13} />, label: "24s Min/Max", value: minP != null ? `${minP.toFixed(0)} / ${maxP.toFixed(0)}` : "-" },
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

export default function PressurePage() {
  const { token, stations, latestReadings } = useOutletContext();

  const avgPressure =
    latestReadings.length > 0
      ? (latestReadings.reduce((s, r) => s + (Number(r.reading?.air_pressure_hpa) || 0), 0) / latestReadings.length).toFixed(1)
      : null;

  const highPressureCount = latestReadings.filter((r) => (r.reading?.air_pressure_hpa ?? 0) > 1020).length;
  const lowPressureCount = latestReadings.filter((r) => (r.reading?.air_pressure_hpa ?? 0) < 1000).length;

  return (
    <div className="section-stack">
      {/* Başlık */}
      <motion.div className="page-header" initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1 className="page-title">Basınç İzleme</h1>
          <p className="page-description">
            4 kıyı istasyonunun anlık atmosferik basınç ölçümü ve 24 saatlik eğrisi.
          </p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          {avgPressure && (
            <>
              <span style={{ color: "#64748b", fontSize: "0.78rem", fontWeight: 600 }}>Ortalama Basınç</span>
              <span style={{ fontSize: "1.9rem", fontWeight: 850, color: "#38bdf8", lineHeight: 1 }}>
                {avgPressure} <span style={{ fontSize: "1rem" }}>hPa</span>
              </span>
            </>
          )}
          <div style={{ display: "flex", gap: 8 }}>
            {highPressureCount > 0 && (
              <span style={{ fontSize: "0.72rem", color: "#f97316", background: "#f9731618", border: "1px solid #f9731644", borderRadius: 999, padding: "2px 8px" }}>
                {highPressureCount} Yüksek
              </span>
            )}
            {lowPressureCount > 0 && (
              <span style={{ fontSize: "0.72rem", color: "#a78bfa", background: "#a78bfa18", border: "1px solid #a78bfa44", borderRadius: 999, padding: "2px 8px" }}>
                {lowPressureCount} Düşük
              </span>
            )}
          </div>
        </div>
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
            <StationPressureCard
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
