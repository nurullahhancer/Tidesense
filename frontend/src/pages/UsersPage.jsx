import {
  Activity,
  Clock,
  Globe2,
  Info,
  KeyRound,
  MonitorSmartphone,
  Network,
  ShieldCheck,
  Trash2,
  UserPlus,
  Users,
} from "lucide-react";
import { Fragment, useCallback, useEffect, useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { usersApi } from "../services/api.js";
import { formatDateTime, roleLabel } from "../utils/formatters.js";

const ALL_ROLES = ["user", "researcher", "admin", "super_admin"];
const MANAGEABLE_ROLES = ["user", "researcher", "admin"];

function deviceValue(value, fallback = "Henüz kayıt yok") {
  return value || fallback;
}

function UserDeviceDetails({ userItem }) {
  const detailItems = [
    {
      label: "Cihaz",
      value: deviceValue(userItem.last_login_device),
      icon: MonitorSmartphone,
    },
    {
      label: "İşletim sistemi",
      value: deviceValue(userItem.last_login_os),
      icon: MonitorSmartphone,
    },
    {
      label: "Tarayıcı",
      value: deviceValue(userItem.last_login_browser),
      icon: Globe2,
    },
    {
      label: "IP adresi",
      value: deviceValue(userItem.last_login_ip),
      icon: Network,
    },
    {
      label: "Son giriş",
      value: userItem.last_login_at ? formatDateTime(userItem.last_login_at) : "Henüz kayıt yok",
      icon: Clock,
    },
  ];

  return (
    <div className="user-device-panel">
      <div className="user-device-panel__header">
        <div className="device-orbit" aria-hidden="true">
          <MonitorSmartphone size={20} />
          <span />
        </div>
        <div>
          <strong>{userItem.username} giriş bilgileri</strong>
          <p className="helper-text">
            Son başarılı girişte yakalanan cihaz ve ağ özeti.
          </p>
        </div>
      </div>

      <div className="device-detail-grid">
        {detailItems.map((item) => {
          const Icon = item.icon;
          return (
            <div className="device-detail-card" key={item.label}>
              <Icon size={16} />
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          );
        })}
      </div>

      <div className="device-user-agent">
        <span>User-Agent</span>
        <code>{deviceValue(userItem.last_login_user_agent)}</code>
      </div>
    </div>
  );
}

export default function UsersPage() {
  const { token, user: currentUser, presenceVersion, activeUserIds } = useOutletContext();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ username: "", password: "", role: "user" });
  const [expandedDeviceUserId, setExpandedDeviceUserId] = useState(null);

  const usersWithLivePresence = useMemo(() => {
    if (!Array.isArray(activeUserIds)) {
      return users;
    }

    const activeUserIdSet = new Set(activeUserIds);
    return users.map((item) => ({
      ...item,
      is_active: activeUserIdSet.has(item.id),
    }));
  }, [activeUserIds, users]);

  const activeCount = useMemo(
    () => usersWithLivePresence.filter((item) => item.is_active).length,
    [usersWithLivePresence],
  );

  const canViewLoginDetails = currentUser.role === "super_admin";

  const roleOptions = useMemo(() => {
    if (currentUser.role === "super_admin") {
      return MANAGEABLE_ROLES;
    }
    return ["user", "researcher"];
  }, [currentUser.role]);

  const [passwordDrafts, setPasswordDrafts] = useState({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const roleCounts = useMemo(
    () =>
      usersWithLivePresence.reduce(
        (counts, item) => ({
          ...counts,
          [item.role]: (counts[item.role] ?? 0) + 1,
        }),
        {},
      ),
    [usersWithLivePresence],
  );

  const loadUsers = useCallback(async () => {
    const payload = await usersApi.list(token);
    setUsers(payload);
  }, [token]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers, presenceVersion]);

  useEffect(() => {
    if (!canViewLoginDetails) {
      setExpandedDeviceUserId(null);
    }
  }, [canViewLoginDetails]);

  function setStatus(nextMessage, nextError = "") {
    setMessage(nextMessage);
    setError(nextError);
  }

  async function handleCreateUser(event) {
    event.preventDefault();
    try {
      await usersApi.create(token, form);
      setForm({ username: "", password: "", role: "user" });
      setStatus("Kullanıcı oluşturuldu.");
      await loadUsers();
    } catch (requestError) {
      setStatus("", "Kullanıcı oluşturulamadı. Yetersiz yetki veya kullanıcı adı alınmış olabilir.");
    }
  }

  async function handleRoleChange(userId, role) {
    try {
      await usersApi.updateRole(token, userId, role);
      setStatus("Rol güncellendi.");
      await loadUsers();
    } catch (requestError) {
      setStatus("", "Rol güncellenemedi.");
    }
  }

  async function handlePasswordReset(userId) {
    const password = passwordDrafts[userId] ?? "";
    if (password.length < 6) {
      setStatus("", "Yeni şifre en az 6 karakter olmalı.");
      return;
    }

    try {
      await usersApi.updatePassword(token, userId, password);
      setPasswordDrafts((current) => ({ ...current, [userId]: "" }));
      setStatus("Şifre sıfırlandı.");
    } catch (requestError) {
      setStatus("", "Şifre sıfırlanamadı.");
    }
  }

  async function handleDelete(userItem) {
    if (userItem.id === currentUser.id) {
      setStatus("", "Aktif admin hesabı silinemez.");
      return;
    }

    if (!window.confirm(`${userItem.username} kullanıcısını silmek istediğine emin misin?`)) {
      return;
    }

    try {
      await usersApi.remove(token, userItem.id);
      setStatus("Kullanıcı silindi.");
      await loadUsers();
    } catch (requestError) {
      setStatus("", "Kullanıcı silinemedi.");
    }
  }

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Kullanıcılar</h1>
          <p className="page-description">
            Admin hesapları kullanıcı ekleyebilir, rollerini değiştirebilir ve şifre sıfırlayabilir.
          </p>
        </div>
        <span className="badge badge--info">
          <Users size={14} />
          {users.length} kullanıcı
        </span>
      </div>

      <div className="grid grid--cards" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
        <article className="stat-card stat-card--teal" style={{ background: "linear-gradient(135deg, #059669, #10b981)" }}>
          <div className="split">
            <Activity size={18} />
            <strong>Aktif Kullanıcılar</strong>
          </div>
          <div className="metric">{activeCount}</div>
          <p className="helper-text">Şu an sistemde çevrimiçi olanlar</p>
        </article>
        {ALL_ROLES.map((role) => (
          <article key={role} className={`color-card color-card--${role}`}>
            <div className="split">
              <ShieldCheck size={18} />
              <strong>{roleLabel(role)}</strong>
            </div>
            <div className="metric">{roleCounts[role] ?? 0}</div>
            <p className="helper-text">
              {role === "super_admin"
                ? "Sistem sahibi (Ana Admin)"
                : role === "admin"
                  ? "Kullanıcı yönetimi yetkisi"
                  : role === "researcher"
                    ? "Tahminler ve veri yönetimi"
                    : "Dashboard izleme yetkisi"}
            </p>
          </article>
        ))}
      </div>

      <div className="grid grid--two">
        <section className="card colorful-panel">
          <div className="split" style={{ marginBottom: 18 }}>
            <div>
              <h3 className="panel-title">Yeni Kullanıcı</h3>
              <p className="helper-text">Sisteme yeni bir personel veya araştırmacı ekle.</p>
            </div>
            <UserPlus size={22} />
          </div>

          <form className="section-stack" onSubmit={handleCreateUser}>
            <div className="form-grid form-grid--user">
              <label className="stack">
                <span className="muted">Kullanıcı adı</span>
                <input
                  className="input"
                  required
                  minLength={3}
                  value={form.username}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, username: event.target.value }))
                  }
                />
              </label>
              <label className="stack">
                <span className="muted">Şifre</span>
                <input
                  className="input"
                  required
                  minLength={6}
                  type="password"
                  value={form.password}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, password: event.target.value }))
                  }
                />
              </label>
              <label className="stack">
                <span className="muted">Rol</span>
                <select
                  className="select"
                  value={form.role}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, role: event.target.value }))
                  }
                >
                  {roleOptions.map((role) => (
                    <option key={role} value={role}>
                      {roleLabel(role)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <button className="button button--primary" type="submit">
              <UserPlus size={16} />
              Kullanıcı Oluştur
            </button>
          </form>
        </section>

        <section className="card profile-card">
          <p className="eyebrow">Aktif Oturum</p>
          <div className="profile-card__main">
            <div className="active-profile-avatar">
              <span className="active-profile-avatar__ring" />
              <div className="avatar avatar--large">{currentUser.username[0]?.toUpperCase()}</div>
            </div>
            <div>
              <div className="user-name-row">
                <h3 className="panel-title">{currentUser.username}</h3>
                <span className="active-session-badge" title="Aktif oturum">
                  <span className="active-session-badge__wave" />
                  <Activity size={12} />
                  Aktif
                </span>
              </div>
              <p className="helper-text">{roleLabel(currentUser.role)} yetkisiyle yönetim panelindesin.</p>
            </div>
          </div>
          <div className="details-list" style={{ marginTop: 18 }}>
            <div className="split">
              <span>Rol</span>
              <span className="badge badge--info">{roleLabel(currentUser.role)}</span>
            </div>
            <div className="split">
              <span>Oluşturulma</span>
              <strong>{formatDateTime(currentUser.created_at)}</strong>
            </div>
          </div>
        </section>
      </div>

      {message ? <div className="status-banner status-banner--success">{message}</div> : null}
      {error ? <div className="status-banner status-banner--danger">{error}</div> : null}

      <section className="card">
        <div className="split" style={{ marginBottom: 16 }}>
          <div>
            <h3 className="panel-title">Kullanıcı Listesi</h3>
            <p className="helper-text">Rol, şifre ve hesap durumu tek ekrandan yönetilir.</p>
          </div>
        </div>

        <div className="table-scroll">
          <table className="table user-table">
            <thead>
              <tr>
                <th>Kullanıcı</th>
                <th>Rol</th>
                <th>Oluşturulma</th>
                <th>Şifre Sıfırla</th>
                <th>İşlem</th>
              </tr>
            </thead>
            <tbody>
              {usersWithLivePresence.map((userItem) => {
                const isTargetSuper = userItem.role === "super_admin";
                const isSelf = userItem.id === currentUser.id;
                const iAmSuper = currentUser.role === "super_admin";
                const isProtectedAdmin = !iAmSuper && userItem.role === "admin";

                const cannotEditRole = isSelf || (isTargetSuper && !iAmSuper) || isProtectedAdmin;
                const cannotDelete = isSelf || (isTargetSuper && !iAmSuper) || isProtectedAdmin;
                const cannotReset = (isTargetSuper && !iAmSuper) || isProtectedAdmin;

                const currentEditOptions = iAmSuper ? MANAGEABLE_ROLES : ["user", "researcher"];

                return (
                <Fragment key={userItem.id}>
                <tr className={isSelf ? "user-row user-row--active" : "user-row"}>
                  <td data-label="Kullanıcı">
                    <div className="user-cell">
                      <div className="user-avatar">
                        <div className="avatar">{userItem.username[0]?.toUpperCase()}</div>
                        {userItem.is_active && (
                          <span className="avatar-status-dot status-dot--online" />
                        )}
                      </div>
                      <div>
                        <div className="user-name-row">
                          <strong>{userItem.username}</strong>
                          {canViewLoginDetails ? (
                            <button
                              className={`about-button${
                                expandedDeviceUserId === userItem.id ? " about-button--active" : ""
                              }`}
                              type="button"
                              aria-expanded={expandedDeviceUserId === userItem.id}
                              onClick={() =>
                                setExpandedDeviceUserId((current) =>
                                  current === userItem.id ? null : userItem.id,
                                )
                              }
                            >
                              <Info size={14} />
                              Hakkında
                            </button>
                          ) : null}
                          {isSelf ? (
                            <span className="active-session-badge" title="Aktif oturum">
                              <span className="active-session-badge__wave" />
                              <Activity size={12} />
                              Aktif
                            </span>
                          ) : userItem.is_active ? (
                            <span className="online-badge">
                              <span className="online-badge__dot" />
                              Online
                            </span>
                          ) : null}
                        </div>
                        {isSelf ? <p className="helper-text">Aktif hesap</p> : null}
                        {isTargetSuper ? <p className="helper-text" style={{ color: "#f59e0b" }}>Ana Admin</p> : null}
                      </div>
                    </div>
                  </td>
                  <td data-label="Rol">
                    <select
                      className="select"
                      value={userItem.role}
                      disabled={cannotEditRole}
                      onChange={(event) => handleRoleChange(userItem.id, event.target.value)}
                    >
                      {/* If we can't edit, just show current role */}
                      {cannotEditRole ? (
                        <option value={userItem.role}>{roleLabel(userItem.role)}</option>
                      ) : (
                        currentEditOptions.map((role) => (
                          <option key={role} value={role}>
                            {roleLabel(role)}
                          </option>
                        ))
                      )}
                    </select>
                  </td>
                  <td data-label="Oluşturulma">{formatDateTime(userItem.created_at)}</td>
                  <td data-label="Şifre Sıfırla">
                    <div className="inline-actions">
                      <input
                        className="input input--compact"
                        type="password"
                        minLength={6}
                        placeholder="Yeni şifre"
                        disabled={cannotReset}
                        value={passwordDrafts[userItem.id] ?? ""}
                        onChange={(event) =>
                          setPasswordDrafts((current) => ({
                            ...current,
                            [userItem.id]: event.target.value,
                          }))
                        }
                      />
                      <button
                        className="button button--secondary"
                        type="button"
                        disabled={cannotReset}
                        onClick={() => handlePasswordReset(userItem.id)}
                      >
                        <KeyRound size={15} />
                        Sıfırla
                      </button>
                    </div>
                  </td>
                  <td data-label="İşlem">
                    <button
                      className="button button--danger"
                      disabled={cannotDelete}
                      type="button"
                      onClick={() => handleDelete(userItem)}
                    >
                      <Trash2 size={15} />
                      Sil
                    </button>
                  </td>
                </tr>
                {canViewLoginDetails && expandedDeviceUserId === userItem.id ? (
                  <tr className="user-detail-row">
                    <td colSpan={5}>
                      <UserDeviceDetails userItem={userItem} />
                    </td>
                  </tr>
                ) : null}
                </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
