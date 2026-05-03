import { Activity, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext.jsx";

async function collectDeviceHints() {
  if (!navigator.userAgentData?.getHighEntropyValues) {
    return {};
  }

  try {
    const hints = await navigator.userAgentData.getHighEntropyValues([
      "platform",
      "platformVersion",
    ]);
    return {
      device_platform: [hints.platform, hints.platformVersion].filter(Boolean).join(" ") || null,
    };
  } catch (error) {
    return {};
  }
}

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({
    username: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!form.username || !form.password) {
      setError("Lütfen kullanıcı adı ve şifre giriniz.");
      return;
    }
    setError("");
    setIsSubmitting(true);
    try {
      const deviceHints = await collectDeviceHints();
      await login({ ...form, ...deviceHints });
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
              <Activity size={24} />
            </span>
            <div className="login-brand-name">TideSense</div>
          </div>
          
          <h1 className="page-title login-hero-title">
            Hoş Geldiniz.
          </h1>
          <p className="page-description login-hero-desc">
            Akıllı gelgit izleme ve tahmin sistemine erişmek için lütfen giriş yapın.
          </p>
        </div>

        <form className="login-card__form" onSubmit={handleSubmit} autoCorrect="off" autoCapitalize="off">
          <div className="login-mobile-brand" aria-hidden="true">
            <span className="brand-mark">
              <Activity size={20} />
              <span className="brand-mark__flow" />
            </span>
            <div>
              <strong>TideSense</strong>
              <span>Operasyon Paneli</span>
            </div>
          </div>

          <div className="stack login-form-header">
            <h2 className="panel-title login-form-title">
              Giriş Yap
            </h2>
            <p className="helper-text">Lütfen kullanıcı bilgilerinizi giriniz.</p>
          </div>

          <label className="stack">
            <span className="input-label">Kullanıcı Adı</span>
            <input
              className="input"
              required
              autoComplete="off"
              placeholder="Kullanıcı adınızı yazın"
              value={form.username}
              onChange={(event) =>
                setForm((current) => ({ ...current, username: event.target.value }))
              }
            />
          </label>

          <label className="stack">
            <span className="input-label">Şifre</span>
            <div className="password-field">
              <input
                type={showPassword ? "text" : "password"}
                className="input"
                required
                autoComplete="new-password"
                placeholder="••••••••"
                value={form.password}
                onChange={(event) =>
                  setForm((current) => ({ ...current, password: event.target.value }))
                }
              />
              <button
                className="password-toggle"
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Şifreyi gizle" : "Şifreyi göster"}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </label>

          {error ? <div className="badge badge--critical login-error">{error}</div> : null}

          <button className="button button--primary login-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Giriş yapılıyor..." : "Sisteme Giriş Yap"}
          </button>
        </form>
      </div>
    </div>
  );
}
