export function formatDateTime(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("tr-TR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatMetric(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return Number(value).toFixed(digits);
}

export function roleLabel(role) {
  return {
    user: "User",
    researcher: "Researcher",
    admin: "Admin",
    super_admin: "Ana Admin",
  }[role] ?? role;
}

export function riskVariant(severity) {
  if (severity === "KRITIK") return "critical";
  if (severity === "DIKKAT") return "warning";
  if (severity === "NORMAL") return "normal";
  return "offline";
}
