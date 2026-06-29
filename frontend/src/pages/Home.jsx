const apps = [
  { name: 'Patient', description: 'Daily check-ins, journal reflections, and care timeline' },
  { name: 'Counselor', description: 'Caseload insights, alerts, and treatment planning' },
  { name: 'Family', description: 'Support resources and safe communication tools' },
  { name: 'Facility', description: 'Analytics, compliance, and staff guidance' },
];

export default function Home({ onNavigate }) {
  return (
    <section className="page-stack">
      <div className="hero">
        <p className="eyebrow">RecoveryOS</p>
        <h1>Privacy-first recovery coordination for modern care teams.</h1>
        <p className="hero-copy">
          A secure operating system for recovery that brings planning, support workflows, and compliance readiness into one place.
        </p>
        <div className="button-row">
          <button onClick={() => onNavigate('patient')}>Open patient view</button>
          <button onClick={() => onNavigate('counselor')}>Open counselor view</button>
        </div>
      </div>

      <div className="grid">
        {apps.map((app) => (
          <div key={app.name} className="card">
            <h2>{app.name}</h2>
            <p>{app.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
