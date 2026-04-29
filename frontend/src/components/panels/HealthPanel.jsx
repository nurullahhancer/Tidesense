import { Database, RadioTower, ShieldCheck, Sparkles } from "lucide-react";

export default function HealthPanel({ health }) {
  if (!health) {
    return <div className="empty-state">Sağlık verisi yüklenemedi.</div>;
  }

  const translateStatus = (status) => {
    if (!status) return "";
    const lower = status.toLowerCase();
    if (lower === "healthy" || lower === "connected" || lower === "running" || lower === "active" || lower === "ok") {
      return "Sorunsuz Çalışıyor";
    }
    return status;
  };

  const cards = [
    { 
      icon: Database, 
      title: "Veri Kayıt Merkezi", 
      value: translateStatus(health.database.status), 
      detail: "Ölçümler ve tahminler güvende", 
      tone: "teal" 
    },
    {
      icon: RadioTower,
      title: "Canlı Veri Akışı",
      value: `${health.websocket.active_connections} Cihaz İzliyor`,
      detail: translateStatus(health.websocket.status),
      tone: "blue",
    },
    {
      icon: Sparkles,
      title: "Yapay Zeka Motoru",
      value: translateStatus(health.ml_module.status),
      detail: "Son öğrenilen modeller devrede",
      tone: "violet",
    },
    {
      icon: ShieldCheck,
      title: "Görev Yöneticisi",
      value: translateStatus(health.scheduler.status),
      detail: `${health.scheduler.jobs?.length ?? 0} otomatik kontrol aktif`,
      tone: "amber",
    },
  ];

  return (
    <div className="grid grid--cards">
      {cards.map((item) => (
        <article key={item.title} className={`color-card color-card--${item.tone}`}>
          <div className="split">
            <item.icon size={20} />
            <strong>{item.title}</strong>
          </div>
          <div className="metric" style={{ fontSize: "1.6rem" }}>
            {item.value}
          </div>
          <p className="helper-text">{item.detail}</p>
        </article>
      ))}
    </div>
  );
}
