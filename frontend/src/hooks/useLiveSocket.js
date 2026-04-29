import { useEffect, useRef, useState } from "react";

import { apiConfig } from "../services/api.js";

export function useLiveSocket({ token, enabled = true, onMessage }) {
  const [status, setStatus] = useState("offline");
  const callbackRef = useRef(onMessage);

  useEffect(() => {
    callbackRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!enabled || !token) {
      setStatus("offline");
      return undefined;
    }

    const websocket = new WebSocket(
      `${apiConfig.wsUrl}?token=${encodeURIComponent(token)}`,
    );
    setStatus("connecting");

    const interval = setInterval(() => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.send("ping");
      }
    }, 20000);

    websocket.onopen = () => setStatus("online");
    websocket.onclose = () => setStatus("offline");
    websocket.onerror = () => setStatus("offline");
    websocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        callbackRef.current?.(payload);
      } catch (error) {
        console.error("WebSocket parse error", error);
      }
    };

    return () => {
      clearInterval(interval);
      websocket.close();
    };
  }, [enabled, token]);

  return status;
}
