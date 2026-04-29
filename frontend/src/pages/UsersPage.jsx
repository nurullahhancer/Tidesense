import { KeyRound, ShieldCheck, Trash2, UserPlus, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { usersApi } from "../services/api.js";
import { formatDateTime, roleLabel } from "../utils/formatters.js";

const roleOptions = ["user", "researcher", "admin"];

export default function UsersPage() {
  const { token, user: currentUser } = useOutletContext();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ username: "", password: "", role: "user" });
  const [passwordDrafts, setPasswordDrafts] = useState({});
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const roleCounts = useMemo(
    () =>
      users.reduce(
        (counts, item) => ({
          ...counts,
          [item.role]: (counts[item.role] ?? 0) + 1,
        }),
        {},
      ),
    [users],
  );

  async function loadUsers() {
    const payload = await usersApi.list(token);
    setUsers(payload);
  }

  useEffect(() => {
    loadUsers();
  }, [token]);

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
      setStatus("", "Kullanıcı oluşturulamadı. Kullanıcı adı daha önce alınmış olabilir.");
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
    if (password.length < 8) {
      setStatus("", "Yeni şifre en az 8 karakter olmalı.");
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

      <div className="grid grid--cards">
        {roleOptions.map((role) => (
          <article key={role} className={`color-card color-card--${role}`}>
            <div className="split">
              <ShieldCheck size={18} />
              <strong>{roleLabel(role)}</strong>
            </div>
            <div className="metric">{roleCounts[role] ?? 0}</div>
            <p className="helper-text">
              {role === "admin"
                ? "Sistem ve kullanıcı yönetimi"
                : role === "researcher"
                  ? "Tahminler ve veri dışa aktarımı"
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
              <p className="helper-text">Demo veya sunum için hızlı hesap oluştur.</p>
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
                  minLength={8}
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
            <div className="avatar avatar--large">{currentUser.username[0]?.toUpperCase()}</div>
            <div>
              <h3 className="panel-title">{currentUser.username}</h3>
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
              {users.map((userItem) => {
                const isMainAdmin = userItem.username === "tidesense";
                const isSelf = userItem.id === currentUser.id;
                const amIMainAdmin = currentUser.username === "tidesense";
                const cannotEditRole = isSelf || (isMainAdmin && !amIMainAdmin);
                const cannotDelete = isSelf || (isMainAdmin && !amIMainAdmin);
                const cannotReset = isMainAdmin && !amIMainAdmin;

                return (
                <tr key={userItem.id}>
                  <td data-label="Kullanıcı">
                    <div className="user-cell">
                      <div className="avatar">{userItem.username[0]?.toUpperCase()}</div>
                      <div>
                        <strong>{userItem.username}</strong>
                        {isSelf ? <p className="helper-text">Aktif hesap</p> : null}
                        {isMainAdmin ? <p className="helper-text" style={{ color: "#f59e0b" }}>Ana Admin</p> : null}
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
                      {roleOptions.map((role) => (
                        <option key={role} value={role}>
                          {roleLabel(role)}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td data-label="Oluşturulma">{formatDateTime(userItem.created_at)}</td>
                  <td data-label="Şifre Sıfırla">
                    <div className="inline-actions">
                      <input
                        className="input input--compact"
                        type="password"
                        minLength={8}
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
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
