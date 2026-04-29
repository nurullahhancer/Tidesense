import { Gauge, RadioTower, Thermometer, Waves } from "lucide-react";

import { formatDateTime, formatMetric } from "../../utils/formatters.js";
import StatusBadge from "../common/StatusBadge.jsx";

export default function SensorCard({ item }) {
  const reading = item.reading;

  return (
    <article className={`station-card station-card--${item.risk_level?.toLowerCase() ?? "normal"}`}>
      <div className="station-card__header">
        <div>
          <p className="eyebrow">{item.station.city}</p>
          <h3 className="panel-title">{item.station.name}</h3>
        </div>
        <StatusBadge label={item.risk_level} />
      </div>

      <div className="station-card__metric">
        <Waves size={22} />
        <div>
          <div className="metric">
            {formatMetric(reading?.water_level_cm)}
            <span>cm</span>
          </div>
          <p className="helper-text">Su seviyesi</p>
        </div>
      </div>

      <div className="sensor-strip">
        <div>
          <Gauge size={16} />
          <strong>{formatMetric(reading?.air_pressure_hpa)}</strong>
          <span>hPa</span>
        </div>
        <div>
          <Thermometer size={16} />
          <strong>{formatMetric(reading?.temperature_c)}</strong>
          <span>C</span>
        </div>
        <div>
          <RadioTower size={16} />
          <strong>{reading?.data_source ?? "-"}</strong>
          <span>kaynak</span>
        </div>
      </div>

      <div className="station-card__footer">
        <span>{formatDateTime(reading?.recorded_at)}</span>
      </div>
    </article>
  );
}
