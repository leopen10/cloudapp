import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, getInvoices, getNotifications } from '../services/api';

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [notifs, setNotifs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getProjects().then(r => setProjects(r.data)).catch(() => {});
    getInvoices().then(r => setInvoices(r.data)).catch(() => {});
    getNotifications().then(r => setNotifs(r.data)).catch(() => {});
  }, []);

  const pending = invoices.filter(i => i.status === 'pending').reduce((s, i) => s + parseFloat(i.amount), 0);
  const unread = notifs.filter(n => !n.read).length;
  const card = { background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 16 };

  return (
    <div>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 20 }}>Bonjour, {localStorage.getItem('username')} 👋</div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 20 }}>
        {[
          { val: projects.filter(p => p.status === 'active').length, lbl: 'Projets actifs', note: 'En cours', col: '#3ecf8e' },
          { val: `€ ${pending.toFixed(0)}`, lbl: 'Factures en cours', note: 'À encaisser', col: '#f5a623' },
          { val: unread, lbl: 'Notifications', note: 'Non lues', col: '#4f7cff' },
          { val: '99%', lbl: 'Disponibilité', note: 'API en ligne', col: '#3ecf8e' },
        ].map((m, i) => (
          <div key={i} style={card}>
            <div style={{ fontSize: 26, fontWeight: 600, color: m.col, fontFamily: 'monospace' }}>{m.val}</div>
            <div style={{ fontSize: 12, color: '#6b7494', margin: '4px 0' }}>{m.lbl}</div>
            <div style={{ fontSize: 11, color: m.col }}>{m.note}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
        <div style={card}>
          <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Projets récents</div>
          {projects.length === 0 && <div style={{ fontSize: 13, color: '#6b7494', textAlign: 'center', padding: 20 }}>Aucun projet encore</div>}
          {projects.slice(0, 4).map(p => (
            <div key={p.id} onClick={() => navigate(`/projects/${p.id}`)}
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #2a3040', cursor: 'pointer' }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{p.name}</div>
                <div style={{ fontSize: 11, color: '#6b7494' }}>{p.client_name} · {p.progress}%</div>
              </div>
              <span style={{ fontSize: 10, padding: '3px 10px', borderRadius: 99, background: p.status === 'active' ? '#0d3326' : '#3d2a0a', color: p.status === 'active' ? '#3ecf8e' : '#f5a623' }}>
                {p.status === 'active' ? 'Actif' : 'En pause'}
              </span>
            </div>
          ))}
        </div>

        <div style={card}>
          <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Dernières notifications</div>
          {notifs.length === 0 && <div style={{ fontSize: 13, color: '#6b7494', textAlign: 'center', padding: 20 }}>Aucune notification</div>}
          {notifs.slice(0, 4).map(n => (
            <div key={n.id} style={{ display: 'flex', gap: 10, padding: '7px 0', borderBottom: '1px solid #2a3040' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: n.type === 'invoice' ? '#f5a623' : '#4f7cff', marginTop: 4, flexShrink: 0 }}></div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{n.title}</div>
                <div style={{ fontSize: 11, color: '#6b7494' }}>{n.message?.slice(0, 60)}...</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}