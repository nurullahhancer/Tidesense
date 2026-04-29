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
      <div className="login-card" style={{ gridTemplateColumns: "1fr 420px" }}>
        <div className="login-card__hero" style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "flex-start" }}>
          <div className="brand-title">
            <span className="brand-mark">
              <Activity size={24} />
            </span>
            <div style={{ fontSize: "1.8rem" }}>TideSense</div>
          </div>
          
          <h1 className="page-title" style={{ marginTop: 24, fontSize: "2.2rem" }}>
            Hoş Geldiniz.
          </h1>
          <p className="page-description" style={{ fontSize: "1.1rem", opacity: 0.9 }}>
            Akıllı gelgit izleme ve tahmin sistemine erişmek için lütfen giriş yapın.
          </p>
        </div>

        <form className="login-card__form" onSubmit={handleSubmit} style={{ justifyContent: "center" }}>
          <div className="stack" style={{ marginBottom: 12 }}>
            <h2 className="panel-title" style={{ fontSize: "1.8rem" }}>
              Giriş Yap
            </h2>
            <p className="helper-text">Lütfen kullanıcı bilgilerinizi giriniz.</p>
          </div>

          <label className="stack">
            <span style={{ fontWeight: 600 }}>Kullanıcı Adı</span>
            <input
              className="input"
              placeholder="Kullanıcı adınızı yazın"
              value={form.username}
              onChange={(event) =>
                setForm((current) => ({ ...current, username: event.target.value }))
              }
            />
          </label>

          <label className="stack">
            <span style={{ fontWeight: 600 }}>Şifre</span>
            <div style={{ position: "relative" }}>
              <input
                type="password"
                className="input"
                placeholder="••••••••"
                value={form.password}
                onChange={(event) =>
                  setForm((current) => ({ ...current, password: event.target.value }))
                }
              />
              <Lock size={16} style={{ position: "absolute", right: 14, top: 14, color: "#94a3b8" }} />
            </div>
          </label>

          {error ? <div className="badge badge--critical" style={{ width: "100%", padding: "10px" }}>{error}</div> : null}

          <button className="button button--primary" type="submit" disabled={isSubmitting} style={{ height: "48px", marginTop: 12 }}>
            {isSubmitting ? "Giriş yapılıyor..." : "Sisteme Giriş Yap"}
          </button>
        </form>
      </div>
    </div>
  );
}
