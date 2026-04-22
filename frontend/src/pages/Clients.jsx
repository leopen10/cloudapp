import { useEffect, useState } from 'react';
import { getClients, createClient } from '../services/api';

export default function Clients() {
  const [clients, setClients] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ company_name: '', email: '', phone: '' });

  const load = () => getClients().then(r => setClients(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const submit = async () => {
    await createClient(form);
    setShowModal(false);
    setForm({ company_name: '', email: '', phone: '' });
    load();
  };

  const inp = { width: '100%', background: '#0d0f14', border: '1px solid #2a3040', borderRadius: 8, padding: '8px 12px', color: '#e8eaf0', fontSize: 13, marginTop: 4, outline: 'none' };
  const colors = ['#4f7cff','#3ecf8e','#f5a623','#9b6dff','#ff5e6c'];
  const bgs = ['#1e2d5e','#0d3326','#3d2a0a','#2a1a3e','#3d1219'];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div style={{ fontSize: 22, fontWeight: 600 }}>Clients</div>
        <button onClick={() => setShowModal(true)} style={{ background: '#4f7cff', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>
          + Nouveau client
        </button>
      </div>

      {clients.length === 0 && <div style={{ textAlign: 'center', padding: 60, color: '#6b7494', fontSize: 14 }}>Aucun client — ajoute le premier !</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
        {clients.map((c, i) => (
          <div key={c.id} style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 16 }}>
            <div style={{ width: 44, height: 44, borderRadius: '50%', background: bgs[i%5], color: colors[i%5], display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 600, marginBottom: 10 }}>
              {c.company_name.slice(0,2).toUpperCase()}
            </div>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{c.company_name}</div>
            <div style={{ fontSize: 12, color: '#6b7494', marginBottom: 6 }}>{c.email}</div>
            {c.phone && <div style={{ fontSize: 12, color: '#6b7494' }}>{c.phone}</div>}
          </div>
        ))}
      </div>

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 16, padding: 32, width: 420 }}>
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>Nouveau client</div>
            {[['company_name',"Nom de l'entreprise"],['email','Email'],['phone','Téléphone']].map(([k,l]) => (
              <div key={k} style={{ marginBottom: 14 }}>
                <label style={{ fontSize: 12, color: '#6b7494' }}>{l}</label>
                <input style={inp} value={form[k]} onChange={e => setForm({...form, [k]: e.target.value})} />
              </div>
            ))}
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 8 }}>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: '1px solid #2a3040', color: '#6b7494', borderRadius: 8, padding: '8px 16px', cursor: 'pointer' }}>Annuler</button>
              <button onClick={submit} style={{ background: '#4f7cff', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>Créer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}