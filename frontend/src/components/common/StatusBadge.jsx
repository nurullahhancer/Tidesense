import { riskVariant } from "../../utils/formatters.js";

export default function StatusBadge({ label }) {
  const variant = riskVariant(label);
  return <span className={`badge badge--${variant}`}>{label}</span>;
}
