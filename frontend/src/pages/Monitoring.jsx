import { useState, useEffect } from 'react';

export default function Monitoring() {
  const [status, setStatus] = useState({});

  useEffect(() => {
    fetch('/api/status')
      .then(r => r.json())
      .then(d => setStatus(d.services || {}))
      .catch(() => {});
  }, []);

  const services = [
    { name: "Auth", port: 8001, color: "#f59e0b" },
    { name: "Project", port: 8002, color: "#8b5cf6" },
    { name: "Billing", port: 8003, color: "#ef4444" },
    { name: "Notification", port: 8004, color: "#06b6d4" },
    { name: "Analytics", port: 8005, color: "#84cc16" },
    { name: "Gateway", port: 8000, color: "#3ecf8e" },
  ];

  const serviceKey = (name) => name.toLowerCase();
  const isOk = (name) => status[serviceKey(name)]?.status === "ok";

  return (
    <div>
      <h2 style={{ fontSize: 22, fontWeight: 600, marginBottom: 8 }}>Monitoring</h2>
      <p style={{ color: "#6b7494", fontSize: 13, marginBottom: 32 }}>
        État des services en temps réel — Prometheus + Grafana
      </p>

      {/* Statut des services */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: "#e8eaf0" }}>
          État des microservices
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
          {services.map((s, i) => (
            <div key={i} style={{
              background: "#161a23", border: `1px solid ${isOk(s.name) ? s.color + "44" : "#ef444444"}`,
              borderRadius: 10, padding: "16px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ fontWeight: 500, fontSize: 14, color: s.color }}>{s.name}</span>
                <span style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: isOk(s.name) ? "#3ecf8e" : "#ef4444",
                  display: "inline-block"
                }}></span>
              </div>
              <div style={{ fontSize: 11, color: "#6b7494" }}>Port :{s.port}</div>
              <div style={{ fontSize: 11, color: isOk(s.name) ? "#3ecf8e" : "#ef4444", marginTop: 4 }}>
                {isOk(s.name) ? "● En ligne" : "● Hors ligne"}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Liens outils */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: "#e8eaf0" }}>
          Outils de monitoring
        </div>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          <a href="http://localhost:9090" target="_blank" rel="noreferrer" style={{
            background: "#161a23", border: "1px solid #e6522c44", borderRadius: 10,
            padding: "20px 24px", textDecoration: "none", display: "block", minWidth: 200
          }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>📊</div>
            <div style={{ fontWeight: 600, color: "#e6522c", marginBottom: 4 }}>Prometheus</div>
            <div style={{ fontSize: 12, color: "#6b7494" }}>Métriques & alertes</div>
            <div style={{ fontSize: 11, color: "#3a4060", marginTop: 8 }}>localhost:9090</div>
          </a>
          <a href="http://localhost:3001" target="_blank" rel="noreferrer" style={{
            background: "#161a23", border: "1px solid #f5993344", borderRadius: 10,
            padding: "20px 24px", textDecoration: "none", display: "block", minWidth: 200
          }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>📈</div>
            <div style={{ fontWeight: 600, color: "#f59933", marginBottom: 4 }}>Grafana</div>
            <div style={{ fontSize: 12, color: "#6b7494" }}>Dashboards & visualisation</div>
            <div style={{ fontSize: 11, color: "#3a4060", marginTop: 8 }}>localhost:3001 — admin / cloudapp2026</div>
          </a>
        </div>
      </div>

      {/* Info */}
      <div style={{ background: "#161a23", border: "1px solid #2a3040", borderRadius: 10, padding: 20 }}>
        <div style={{ fontWeight: 600, marginBottom: 12 }}>Configuration Prometheus</div>
        <div style={{ fontFamily: "monospace", fontSize: 12, color: "#6b7494", lineHeight: 1.8 }}>
          <div>scrape_interval: <span style={{ color: "#3ecf8e" }}>15s</span></div>
          <div>targets: <span style={{ color: "#4f7cff" }}>6 microservices</span></div>
          <div>metrics_path: <span style={{ color: "#f59e0b" }}>/metrics</span></div>
        </div>
      </div>
    </div>
  );
}