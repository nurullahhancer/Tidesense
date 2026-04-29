import { RefreshCw, Wifi, WifiOff, Moon, Sun } from "lucide-react";

import { roleLabel } from "../../utils/formatters.js";

export default function Topbar({
  user,
  stations,
  selectedStationId,
  onStationChange,
  onRefresh,
  socketStatus,
  theme,
  onToggleTheme,
}) {
  return (
    <header className="topbar">
      <div className="stack">
        <h1 className="page-title" style={{ fontSize: "1.7rem", margin: 0 }}>
          Operasyon Paneli
        </h1>
        <p className="helper-text">
          İstasyon bazlı sensör akışı, tahminler ve alarmlar merkezi olarak izlenir.
        </p>
      </div>

      <div className="topbar__actions">
        <button 
          className="button button--secondary" 
          onClick={onToggleTheme}
          title={theme === "dark" ? "Aydınlık Tema" : "Karanlık Tema"}
        >
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        <div className="stack">
          <span className="muted">{roleLabel(user.role)}</span>
          <div className="split">
            <span
              className={`status-dot status-dot--${
                socketStatus === "online" ? "online" : "offline"
              }`}
            />
            <span>{socketStatus === "online" ? "Canlı akış açık" : "Canlı akış kapalı"}</span>
          </div>
        </div>


        <button className="button button--secondary" onClick={onRefresh}>
          <RefreshCw size={16} />
          Yenile
        </button>

        <span className="badge badge--normal">
          {socketStatus === "online" ? <Wifi size={14} /> : <WifiOff size={14} />}
          {socketStatus === "online" ? "WebSocket aktif" : "Pasif"}
        </span>
      </div>
    </header>
  );
}
