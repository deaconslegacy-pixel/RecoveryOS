import { useState } from 'react';
import CounselorDashboard from './pages/CounselorDashboard';
import Home from './pages/Home';
import PatientDashboard from './pages/PatientDashboard';

export default function App() {
  const [view, setView] = useState('home');

  return (
    <div className="app-shell">
      <nav className="top-nav">
        <button onClick={() => setView('home')}>RecoveryOS</button>
        <button onClick={() => setView('patient')}>Patient</button>
        <button onClick={() => setView('counselor')}>Counselor</button>
      </nav>

      {view === 'home' ? <Home onNavigate={setView} /> : null}
      {view === 'patient' ? <PatientDashboard /> : null}
      {view === 'counselor' ? <CounselorDashboard /> : null}
    </div>
  );
}
