import {
  Bell,
  Camera,
  Gauge,
  HeartPulse,
  LogOut,
  Map,
  MoonStar,
  ShieldAlert,
  Thermometer,
  UserCog,
  Waves,
  Download,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { roleLabel } from "../../utils/formatters.js";

const navigation = [
  { to: "/dashboard", label: "Risk Durumu", icon: ShieldAlert, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/pressure", label: "Basınç", icon: Gauge, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/temperature", label: "Sıcaklık", icon: Thermometer, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/cameras", label: "Kameralar", icon: Camera, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/moon", label: "Ay Durumu", icon: MoonStar, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/map", label: "Canlı Harita", icon: Map, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/predictions", label: "Tahminler", icon: Waves, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/alerts", label: "Alarm Geçmişi", icon: Bell, roles: ["user", "researcher", "admin", "super_admin"] },
  { to: "/users", label: "Kullanıcılar", icon: UserCog, roles: ["admin", "super_admin"] },
  { to: "/health", label: "Sistem Sağlığı", icon: HeartPulse, roles: ["admin", "super_admin"] },
  { to: "/export", label: "Veri İndir", icon: Download, roles: ["researcher", "admin", "super_admin"] },
];

export default function Sidebar({ user, onLogout, isOpen, onClose }) {
  const items = navigation.filter((item) => item.roles.includes(user.role));

  return (
    <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
      <div className="sidebar__header">
        <div className="brand-title">
          <span className="brand-mark">
            <MoonStar size={22} />
            <span className="brand-mark__flow" />
          </span>
          <div>
            <div>TideSense</div>
            <div className="brand-subtitle">Smart Tide Monitoring</div>
          </div>
        </div>
      </div>

      <nav className="sidebar__nav">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onClose}
            className={({ isActive }) =>
              `nav-link${isActive ? " nav-link--active" : ""}`
            }
          >
            <item.icon size={18} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="split">
          <div className="split">
            <div className="avatar">{user.username[0]?.toUpperCase()}</div>
            <div className="stack" style={{ minWidth: 0 }}>
              <strong style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{user.username}</strong>
              <span className="muted">{roleLabel(user.role)}</span>
            </div>
          </div>
          <button className="button button--ghost" onClick={onLogout}>
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
