import { Download, FileDown, CalendarDays } from "lucide-react";
import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { motion } from "framer-motion";

import { readingsApi } from "../services/api.js";

const containerVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 280, damping: 22 } },
};

export default function ExportPage() {
  const { token, stations } = useOutletContext();
  const [stationId, setStationId] = useState(stations?.[0]?.id || "");
  const [startAt, setStartAt] = useState("");
  const [endAt, setEndAt] = useState("");
  const [isExporting, setIsExporting] = useState(false);

  async function handleExport(e) {
    e.preventDefault();
    if (!stationId) return;

    setIsExporting(true);
    try {
      const startIso = startAt ? new Date(startAt).toISOString() : null;
      const endIso = endAt ? new Date(endAt).toISOString() : null;

      const csv = await readingsApi.historyCsv(token, stationId, startIso, endIso);
      
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      
      const st = stations.find((s) => s.id === Number(stationId));
      const code = st ? st.code.toLowerCase() : "data";
      
      anchor.href = url;
      anchor.download = `${code}_history_${new Date().getTime()}.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export failed:", error);
      alert("Dışa aktarım sırasında bir hata oluştu.");
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="section-stack">
      <motion.div className="page-header" variants={containerVariants} initial="hidden" animate="show">
        <div>
          <h1 className="page-title">Veri İndirme (Export)</h1>
          <p className="page-description">
            Araştırmacılar için geriye dönük sensör ölçümlerini ve modelleri dışa aktarın.
          </p>
        </div>
      </motion.div>

      <motion.div variants={containerVariants} initial="hidden" animate="show" transition={{ delay: 0.1 }}>
        <section className="card" style={{ maxWidth: 640 }}>
          <div className="split" style={{ marginBottom: 24, borderBottom: "1px solid var(--border-soft)", paddingBottom: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ padding: 10, background: "rgba(99,179,237,0.1)", borderRadius: 10, color: "#63b3ed" }}>
                <FileDown size={24} />
              </div>
              <div>
                <h3 className="panel-title">Tarihsel Veri Aktarımı</h3>
                <p className="helper-text" style={{ marginTop: 2 }}>İstasyon ve tarih aralığı belirterek CSV olarak indirin (Maks 2000 kayıt).</p>
              </div>
            </div>
          </div>

          <form onSubmit={handleExport} style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div>
              <label style={{ display: "block", marginBottom: 8, fontSize: "0.9rem", color: "#cbd5e1", fontWeight: 500 }}>
                İstasyon Seçin
              </label>
              <select
                value={stationId}
                onChange={(e) => setStationId(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "var(--bg-tertiary)",
                  border: "1px solid var(--border-soft)",
                  borderRadius: "8px",
                  color: "white",
                  fontSize: "1rem"
                }}
                required
              >
                <option value="" disabled>İstasyon Seçiniz</option>
                {stations.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div>
                <label style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: "0.9rem", color: "#cbd5e1", fontWeight: 500 }}>
                  <CalendarDays size={14} color="#94a3b8" /> Başlangıç Tarihi (İsteğe Bağlı)
                </label>
                <input
                  type="datetime-local"
                  value={startAt}
                  onChange={(e) => setStartAt(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "11px",
                    background: "var(--bg-tertiary)",
                    border: "1px solid var(--border-soft)",
                    borderRadius: "8px",
                    color: "white",
                    fontSize: "0.95rem"
                  }}
                />
              </div>
              <div>
                <label style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, fontSize: "0.9rem", color: "#cbd5e1", fontWeight: 500 }}>
                  <CalendarDays size={14} color="#94a3b8" /> Bitiş Tarihi (İsteğe Bağlı)
                </label>
                <input
                  type="datetime-local"
                  value={endAt}
                  onChange={(e) => setEndAt(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "11px",
                    background: "var(--bg-tertiary)",
                    border: "1px solid var(--border-soft)",
                    borderRadius: "8px",
                    color: "white",
                    fontSize: "0.95rem"
                  }}
                />
              </div>
            </div>

            <div style={{ marginTop: 8 }}>
              <button 
                type="submit" 
                className="button" 
                style={{ width: "100%", padding: "14px", justifyContent: "center", fontSize: "1.05rem", fontWeight: 600 }}
                disabled={isExporting}
              >
                {isExporting ? (
                  <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 16, height: 16, border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
                    Hazırlanıyor...
                  </span>
                ) : (
                  <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Download size={18} /> CSV Dosyasını İndir
                  </span>
                )}
              </button>
            </div>
          </form>
        </section>
      </motion.div>
    </div>
  );
}
