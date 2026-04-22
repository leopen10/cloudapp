import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects, getClients, createProject } from '../services/api';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ client_id: '', name: '', description: '', budget: '', end_date: '' });
  const navigate = useNavigate();

  const load = () => {
    getProjects().then(r => setProjects(r.data)).catch(() => {});
    getClients().then(r => setClients(r.data)).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const submit = async () => {
    await createProject({ ...form, client_id: parseInt(form.client_id), budget: parseFloat(form.budget) });
    setShowModal(false);
    setForm({ client_id: '', name: '', description: '', budget: '', end_date: '' });
    load();
  };

  const inp = { width: '100%', background: '#0d0f14', border: '1px solid #2a3040', borderRadius: 8, padding: '8px 12px', color: '#e8eaf0', fontSize: 13, marginTop: 4, outline: 'none' };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div style={{ fontSize: 22, fontWeight: 600 }}>Mes projets</div>
        <button onClick={() => setShowModal(true)} style={{ background: '#4f7cff', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>
          + Nouveau projet
        </button>
      </div>

      {projects.length === 0 && <div style={{ textAlign: 'center', padding: 60, color: '#6b7494', fontSize: 14 }}>Aucun projet — crée le premier !</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
        {projects.map(p => (
          <div key={p.id} onClick={() => navigate(`/projects/${p.id}`)}
            style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 16, cursor: 'pointer', transition: '.2s' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{p.name}</div>
                <div style={{ fontSize: 12, color: '#6b7494', marginTop: 2 }}>{p.client_name}</div>
              </div>
              <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 99, height: 'fit-content', background: p.status === 'active' ? '#0d3326' : '#3d2a0a', color: p.status === 'active' ? '#3ecf8e' : '#f5a623' }}>
                {p.status === 'active' ? 'Actif' : 'En pause'}
              </span>
            </div>
            <div style={{ fontSize: 20, fontWeight: 600, color: '#3ecf8e', fontFamily: 'monospace', marginBottom: 10 }}>€ {parseFloat(p.budget).toLocaleString('fr-FR')}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#6b7494', marginBottom: 4 }}>
              <span>Avancement</span><span>{p.progress}%</span>
            </div>
            <div style={{ height: 4, background: '#2a3040', borderRadius: 99 }}>
              <div style={{ height: 4, width: `${p.progress}%`, background: '#3ecf8e', borderRadius: 99 }}></div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 16, padding: 32, width: 440 }}>
            <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>Nouveau projet</div>
            {[['name','Nom du projet','text'],['description','Description','text'],['budget','Budget (€)','number'],['end_date','Date de livraison','date']].map(([k,l,t]) => (
              <div key={k} style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, color: '#6b7494' }}>{l}</label>
                <input type={t} style={inp} value={form[k]} onChange={e => setForm({...form, [k]: e.target.value})} />
              </div>
            ))}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 12, color: '#6b7494' }}>Client</label>
              <select style={inp} value={form.client_id} onChange={e => setForm({...form, client_id: e.target.value})}>
                <option value="">-- Sélectionner --</option>
                {clients.map(c => <option key={c.id} value={c.id}>{c.company_name}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: '1px solid #2a3040', color: '#6b7494', borderRadius: 8, padding: '8px 16px', cursor: 'pointer' }}>Annuler</button>
              <button onClick={submit} style={{ background: '#4f7cff', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>Créer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}