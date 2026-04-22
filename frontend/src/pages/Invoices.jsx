import { useEffect, useState } from 'react';
import { getInvoices, payInvoice } from '../services/api';

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);

  const load = () => getInvoices().then(r => setInvoices(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const pay = async (id) => {
    await payInvoice(id);
    load();
  };

  const pending = invoices.filter(i => i.status === 'pending').reduce((s,i) => s + parseFloat(i.amount), 0);
  const paid = invoices.filter(i => i.status === 'paid').reduce((s,i) => s + parseFloat(i.amount), 0);

  return (
    <div>
      <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 20 }}>Facturation</div>

      <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, overflow: 'hidden', marginBottom: 16 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #2a3040' }}>
              {['Projet','Montant','Palier','Statut','Échéance','Action'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 16px', fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {invoices.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: 40, color: '#6b7494' }}>Aucune facture — mets à jour un projet pour en générer</td></tr>
            )}
            {invoices.map(inv => (
              <tr key={inv.id} style={{ borderBottom: '1px solid #2a3040' }}>
                <td style={{ padding: '12px 16px' }}>Projet #{inv.project_id}</td>
                <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontWeight: 500 }}>€ {parseFloat(inv.amount).toFixed(0)}</td>
                <td style={{ padding: '12px 16px', color: '#6b7494' }}>{inv.percentage_billed}%</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ fontSize: 10, padding: '3px 8px', borderRadius: 99, background: inv.status === 'paid' ? '#0d3326' : '#3d2a0a', color: inv.status === 'paid' ? '#3ecf8e' : '#f5a623' }}>
                    {inv.status === 'paid' ? 'Payée' : 'En attente'}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', color: '#6b7494' }}>{inv.due_date}</td>
                <td style={{ padding: '12px 16px' }}>
                  {inv.status === 'pending' && (
                    <button onClick={() => pay(inv.id)} style={{ background: '#0d3326', color: '#3ecf8e', border: '1px solid #3ecf8e44', borderRadius: 6, padding: '4px 10px', fontSize: 11, cursor: 'pointer' }}>
                      Marquer payée
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Total en attente</div>
          <div style={{ fontSize: 28, fontWeight: 600, color: '#f5a623', fontFamily: 'monospace' }}>€ {pending.toFixed(0)}</div>
        </div>
        <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: 11, color: '#6b7494', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Total encaissé</div>
          <div style={{ fontSize: 28, fontWeight: 600, color: '#3ecf8e', fontFamily: 'monospace' }}>€ {paid.toFixed(0)}</div>
        </div>
      </div>
    </div>
  );
}