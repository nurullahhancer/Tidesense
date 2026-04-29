import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ActivitySquare, AlertTriangle, BellRing, RadioTower } from "lucide-react";

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};
import { useOutletContext } from "react-router-dom";

import AlertPanel from "../components/panels/AlertPanel.jsx";
import SensorCard from "../components/panels/SensorCard.jsx";
import { alertsApi, readingsApi } from "../services/api.js";
import { formatMetric } from "../utils/formatters.js";

export default function DashboardPage() {
  const { token, selectedStation, latestReadings, alerts, refreshOverview } = useOutletContext();

  async function handleAck(alertId) {
    await alertsApi.acknowledge(token, alertId);
    refreshOverview();
  }

  const criticalCount = latestReadings.filter((item) => item.risk_level === "KRITIK").length;
  const warningCount = latestReadings.filter((item) => item.risk_level === "DIKKAT").length;

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Risk ve Canlı Durum</h1>
          <p className="page-description">
            İstasyon kartları gerçek ölçüm, risk seviyesi ve çevresel verileri aynı ekranda gösterir.
          </p>
        </div>
      </div>

      <motion.div className="grid grid--cards" variants={containerVariants} initial="hidden" animate="show">
        <motion.article variants={itemVariants} className="stat-card stat-card--teal">
          <div className="split">
            <ActivitySquare size={18} />
            <strong>Aktif İstasyon</strong>
          </div>
          <div className="metric">{latestReadings.length}</div>
          <p className="helper-text">Dashboard üzerinde izlenen toplam istasyon</p>
        </motion.article>
        <motion.article variants={itemVariants} className="stat-card stat-card--red">
          <div className="split">
            <AlertTriangle size={18} />
            <strong>Kritik Risk</strong>
          </div>
          <div className="metric">{criticalCount}</div>
          <p className="helper-text">150 cm üstü son ölçümler</p>
        </motion.article>
        <motion.article variants={itemVariants} className="stat-card stat-card--amber">
          <div className="split">
            <BellRing size={18} />
            <strong>Dikkat</strong>
          </div>
          <div className="metric">{warningCount}</div>
          <p className="helper-text">120 cm üstü son ölçümler</p>
        </motion.article>
      </motion.div>

      <motion.div className="grid grid--cards" variants={containerVariants} initial="hidden" animate="show">
        {latestReadings.map((item) => (
          <motion.div key={item.station.id} variants={itemVariants}>
            <SensorCard item={item} />
          </motion.div>
        ))}
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, type: "spring", stiffness: 300, damping: 24 }}
      >
        <section className="card">
          <div className="page-header" style={{ marginBottom: 18 }}>
            <div>
              <h3 className="panel-title">Alarm Paneli</h3>
              <p className="helper-text">İlk sekiz alarm kaydı burada canlı güncellenir.</p>
            </div>
          </div>
          <AlertPanel alerts={alerts.slice(0, 8)} onAcknowledge={handleAck} />
        </section>
      </motion.div>
    </div>
  );
}
