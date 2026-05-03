import { Wifi, WifiOff, Moon, Sun, Menu, Waves } from "lucide-react";

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
  onToggleSidebar,
}) {
  return (
    <header className="topbar">
      <div className="topbar__brand-mobile">
        <button className="button button--ghost mobile-only" onClick={onToggleSidebar}>
          <Menu size={20} />
        </button>
        <div className="brand-flow brand-flow--mobile">
          <span className="brand-flow__mark">
            <Moon size={16} />
            <span className="brand-flow__wave brand-flow__wave--one" />
            <span className="brand-flow__wave brand-flow__wave--two" />
          </span>
          <strong>TideSense</strong>
        </div>
      </div>

      <div className="topbar__identity desktop-only">
        <div className="brand-flow">
          <span className="brand-flow__mark">
            <Moon size={18} />
            <span className="brand-flow__wave brand-flow__wave--one" />
            <span className="brand-flow__wave brand-flow__wave--two" />
          </span>
          <div>
            <div className="brand-flow__title">
              <span>TideSense</span>
              <strong>Operasyon Paneli</strong>
            </div>
            <p className="brand-flow__subtitle">
              Sensör akışı, tahminler ve alarmlar canlı izlenir.
            </p>
          </div>
        </div>
      </div>

      <div className="topbar__actions">
        <button 
          className="button button--secondary" 
          onClick={onToggleTheme}
          title={theme === "dark" ? "Aydınlık Tema" : "Karanlık Tema"}
        >
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        <div className="live-status-card desktop-only">
          <div className="live-status-card__role">{roleLabel(user.role)}</div>
          <div className="live-status-card__state">
            <span
              className={`status-dot status-dot--${
                socketStatus === "online" ? "online" : "offline"
              }`}
            />
            <Waves size={14} />
            <span>{socketStatus === "online" ? "Canlı akış açık" : "Canlı akış kapalı"}</span>
          </div>
        </div>


        <span className="badge badge--normal desktop-only">
          {socketStatus === "online" ? <Wifi size={14} /> : <WifiOff size={14} />}
          {socketStatus === "online" ? "WebSocket aktif" : "Pasif"}
        </span>
      </div>
    </header>
  );
}
