import { useState, useEffect } from 'react';
import { getNotifications, markRead } from '../services/api';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    getNotifications().then(r => setNotifications(r.data)).catch(() => {});
  }, []);

  const handleRead = async (id) => {
    await markRead(id);
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const typeColor = { invoice: '#f59e0b', project_update: '#4f7cff', info: '#3ecf8e' };

  return (
    <div>
      <h2 style={{ fontSize: 22, fontWeight: 600, marginBottom: 24 }}>Notifications</h2>
      {notifications.length === 0 && <p style={{ color: '#6b7494' }}>Aucune notification.</p>}
      {notifications.map(n => (
        <div key={n.id} style={{
          background: n.read ? '#161a23' : '#1a1f2e',
          border: `1px solid ${n.read ? '#2a3040' : '#2e3a5e'}`,
          borderRadius: 10, padding: '14px 18px', marginBottom: 10,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: typeColor[n.type] || '#6b7494', display: 'inline-block' }}></span>
              <span style={{ fontWeight: 500, fontSize: 14 }}>{n.title}</span>
              {!n.read && <span style={{ background: '#4f7cff22', color: '#4f7cff', fontSize: 10, padding: '2px 6px', borderRadius: 4 }}>Nouveau</span>}
            </div>
            <div style={{ color: '#6b7494', fontSize: 13 }}>{n.message}</div>
            <div style={{ color: '#3a4060', fontSize: 11, marginTop: 4 }}>{new Date(n.created_at).toLocaleString('fr-FR')}</div>
          </div>
          {!n.read && (
            <button onClick={() => handleRead(n.id)} style={{
              background: '#1e2d5e', color: '#4f7cff', border: 'none',
              borderRadius: 6, padding: '6px 12px', fontSize: 12, cursor: 'pointer'
            }}>Marquer lu</button>
          )}
        </div>
      ))}
    </div>
  );
}