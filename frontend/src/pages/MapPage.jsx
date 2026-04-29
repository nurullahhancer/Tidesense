import { useState } from "react";
import { useOutletContext, useNavigate } from "react-router-dom";
import { Plus, X } from "lucide-react";

import LiveMap from "../components/map/LiveMap.jsx";
import { stationsApi } from "../services/api.js";

export default function MapPage() {
  const { token, user, stations, latestReadings } = useOutletContext();
  const navigate = useNavigate();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCameraPos, setNewCameraPos] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    city: "",
    snapshot_url: "",
  });

  const handleMapClick = (latlng) => {
    if (user?.role === "admin") {
      setNewCameraPos(latlng);
      setIsModalOpen(true);
      setFormData({
        name: "",
        code: `ST_${Math.floor(Math.random() * 10000)}`,
        city: "",
        snapshot_url: "https://picsum.photos/seed/new-camera/960/540",
      });
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newCameraPos) return;
    try {
      await stationsApi.create(token, {
        name: formData.name,
        code: formData.code,
        city: formData.city,
        latitude: newCameraPos.lat,
        longitude: newCameraPos.lng,
        snapshot_url: formData.snapshot_url,
      });
      setIsModalOpen(false);
      setNewCameraPos(null);
      // Başarılı olduktan sonra kameralar sayfasına veya dashboard'a yönlendirilebilir, 
      // ama sadece sayfayı yenilemek de yeterli (App.jsx fetch ediyor).
      window.location.reload(); 
    } catch (err) {
      alert("Hata: " + err.message);
    }
  };

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Canlı Harita</h1>
          <p className="page-description">
            Leaflet tabanlı istasyon haritasında marker seçildiğinde son ölçüm ve risk popup içinde görünür.
            {user?.role === "admin" && " Admin olarak boş bir yere tıklayarak yeni istasyon ekleyebilirsiniz."}
          </p>
        </div>
      </div>

      <LiveMap stations={stations} latestReadings={latestReadings} onMapClick={handleMapClick} />

      {isModalOpen && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999
        }}>
          <div className="card" style={{ width: "400px", padding: "24px", position: "relative" }}>
            <button
              onClick={() => setIsModalOpen(false)}
              style={{ position: "absolute", top: "16px", right: "16px", background: "transparent", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}
            >
              <X size={20} />
            </button>
            <h3 style={{ margin: "0 0 16px", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "8px" }}>
              <Plus size={18} /> Haritadan Yeni İstasyon Ekle
            </h3>
            
            <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>
                  Tıklanan Koordinatlar
                </label>
                <div style={{ fontSize: "0.85rem", color: "var(--text-primary)", background: "var(--bg-primary)", padding: "8px 12px", borderRadius: "6px" }}>
                  {newCameraPos?.lat.toFixed(4)}, {newCameraPos?.lng.toFixed(4)}
                </div>
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>İstasyon Kodu</label>
                <input required type="text" value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>İstasyon Adı</label>
                <input required type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>Şehir</label>
                <input required type="text" value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>Kamera Görüntü URL (Opsiyonel)</label>
                <input type="url" value={formData.snapshot_url} onChange={(e) => setFormData({ ...formData, snapshot_url: e.target.value })} style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <button type="submit" style={{ marginTop: "8px", padding: "10px", borderRadius: "6px", border: "none", background: "var(--accent-primary)", color: "white", fontWeight: "600", cursor: "pointer" }}>Kaydet ve Ekle</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
