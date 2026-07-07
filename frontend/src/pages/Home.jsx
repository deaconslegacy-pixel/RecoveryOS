const apps = [
  { name: 'Patient', description: 'Daily check-ins, guided reflections, and a clear recovery timeline in one place.' },
  { name: 'Counselor', description: 'Caseload visibility, treatment planning support, and risk-aware coordination tools.' },
  { name: 'Family', description: 'Permission-based updates and compassionate support resources for loved ones.' },
  { name: 'Facility', description: 'Operational insights, compliance-ready reporting, and coordinated care oversight.' },
];

export default function Home({ onNavigate }) {
  return (
    <section className="page-stack">
      <div className="hero hero-split">
        <div className="hero-copy-block">
          <p className="eyebrow">RecoveryOS by Deacons Legacy</p>
          <h1>Rise stronger every day with coordinated recovery care.</h1>
          <p className="hero-copy">
            RecoveryOS by Deacons Legacy unifies daily support, clinical workflows, and family collaboration in one secure platform designed around renewal and progress.
          </p>
          <div className="button-row">
            <button onClick={() => onNavigate('patient')}>Explore patient experience</button>
            <button onClick={() => onNavigate('counselor')}>See counselor workflow</button>
          </div>
        </div>
        <div className="phoenix-card" aria-label="Phoenix rising as a recovery symbol">
          <div className="phoenix-glow" />
          <div className="phoenix-crest">
            <span className="phoenix-core" />
            <span className="phoenix-wing left" />
            <span className="phoenix-wing right" />
          </div>
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
