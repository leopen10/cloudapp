export default function Architecture() {
  const services = [
    { name: "Frontend", port: "3000", color: "#4f7cff", icon: "🖥️", tech: "React + Nginx" },
    { name: "Gateway", port: "8000", color: "#3ecf8e", icon: "🔀", tech: "FastAPI" },
    { name: "Auth", port: "8001", color: "#f59e0b", icon: "🔐", tech: "FastAPI + JWT" },
    { name: "Project", port: "8002", color: "#8b5cf6", icon: "📁", tech: "FastAPI" },
    { name: "Billing", port: "8003", color: "#ef4444", icon: "🧾", tech: "FastAPI" },
    { name: "Notification", port: "8004", color: "#06b6d4", icon: "🔔", tech: "FastAPI + Resend" },
    { name: "Analytics", port: "8005", color: "#84cc16", icon: "📊", tech: "FastAPI" },
    { name: "PostgreSQL", port: "5432", color: "#6b7494", icon: "🗄️", tech: "PostgreSQL 16" },
  ];

  const box = (s, i) => (
    <div key={i} style={{
      background: "#161a23", border: `1px solid ${s.color}44`,
      borderRadius: 10, padding: "12px 16px", minWidth: 140,
      textAlign: "center", position: "relative"
    }}>
      <div style={{ fontSize: 24 }}>{s.icon}</div>
      <div style={{ fontWeight: 600, fontSize: 13, color: s.color, margin: "4px 0" }}>{s.name}</div>
      <div style={{ fontSize: 11, color: "#6b7494" }}>{s.tech}</div>
      <div style={{ fontSize: 10, color: "#3a4060", marginTop: 4,
        background: "#0d0f14", borderRadius: 4, padding: "2px 6px", display: "inline-block" }}>
        :{s.port}
      </div>
    </div>
  );

  const arrow = (label) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 8px" }}>
      <div style={{ fontSize: 10, color: "#6b7494", marginBottom: 2 }}>{label}</div>
      <div style={{ color: "#4f7cff", fontSize: 18 }}>→</div>
    </div>
  );

  return (
    <div>
      <h2 style={{ fontSize: 22, fontWeight: 600, marginBottom: 8 }}>Architecture CloudApp</h2>
      <p style={{ color: "#6b7494", fontSize: 13, marginBottom: 32 }}>
        Architecture microservices — 7 services FastAPI + PostgreSQL + React frontend
      </p>

      {/* Couche 1 — Client */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: "#6b7494", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>
          Couche Client
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {box(services[0])}
          {arrow("HTTP/HTTPS")}
          {box(services[1])}
        </div>
      </div>

      {/* Flèche vers bas */}
      <div style={{ display: "flex", alignItems: "center", marginLeft: 160, marginBottom: 16 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div style={{ fontSize: 10, color: "#6b7494" }}>Routing</div>
          <div style={{ color: "#4f7cff", fontSize: 18 }}>↓</div>
        </div>
      </div>

      {/* Couche 2 — Microservices */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: "#6b7494", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>
          Couche Microservices
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {services.slice(2, 7).map((s, i) => box(s, i))}
        </div>
      </div>

      {/* Flèche vers bas */}
      <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div style={{ fontSize: 10, color: "#6b7494" }}>SQLAlchemy ORM</div>
          <div style={{ color: "#4f7cff", fontSize: 18 }}>↓</div>
        </div>
      </div>

      {/* Couche 3 — Base de données */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 11, color: "#6b7494", marginBottom: 8, textTransform: "uppercase", letterSpacing: 1 }}>
          Couche Données
        </div>
        {box(services[7])}
      </div>

      {/* Stack technique */}
      <div style={{ background: "#161a23", border: "1px solid #2a3040", borderRadius: 10, padding: 20 }}>
        <div style={{ fontWeight: 600, marginBottom: 16 }}>Stack Technique</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
          {[
            { label: "Backend", value: "FastAPI (Python 3.11)", color: "#4f7cff" },
            { label: "Frontend", value: "React + Vite + Nginx", color: "#3ecf8e" },
            { label: "Base de données", value: "PostgreSQL 16", color: "#f59e0b" },
            { label: "ORM", value: "SQLAlchemy 2.0", color: "#8b5cf6" },
            { label: "Conteneurisation", value: "Docker + Docker Compose", color: "#06b6d4" },
            { label: "CI/CD", value: "GitHub Actions", color: "#ef4444" },
            { label: "Auth", value: "JWT + bcrypt", color: "#84cc16" },
            { label: "Emails", value: "Resend API", color: "#f59e0b" },
          ].map((item, i) => (
            <div key={i} style={{ background: "#0d0f14", borderRadius: 8, padding: "10px 12px" }}>
              <div style={{ fontSize: 11, color: "#6b7494", marginBottom: 4 }}>{item.label}</div>
              <div style={{ fontSize: 13, color: item.color, fontWeight: 500 }}>{item.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}