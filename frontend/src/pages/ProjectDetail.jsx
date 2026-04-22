import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, updateProject, getInvoicesByProject } from '../services/api';

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [progress, setProgress] = useState(0);
  const [msg, setMsg] = useState('');

  const load = () => {
    getProject(id).then(r => { setProject(r.data); setProgress(r.data.progress); }).catch(() => {});
    getInvoicesByProject(id).then(r => setInvoices(r.data)).catch(() => {});
  };
  useEffect(() => { load(); }, [id]);

  const save = async () => {
    const res = await updateProject(id, { progress });
    const inv = res.data.new_invoices || 0;
    setMsg(inv > 0 ? `✅ ${inv} facture(s) générée(s) automatiquement ! Client notifié.` : '✅ Avancement mis à jour. Client notifié.');
    load();
  };

  if (!project) return <div style={{ padding: 32, color: '#6b7494' }}>Chargement...</div>;

  const paliers = [25, 50, 75, 100];
  const billedPct = invoices.map(i => i.percentage_billed);
  const nextPalier = paliers.find(p => progress >= p && !billedPct.includes(p));

  return (
    <div>
      <button onClick={() => navigate('/projects')} style={{ background: 'none', border: 'none', color: '#6b7494', fontSize: 13, cursor: 'pointer', marginBottom: 16 }}>
        ← Retour aux projets
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16 }}>
        <div>
          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 20, marginBottom: 12 }}>
            <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 4 }}>{project.name}</div>
            <div style={{ fontSize: 13, color: '#6b7494', marginBottom: 4 }}>{project.client_name}</div>
            <div style={{ fontSize: 13, color: '#6b7494', marginBottom: 16 }}>{project.description}</div>
            <div style={{ fontSize: 36, fontWeight: 700, color: '#3ecf8e', fontFamily: 'monospace' }}>{project.progress}%</div>
            <div style={{ height: 8, background: '#2a3040', borderRadius: 99, margin: '10px 0 6px' }}>
              <div style={{ height: 8, width: `${project.progress}%`, background: '#3ecf8e', borderRadius: 99, transition: '1s' }}></div>
            </div>
            <div style={{ fontSize: 12, color: '#6b7494' }}>Budget : € {parseFloat(project.budget).toLocaleString('fr-FR')} · Facturé : € {(project.budget * project.progress / 100).toFixed(0)}</div>
          </div>

          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 20, marginBottom: 12 }}>
            <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Étapes de facturation</div>
            {paliers.map(p => (
              <div key={p} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0', borderBottom: '1px solid #2a3040' }}>
                <div style={{ width: 22, height: 22, borderRadius: '50%', background: project.progress >= p ? '#3ecf8e' : '#2a3040', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, color: project.progress >= p ? '#fff' : '#6b7494' }}>
                  {project.progress >= p ? '✓' : p}
                </div>
                <div style={{ flex: 1, fontSize: 13 }}>Palier {p}% atteint</div>
                <span style={{ fontSize: 12, fontFamily: 'monospace', color: '#6b7494' }}>€ {(project.budget * 0.25).toFixed(0)}</span>
                {billedPct.includes(p) && <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 99, background: '#0d3326', color: '#3ecf8e' }}>Facturé</span>}
              </div>
            ))}
          </div>

          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 20 }}>
            <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Informations</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 13 }}>
              <div><div style={{ color: '#6b7494', fontSize: 11 }}>Budget</div><div style={{ fontWeight: 500 }}>€ {parseFloat(project.budget).toLocaleString('fr-FR')}</div></div>
              <div><div style={{ color: '#6b7494', fontSize: 11 }}>Statut</div><div style={{ fontWeight: 500 }}>{project.status}</div></div>
              <div><div style={{ color: '#6b7494', fontSize: 11 }}>Début</div><div style={{ fontWeight: 500 }}>{project.start_date || '—'}</div></div>
              <div><div style={{ color: '#6b7494', fontSize: 11 }}>Livraison</div><div style={{ fontWeight: 500 }}>{project.end_date || '—'}</div></div>
            </div>
          </div>
        </div>

        <div>
          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 20, marginBottom: 12 }}>
            <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Mettre à jour</div>
            <input type="range" min="0" max="100" value={progress} onChange={e => setProgress(parseInt(e.target.value))}
              style={{ width: '100%', accentColor: '#4f7cff', marginBottom: 8 }} />
            <div style={{ fontSize: 28, fontWeight: 700, textAlign: 'center', color: '#4f7cff', fontFamily: 'monospace', marginBottom: 8 }}>{progress}%</div>
            {nextPalier && <div style={{ fontSize: 12, color: '#f5a623', textAlign: 'center', marginBottom: 8 }}>
              → Générera une facture de € {(project.budget * 0.25).toFixed(0)}
            </div>}
            <button onClick={save} style={{ width: '100%', background: '#4f7cff', color: '#fff', border: 'none', borderRadius: 8, padding: 10, fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>
              Mettre à jour et notifier
            </button>
            {msg && <div style={{ marginTop: 10, fontSize: 12, color: '#3ecf8e', background: '#0d3326', border: '1px solid #3ecf8e44', borderRadius: 8, padding: 10 }}>{msg}</div>}
          </div>

          <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 20 }}>
            <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 }}>Factures générées</div>
            {invoices.length === 0 && <div style={{ fontSize: 13, color: '#6b7494', textAlign: 'center', padding: 20 }}>Aucune facture encore</div>}
            {invoices.map(inv => (
              <div key={inv.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #2a3040' }}>
                <div>
                  <div style={{ fontSize: 13, fontFamily: 'monospace', fontWeight: 500 }}>€ {parseFloat(inv.amount).toFixed(0)}</div>
                  <div style={{ fontSize: 11, color: '#6b7494' }}>{inv.percentage_billed}% du projet</div>
                </div>
                <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 99, background: inv.status === 'paid' ? '#0d3326' : '#3d2a0a', color: inv.status === 'paid' ? '#3ecf8e' : '#f5a623' }}>
                  {inv.status === 'paid' ? 'Payée' : 'En attente'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}