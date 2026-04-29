import { Play } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { apiConfig } from "../../services/api.js";
import StatusBadge from "../common/StatusBadge.jsx";

export default function CameraView({ camera }) {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [isLive, setIsLive] = useState(false);
  const [error, setError] = useState(false);

  const baseUrl = apiConfig.baseUrl.replace("/api/v1", "");
  const snapshotUrl = camera.snapshot_url?.startsWith("http")
    ? camera.snapshot_url
    : camera.snapshot_url
      ? `${baseUrl}${camera.snapshot_url}`
      : null;
  const streamUrl = camera.stream_url?.startsWith("http")
    ? camera.stream_url
    : camera.stream_url
      ? `${baseUrl}${camera.stream_url}`
      : null;
  const hasStream = Boolean(streamUrl);
  const isYouTube =
    streamUrl && (streamUrl.includes("youtube.com") || streamUrl.includes("youtu.be"));

  const getYoutubeId = (url) => {
    if (!url) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  };

  const toggleLive = () => {
    if (!hasStream) return;
    setError(false);
    setIsLive(!isLive);
  };

  useEffect(() => {
    function initHls() {
      if (!videoRef.current || !streamUrl || !window.Hls?.isSupported()) return;

      const hls = new window.Hls();
      hls.loadSource(streamUrl);
      hls.attachMedia(videoRef.current);
      hls.on(window.Hls.Events.MANIFEST_PARSED, () =>
        videoRef.current.play().catch(() => setError(true)),
      );
      hls.on(window.Hls.Events.ERROR, () => setError(true));
      hlsRef.current = hls;
    }

    if (isLive && !isYouTube && streamUrl) {
      if (!window.Hls) {
        const script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/hls.js@latest";
        script.async = true;
        script.onload = () => initHls();
        document.body.appendChild(script);
      } else {
        initHls();
      }
    }

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [isLive, isYouTube, streamUrl]);

  return (
    <article
      className="card"
      style={{ border: isLive ? "1px solid var(--accent)" : "1px solid var(--border-soft)" }}
    >
      <div className="split" style={{ marginBottom: 12 }}>
        <div>
          <p className="muted" style={{ margin: 0 }}>{camera.station.city}</p>
          <h3 className="panel-title">{camera.station.name}</h3>
        </div>
        <StatusBadge label={camera.risk_status} />
      </div>

      <div
        className="camera-frame"
        style={{
          position: "relative",
          background: "#000",
          borderRadius: "16px",
          overflow: "hidden",
          height: "260px",
        }}
      >
        {isLive && hasStream ? (
          isYouTube ? (
            <iframe
              width="100%"
              height="100%"
              src={`https://www.youtube.com/embed/${getYoutubeId(streamUrl)}?autoplay=1&mute=1`}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          ) : (
            <video ref={videoRef} autoPlay muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          )
        ) : (
          <div style={{ position: "relative", width: "100%", height: "100%" }}>
            <img
              src={snapshotUrl || `https://picsum.photos/seed/${camera.station.code}/800/450`}
              alt="station snapshot"
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "rgba(0,0,0,0.3)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {hasStream ? (
                <button onClick={toggleLive} className="play-button-large">
                  <Play size={32} fill="white" />
                </button>
              ) : (
                <div className="badge">Demo kamera görüntüsü</div>
              )}
            </div>
          </div>
        )}
      </div>

      {error ? <div className="badge badge--critical">Yayın bağlantısı açılamadı</div> : null}

      <div className="split" style={{ marginTop: 16 }}>
        <button
          className={`button ${isLive ? "button--secondary" : "button--primary"}`}
          disabled={!hasStream}
          onClick={toggleLive}
          style={{ width: "100%" }}
        >
          {!hasStream ? "Demo Kamera" : isLive ? "Yayını Kapat" : "Canlı Yayına Bağlan"}
        </button>
      </div>
    </article>
  );
}
