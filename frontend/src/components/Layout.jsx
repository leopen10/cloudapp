import { Outlet, NavLink, useNavigate } from 'react-router-dom';

export default function Layout() {
  const navigate = useNavigate();
  const username = localStorage.getItem('username') || 'Admin';

  const logout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const linkStyle = ({ isActive }) => ({
    display: 'flex', alignItems: 'center', gap: 10,
    padding: '8px 12px', borderRadius: 8, fontSize: 13,
    color: isActive ? '#4f7cff' : '#6b7494',
    background: isActive ? '#1e2d5e' : 'none',
    fontWeight: isActive ? 500 : 400,
    textDecoration: 'none', marginBottom: 2, transition: '.15s'
  });

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0d0f14', color: '#e8eaf0', fontFamily: 'DM Sans, sans-serif' }}>
      <div style={{ width: 200, background: '#161a23', borderRight: '1px solid #2a3040', padding: '20px 10px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 24, paddingLeft: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#4f7cff' }}></div>CloudApp
        </div>
        <NavLink to="/" end style={linkStyle}>Vue d'ensemble</NavLink>
        <NavLink to="/projects" style={linkStyle}>Mes projets</NavLink>
        <NavLink to="/invoices" style={linkStyle}>Factures</NavLink>
       <NavLink to="/clients" style={linkStyle}>Clients</NavLink>
<NavLink to="/notifications" style={linkStyle}>Notifications</NavLink>
<NavLink to="/architecture" style={linkStyle}>Architecture</NavLink>
<NavLink to="/monitoring" style={linkStyle}>Monitoring</NavLink>
        <div style={{ marginTop: 'auto', padding: '10px 12px', fontSize: 12, color: '#6b7494' }}>
          <div style={{ color: '#e8eaf0', marginBottom: 4, fontWeight: 500 }}>{username}</div>
          <div style={{ color: '#3ecf8e', cursor: 'pointer' }} onClick={logout}>● Déconnexion</div>
        </div>
      </div>
      <div style={{ flex: 1, overflow: 'auto', padding: 32 }}>
        <Outlet />
      </div>
    </div>
  );
}