import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('leonel@cloudapp.io');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await login({ email, password });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('username', res.data.username);
      localStorage.setItem('role', res.data.role);
      navigate('/');
    } catch {
      setError('Email ou mot de passe incorrect');
    }
  };

  const inp = { width: '100%', background: '#0d0f14', border: '1px solid #2a3040', borderRadius: 8, padding: '10px 14px', color: '#e8eaf0', fontSize: 14, marginTop: 6, outline: 'none' };

  return (
    <div style={{ minHeight: '100vh', background: '#0d0f14', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'DM Sans, sans-serif' }}>
      <div style={{ background: '#161a23', border: '1px solid #2a3040', borderRadius: 16, padding: 40, width: 400 }}>
        <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 8, color: '#e8eaf0' }}>CloudApp</div>
        <div style={{ fontSize: 14, color: '#6b7494', marginBottom: 28 }}>Connectez-vous à votre espace</div>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 12, color: '#6b7494' }}>Email</label>
            <input style={inp} value={email} onChange={e => setEmail(e.target.value)} type="email" />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: 12, color: '#6b7494' }}>Mot de passe</label>
            <input style={inp} value={password} onChange={e => setPassword(e.target.value)} type="password" />
          </div>
          {error && <div style={{ color: '#ff5e6c', fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button type="submit" style={{ width: '100%', background: '#4f7cff', color: '#fff', border: 'none', borderRadius: 8, padding: 12, fontSize: 14, fontWeight: 500, cursor: 'pointer' }}>
            Se connecter
          </button>
        </form>
      </div>
    </div>
  );
}