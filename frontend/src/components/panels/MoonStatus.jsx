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

  // Calculate moon glow intensity based on illumination
  const glowOpacity = Math.max(0.15, moon.moon_illumination * 0.4);

  return (
    <motion.section 
      className="card card--highlight" 
      variants={containerVariants}
      initial="hidden"
      animate="show"
      style={{ overflow: "hidden", position: "relative" }}
    >
      {/* Background ambient glow */}
      <motion.div 
        animate={{ opacity: [glowOpacity * 0.6, glowOpacity * 1.2, glowOpacity * 0.6] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        style={{
          position: "absolute",
          top: "-20%", right: "-10%",
          width: "250px", height: "250px",
          background: "radial-gradient(circle, rgba(167,139,250,0.4) 0%, transparent 70%)",
          filter: "blur(40px)",
          pointerEvents: "none",
          zIndex: 0
        }}
      />

      <div className="split" style={{ position: "relative", zIndex: 1 }}>
        <div>
          <p className="muted" style={{ margin: 0 }}>
            {moon.station_name}
          </p>
          <h3 className="panel-title">Ay Konumu</h3>
        </div>
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          style={{ 
            padding: 12, 
            background: "rgba(167,139,250,0.15)", 
            borderRadius: "50%",
            color: "#c4b5fd",
            boxShadow: `0 0 20px rgba(167,139,250,${glowOpacity})`
          }}
        >
          <MoonStar size={32} />
        </motion.div>
      </div>

      <motion.div variants={itemVariants} style={{ position: "relative", zIndex: 1, marginTop: "8px" }}>
        <div 
          className="metric" 
          style={{ 
            fontSize: "2.4rem", 
            background: "linear-gradient(90deg, #e2e8f0, #94a3b8)", 
            WebkitBackgroundClip: "text", 
            WebkitTextFillColor: "transparent" 
          }}
        >
          {moon.moon_phase}
        </div>
        <p className="metric-subtext" style={{ color: "#a78bfa", fontWeight: 600 }}>
          Aydınlanma oranı %{formatMetric(moon.moon_illumination * 100, 1)}
        </p>
      </motion.div>

      <div className="grid grid--three" style={{ marginTop: 24, position: "relative", zIndex: 1 }}>
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
