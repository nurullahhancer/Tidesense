import { Compass, MoonStar, Orbit } from "lucide-react";
import { motion } from "framer-motion";

import { formatMetric } from "../../utils/formatters.js";

const containerVariants = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 300, damping: 24, staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  show: { opacity: 1, scale: 1, transition: { type: "spring", stiffness: 300, damping: 20 } }
};

export default function MoonStatus({ moon }) {
  if (!moon) {
    return <div className="empty-state">Ay verisi yüklenemedi.</div>;
  }

  const illuminationPercent = Math.round(moon.moon_illumination * 100);
  const glowOpacity = Math.max(0.15, moon.moon_illumination * 0.4);
  const phaseName = moon.moon_phase?.toLowerCase() ?? "";
  const isWaning = phaseName.includes("waning") || phaseName.includes("last");
  const shadeWidth = `${Math.max(0, Math.min(100, (1 - moon.moon_illumination) * 100))}%`;
  const shadeSide = isWaning ? { right: 0 } : { left: 0 };
  const markerRotation = Number.isFinite(moon.azimuth) ? moon.azimuth : 0;
  const altitudeOffset = Number.isFinite(moon.altitude)
    ? Math.max(-20, Math.min(20, moon.altitude / 3))
    : 0;

  return (
    <motion.section
      className="card card--highlight moon-panel"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <div className="moon-panel__layout">
        <div className="moon-panel__copy">
          <h3 className="panel-title">Ay Konumu</h3>
          <motion.div variants={itemVariants} className="moon-phase-name">
            <MoonStar size={30} />
            <span>{moon.moon_phase}</span>
          </motion.div>
          <p className="metric-subtext moon-panel__summary">
            Aydınlanma oranı %{formatMetric(illuminationPercent, 0)}
          </p>
        </div>

        <div className="moon-scene" aria-hidden="true">
          <motion.div
            className="moon-scene__aura"
            animate={{ opacity: [glowOpacity, glowOpacity * 1.7, glowOpacity] }}
            transition={{ duration: 4.8, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="moon-orbit"
            animate={{ rotate: [markerRotation, markerRotation + 360] }}
            transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
          >
            <span className="moon-orbit__marker" />
          </motion.div>
          <motion.div
            className="moon-disc"
            animate={{ y: [altitudeOffset - 4, altitudeOffset + 4, altitudeOffset - 4], rotate: [-1.5, 1.5, -1.5] }}
            transition={{ duration: 6.5, repeat: Infinity, ease: "easeInOut" }}
          >
            <span className="moon-disc__crater moon-disc__crater--one" />
            <span className="moon-disc__crater moon-disc__crater--two" />
            <span className="moon-disc__crater moon-disc__crater--three" />
            <span
              className="moon-disc__shade"
              style={{ width: shadeWidth, ...shadeSide }}
            />
            <span
              className="moon-disc__terminator"
              style={isWaning ? { right: shadeWidth } : { left: shadeWidth }}
            />
          </motion.div>
          <span className="moon-star moon-star--one" />
          <span className="moon-star moon-star--two" />
          <span className="moon-star moon-star--three" />
        </div>
      </div>

      <div className="grid grid--three moon-metrics">
        <motion.div variants={itemVariants} className="card" whileHover={{ scale: 1.05, background: "rgba(148,163,184,0.08)" }}>
          <div className="split">
            <Orbit size={18} color="#94a3b8" />
            <strong style={{ fontSize: "1.1rem" }}>{formatMetric(moon.gravity_factor, 3)}x</strong>
          </div>
          <p className="helper-text" style={{ marginTop: 4 }}>Yerçekimi (Gravity)</p>
        </motion.div>

        <motion.div variants={itemVariants} className="card" whileHover={{ scale: 1.05, background: "rgba(148,163,184,0.08)" }}>
          <div className="split">
            <Compass size={18} color="#94a3b8" />
            <strong style={{ fontSize: "1.1rem" }}>{formatMetric(moon.altitude)}°</strong>
          </div>
          <p className="helper-text" style={{ marginTop: 4 }}>İrtifa (Altitude)</p>
        </motion.div>

        <motion.div variants={itemVariants} className="card" whileHover={{ scale: 1.05, background: "rgba(148,163,184,0.08)" }}>
          <div className="split">
            <Compass size={18} color="#94a3b8" />
            <strong style={{ fontSize: "1.1rem" }}>{formatMetric(moon.azimuth)}°</strong>
          </div>
          <p className="helper-text" style={{ marginTop: 4 }}>Azimut (Azimuth)</p>
        </motion.div>
      </div>
    </motion.section>
  );
}
