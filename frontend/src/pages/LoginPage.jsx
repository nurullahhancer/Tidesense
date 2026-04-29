import { Activity, Lock, ShieldCheck, Sparkles, Waves } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext.jsx";

const demoAccounts = [
  { username: "coastal_user", password: "User123!", role: "User" },
  { username: "marine_researcher", password: "Research123!", role: "Researcher" },
  { username: "system_admin", password: "Admin123!", role: "Admin" },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({
    username: "marine_researcher",
    password: "Research123!",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(form);
      const redirectTo = location.state?.from?.pathname ?? "/dashboard";
      navigate(redirectTo, { replace: true });
    } catch (requestError) {
      setError("Giriş başarısız. Kullanıcı adı veya şifreyi kontrol et.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-card__hero">
          <div className="brand-title">
            <span className="brand-mark">
              <Activity size={22} />
            </span>
            <div>
              <div>TideSense</div>
              <div className="brand-subtitle">Ay Konumu Tabanlı Gelgit Tahmin Platformu</div>
            </div>
          </div>

          <h1 className="page-title" style={{ marginTop: 28 }}>
            Kıyı istasyonlarını, tahminleri ve risk akışını tek panelden yönetin.
          </h1>
          <p className="page-description">
            Frontend yalnızca kendi backend API’sine bağlanır; dış veri önce veritabanına yazılır,
            ardından canlı dashboard ve tahmin ekranlarına taşınır.
          </p>

          <div className="hero-stat">
            <Waves size={18} />
            <div>
              <strong>4 kıyı istasyonu</strong>
              <div className="helper-text">İskenderun, İzmir, İstanbul ve Trabzon aynı akışta</div>
            </div>
          </div>

          <div className="hero-grid">
            <article className="card">
              <ShieldCheck size={18} />
              <h3 className="panel-title">JWT + RBAC</h3>
              <p className="helper-text">User, Researcher ve Admin için ayrılmış görünüm.</p>
            </article>
            <article className="card">
              <Sparkles size={18} />
              <h3 className="panel-title">ML Tahmin</h3>
              <p className="helper-text">RandomForest tabanlı 24 saatlik gelgit öngörüsü.</p>
            </article>
          </div>
        </div>

        <form className="login-card__form" onSubmit={handleSubmit}>
          <div className="stack">
            <h2 className="panel-title" style={{ fontSize: "1.6rem" }}>
              Sisteme giriş yap
            </h2>
            <p className="helper-text">Demo kullanıcıları hazır yüklendi.</p>
          </div>

          <label className="stack">
            <span>Kullanıcı adı</span>
            <input
              className="input"
              value={form.username}
              onChange={(event) =>
                setForm((current) => ({ ...current, username: event.target.value }))
              }
            />
          </label>

          <label className="stack">
            <span>Şifre</span>
            <div style={{ position: "relative" }}>
              <input
                type="password"
                className="input"
                value={form.password}
                onChange={(event) =>
                  setForm((current) => ({ ...current, password: event.target.value }))
                }
              />
              <Lock size={16} style={{ position: "absolute", right: 14, top: 14, color: "#94a3b8" }} />
            </div>
          </label>

          {error ? <div className="badge badge--critical">{error}</div> : null}

          <button className="button button--primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Giriş yapılıyor..." : "Giriş Yap"}
          </button>

          <div className="stack">
            <span className="muted">Hazır demo hesapları</span>
            <div className="table-list">
              {demoAccounts.map((account) => (
                <button
                  key={account.username}
                  type="button"
                  className="button button--ghost"
                  onClick={() =>
                    setForm({ username: account.username, password: account.password })
                  }
                >
                  {account.role}: {account.username}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
