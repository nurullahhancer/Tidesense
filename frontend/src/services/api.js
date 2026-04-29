const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ??
  API_BASE_URL.replace("/api/v1", "").replace(/^http/, "ws");

async function request(path, options = {}) {
  const { token, body, headers, ...rest } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers ?? {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const payload = await response.text();
    throw new Error(payload || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const apiConfig = {
  baseUrl: API_BASE_URL,
  wsUrl: `${WS_BASE_URL}/ws/live`,
};

export const authApi = {
  login: (credentials) =>
    request("/auth/login", { method: "POST", body: credentials }),
  me: (token) => request("/auth/me", { token }),
};

export const stationsApi = {
  list: (token) => request("/stations", { token }),
  detail: (token, stationId) => request(`/stations/${stationId}`, { token }),
  create: (token, payload) =>
    request("/stations", { method: "POST", token, body: payload }),
};

export const sensorApi = {
  latest: (token) => request("/sensors/latest", { token }),
  readings: (token, stationId) =>
    request(`/sensors/readings${stationId ? `?station_id=${stationId}` : ""}`, {
      token,
    }),
};

export const readingsApi = {
  history: (token, stationId, params = {}) => {
    const searchParams = new URLSearchParams({ station_id: stationId, ...params });
    return request(`/readings/history?${searchParams.toString()}`, { token });
  },
  historyCsv: async (token, stationId, startAt = null, endAt = null) => {
    let url = `${API_BASE_URL}/readings/history?station_id=${stationId}&export_format=csv&limit=2000`;
    if (startAt) url += `&start_at=${encodeURIComponent(startAt)}`;
    if (endAt) url += `&end_at=${encodeURIComponent(endAt)}`;
    const response = await fetch(url, {
      headers: { 
        Authorization: `Bearer ${token}`,
        "ngrok-skip-browser-warning": "true"
      },
    });
    if (!response.ok) {
      throw new Error("CSV export failed");
    }
    return response.text();
  },
  stats: (token, stationId, periodHours = 24) =>
    request(`/readings/stats?station_id=${stationId}&period_hours=${periodHours}`, {
      token,
    }),
  external: (token, params = {}) => {
    const searchParams = new URLSearchParams(params);
    return request(`/readings/noaa?${searchParams.toString()}`, { token });
  },
};

export const moonApi = {
  current: (token, stationId) =>
    request(`/moon/current${stationId ? `?station_id=${stationId}` : ""}`, { token }),
};

export const predictionApi = {
  list: (token, params = {}) => {
    const searchParams = new URLSearchParams(params);
    return request(`/predictions?${searchParams.toString()}`, { token });
  },
};

export const alertsApi = {
  list: (token, params = {}) => {
    const searchParams = new URLSearchParams(params);
    return request(`/alerts?${searchParams.toString()}`, { token });
  },
  acknowledge: (token, alertId) =>
    request("/alerts/ack", { method: "POST", token, body: { alert_id: alertId } }),
};

export const cameraApi = {
  list: (token, stationId) =>
    request(`/cameras${stationId ? `?station_id=${stationId}` : ""}`, { token }),
};

export const healthApi = {
  snapshot: (token) => request("/health", { token }),
};

export const usersApi = {
  list: (token) => request("/users", { token }),
  create: (token, payload) =>
    request("/users", { method: "POST", token, body: payload }),
  updateRole: (token, userId, role) =>
    request(`/users/${userId}/role`, { method: "PATCH", token, body: { role } }),
  updatePassword: (token, userId, password) =>
    request(`/users/${userId}/password`, { method: "PATCH", token, body: { password } }),
  remove: async (token, userId) => {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: "DELETE",
      headers: { 
        Authorization: `Bearer ${token}`,
        "ngrok-skip-browser-warning": "true"
      },
    });
    if (!response.ok) {
      const payload = await response.text();
      throw new Error(payload || "User delete failed");
    }
    return null;
  },
};
