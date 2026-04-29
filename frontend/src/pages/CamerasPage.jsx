import { Camera, Plus, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import CameraView from "../components/panels/CameraView.jsx";
import { cameraApi, stationsApi } from "../services/api.js";

export default function CamerasPage() {
  const { token, user } = useOutletContext();
  const [cameras, setCameras] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    city: "",
    latitude: "",
    longitude: "",
    snapshot_url: "",
  });

  const load = async () => {
    try {
      const payload = await cameraApi.list(token);
      setCameras(payload.items);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    load();
  }, [token]);

  const handleOpenModal = () => {
    setIsModalOpen(true);
    setFormData({
      name: "",
      code: `ST_${Math.floor(Math.random() * 10000)}`,
      city: "",
      latitude: "",
      longitude: "",
      snapshot_url: "https://picsum.photos/seed/new-camera/960/540",
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await stationsApi.create(token, {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
      });
      setIsModalOpen(false);
      load(); // Refresh cameras list
    } catch (err) {
      alert("Hata: " + err.message);
    }
  };

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Canlı Kameralar</h1>
          <p className="page-description">
            Sisteme kayıtlı tüm istasyonların kamera görüntüleri.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <span className="badge badge--critical">
            <Camera size={14} />
            {cameras.length} Kamera
          </span>
          {user?.role === "admin" && (
            <button 
              onClick={handleOpenModal} 
              style={{ 
                padding: "6px 14px", 
                fontSize: "0.85rem", 
                display: "flex", 
                alignItems: "center", 
                gap: "6px", 
                background: "var(--accent-primary)", 
                color: "white", 
                border: "none", 
                borderRadius: "6px", 
                cursor: "pointer",
                fontWeight: 600
              }}
            >
              <Plus size={16} /> Yeni Ekle
            </button>
          )}
        </div>
      </div>

      <div className="camera-grid" style={{ marginTop: "12px" }}>
        {cameras.map((camera) => (
          <CameraView key={camera.station.id} camera={camera} />
        ))}
      </div>

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
              <Plus size={18} /> Yeni Kamera Ekle
            </h3>
            
            <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div style={{ display: "flex", gap: "12px" }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>Enlem (Lat)</label>
                  <input required type="number" step="any" value={formData.latitude} onChange={(e) => setFormData({ ...formData, latitude: e.target.value })} style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>Boylam (Lng)</label>
                  <input required type="number" step="any" value={formData.longitude} onChange={(e) => setFormData({ ...formData, longitude: e.target.value })} style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
                </div>
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>İstasyon Kodu</label>
                <input required type="text" value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>İstasyon Adı</label>
                <input required type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>Şehir</label>
                <input required type="text" value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "4px" }}>Kamera Snapshot URL</label>
                <input type="url" value={formData.snapshot_url} onChange={(e) => setFormData({ ...formData, snapshot_url: e.target.value })} style={{ width: "100%", padding: "8px", borderRadius: "6px", border: "1px solid var(--border-soft)", background: "var(--bg-primary)", color: "var(--text-primary)" }} />
              </div>
              <button type="submit" style={{ marginTop: "8px", padding: "10px", borderRadius: "6px", border: "none", background: "var(--accent-primary)", color: "white", fontWeight: "600", cursor: "pointer" }}>Kaydet ve Ekle</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
