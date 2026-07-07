export default function CounselorDashboard() {
  return (
    <section className="page-stack">
      <div className="card wide-card">
        <div className="card-header">
          <p className="eyebrow">RecoveryOS workspace</p>
          <h2>Counselor dashboard</h2>
        </div>
        <p>Caseload overview, alerts, planning notes, and compliance summaries will appear here.</p>
      </div>
      <div className="card wide-card">
        <h2>Priority alerts</h2>
        <ul>
          <li>Demo Patient — missed two check-ins</li>
          <li>Alex Chen — low recent engagement</li>
        </ul>
      </div>
    </section>
  );
}
