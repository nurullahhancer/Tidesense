import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import MoonStatus from "../components/panels/MoonStatus.jsx";
import { moonApi } from "../services/api.js";

export default function MoonPage() {
  const { token, selectedStation } = useOutletContext();
  const [moon, setMoon] = useState(null);

  useEffect(() => {
    async function load() {
      if (!selectedStation) return;
      const payload = await moonApi.current(token, selectedStation.id);
      setMoon(payload);
    }
    load();
  }, [token, selectedStation]);

  return (
    <div className="section-stack">
      <div className="page-header">
        <div>
          <h1 className="page-title">Ay Durumu</h1>
          <p className="page-description">
            Ay fazı, illumination ve gravity factor bilgileri tahmin modelini besleyen ortak girdilerdir.
          </p>
        </div>
      </div>
      <MoonStatus moon={moon} />
    </div>
  );
}
