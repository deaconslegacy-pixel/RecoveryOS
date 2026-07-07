import { useMemo, useState } from 'react';
import { API_BASE_URL } from './api';
import CounselorDashboard from './pages/CounselorDashboard';
import FacilityDashboard from './pages/FacilityDashboard';
import FamilyDashboard from './pages/FamilyDashboard';
import Home from './pages/Home';
import PatientDashboard from './pages/PatientDashboard';
import Pricing from './pages/Pricing';

const ROLE_OPTIONS = [
  { value: 'patient', label: 'Patient' },
  { value: 'counselor', label: 'Counselor' },
  { value: 'family', label: 'Family' },
  { value: 'facility_admin', label: 'Facility' },
];

export default function App() {
  const [view, setView] = useState('home');
  const [role, setRole] = useState('patient');
  const [userId, setUserId] = useState('demo-patient');
  const [session, setSession] = useState(null);
  const [status, setStatus] = useState('');

  const canAccessDashboard = useMemo(() => ['patient', 'counselor', 'family', 'facility_admin'].includes(role), [role]);

  async function handleLogin(event) {
    event.preventDefault();
    setStatus('Signing in…');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role, user_id: userId }),
      });

      if (!response.ok) {
        throw new Error('Unable to sign in');
      }

      const payload = await response.json();
      setSession({ role, userId, token: payload.token });
      setStatus(`Signed in as ${role} (${userId})`);
      setView(role === 'counselor' ? 'counselor' : role === 'family' ? 'family' : role === 'facility_admin' ? 'facility' : 'patient');
    } catch (error) {
      setStatus(error.message || 'Unable to sign in');
    }
  }

  return (
    <div className="app-shell">
      <nav className="top-nav">
        <div className="top-nav-brand">
          <div className="brand-mark" aria-hidden="true">
            <span className="brand-flame" />
            <span className="brand-wing left" />
            <span className="brand-wing right" />
          </div>
          <div className="brand-title">
            <strong>RecoveryOS</strong>
            <span>by Deacons Legacy</span>
          </div>
        </div>
        <div className="nav-actions">
          <button onClick={() => setView('home')}>Home</button>
          <button onClick={() => setView('pricing')}>Pricing</button>
          <button onClick={() => setView('patient')}>Patient</button>
          <button onClick={() => setView('counselor')}>Counselor</button>
          <button onClick={() => setView('family')}>Family</button>
          <button onClick={() => setView('facility')}>Facility</button>
        </div>
      </nav>

      <div className="auth-card">
        <div className="auth-card-header">
          <p className="eyebrow">Secure care coordination</p>
          <h2>Choose the workspace that fits your role.</h2>
        </div>
        <form onSubmit={handleLogin} className="login-form">
          <label>
            Role
            <select value={role} onChange={(event) => setRole(event.target.value)}>
              {ROLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <label>
            User ID
            <input value={userId} onChange={(event) => setUserId(event.target.value)} />
          </label>
          <button type="submit">Sign in</button>
        </form>
        <p className="status-text">{status || 'Use demo-patient for the patient experience or counselor-1 for the counselor view.'}</p>
      </div>

      {view === 'home' ? <Home onNavigate={setView} /> : null}
      {view === 'pricing' ? <Pricing /> : null}
      {view === 'patient' ? <PatientDashboard session={session} /> : null}
      {view === 'counselor' ? <CounselorDashboard session={session} /> : null}
      {view === 'family' ? <FamilyDashboard session={session} /> : null}
      {view === 'facility' ? <FacilityDashboard session={session} /> : null}
      {!canAccessDashboard && view !== 'home' ? <p className="status-text">Select a role to open a dashboard.</p> : null}
    </div>
  );
}
