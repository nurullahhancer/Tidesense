import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle2, ShieldAlert, BellRing } from "lucide-react";

import { formatDateTime } from "../../utils/formatters.js";
import StatusBadge from "../common/StatusBadge.jsx";

const itemVariants = {
  hidden: { opacity: 0, x: -20, scale: 0.95 },
  show: { opacity: 1, x: 0, scale: 1, transition: { type: "spring", stiffness: 300, damping: 24 } },
  exit: { opacity: 0, scale: 0.9, transition: { duration: 0.2 } }
};

export default function AlertPanel({ alerts, onAcknowledge, canAcknowledge = true }) {
  if (!alerts?.length) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        className="empty-state"
        style={{ padding: "40px 20px", display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}
      >
        <CheckCircle2 size={40} color="#10b981" style={{ opacity: 0.8 }} />
        <p style={{ margin: 0, fontSize: "1.1rem", fontWeight: 600, color: "#94a3b8" }}>Tüm sistemler normal</p>
        <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Aktif alarm kaydı bulunmuyor.</span>
      </motion.div>
    );
  }

  return (
    <div className="alert-list" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <AnimatePresence>
        {alerts.map((alert) => {
          const isCritical = alert.severity === "KRITIK";
          const isWarning = alert.severity === "DIKKAT";
          
          let cardStyle = {
            borderLeft: "4px solid var(--border-soft)",
            background: "var(--bg-secondary)",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
          };
          
          let Icon = BellRing;
          let iconColor = "#94a3b8";

          if (isCritical) {
            cardStyle.borderLeft = "4px solid #ef4444";
            cardStyle.background = "linear-gradient(90deg, rgba(239,68,68,0.08) 0%, rgba(30,41,59,0.4) 100%)";
            cardStyle.boxShadow = "0 8px 24px rgba(239,68,68,0.15)";
            cardStyle.border = "1px solid rgba(239,68,68,0.2)";
            Icon = ShieldAlert;
            iconColor = "#ef4444";
          } else if (isWarning) {
            cardStyle.borderLeft = "4px solid #f59e0b";
            cardStyle.background = "linear-gradient(90deg, rgba(245,158,11,0.08) 0%, rgba(30,41,59,0.4) 100%)";
            cardStyle.border = "1px solid rgba(245,158,11,0.2)";
            Icon = AlertTriangle;
            iconColor = "#f59e0b";
          }

          if (alert.is_acknowledged) {
            cardStyle.opacity = 0.7;
            cardStyle.filter = "grayscale(60%)";
            cardStyle.background = "var(--bg-tertiary)";
            cardStyle.boxShadow = "none";
          }

          return (
            <motion.article 
              key={alert.id} 
              className="card"
              variants={itemVariants}
              initial="hidden"
              animate="show"
              exit="exit"
              layout
              style={{
                ...cardStyle,
                padding: "16px",
                position: "relative",
                overflow: "hidden",
                transition: "all 0.3s ease",
              }}
              whileHover={{ scale: 1.01, x: 4 }}
            >
              {/* Dynamic pulse effect for unacknowledged critical alerts */}
              {!alert.is_acknowledged && isCritical && (
                <motion.div
                  animate={{ opacity: [0.1, 0.3, 0.1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  style={{
                    position: "absolute",
                    top: 0, left: 0, right: 0, bottom: 0,
                    background: "radial-gradient(circle at top left, rgba(239,68,68,0.2), transparent 70%)",
                    pointerEvents: "none"
                  }}
                />
              )}

              <div className="split" style={{ alignItems: "flex-start", position: "relative", zIndex: 2 }}>
                <div style={{ display: "flex", gap: "14px", alignItems: "flex-start" }}>
                  <div style={{ 
                    padding: "10px", 
                    borderRadius: "12px", 
                    background: `rgba(${isCritical ? '239,68,68' : isWarning ? '245,158,11' : '148,163,184'}, 0.1)`,
                    color: iconColor
                  }}>
                    <Icon size={22} />
                  </div>
                  <div className="stack" style={{ gap: "4px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <strong style={{ fontSize: "1.05rem", color: "white" }}>{alert.station.name}</strong>
                      {!alert.is_acknowledged && (
                        <span style={{ 
                          width: 8, height: 8, borderRadius: "50%", 
                          background: isCritical ? "#ef4444" : "#f59e0b",
                          boxShadow: `0 0 8px ${isCritical ? "#ef4444" : "#f59e0b"}`
                        }} />
                      )}
                    </div>
                    <span style={{ color: "#cbd5e1", fontSize: "0.9rem", lineHeight: 1.4 }}>{alert.message}</span>
                  </div>
                </div>
                <StatusBadge label={alert.severity} />
              </div>

              <div className="split" style={{ marginTop: 18, position: "relative", zIndex: 2, paddingLeft: "46px" }}>
                <span style={{ color: "#64748b", fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ width: 4, height: 4, borderRadius: "50%", background: "#64748b" }} />
                  {formatDateTime(alert.triggered_at)}
                </span>
                
                {alert.is_acknowledged ? (
                  <span style={{ display: "flex", alignItems: "center", gap: "6px", color: "#10b981", fontSize: "0.85rem", fontWeight: 600 }}>
                    <CheckCircle2 size={16} />
                    Onaylandı
                  </span>
                ) : canAcknowledge ? (
                  <button 
                    className="button button--secondary" 
                    onClick={() => onAcknowledge(alert.id)}
                    style={{ 
                      padding: "6px 14px", 
                      fontSize: "0.85rem",
                      background: isCritical ? "rgba(239,68,68,0.15)" : "rgba(245,158,11,0.15)",
                      color: isCritical ? "#fca5a5" : "#fcd34d",
                      borderColor: isCritical ? "rgba(239,68,68,0.3)" : "rgba(245,158,11,0.3)",
                    }}
                  >
                    Alarmı Kapat
                  </button>
                ) : (
                  <span className="badge badge--warning">Bekliyor</span>
                )}
              </div>
            </motion.article>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
