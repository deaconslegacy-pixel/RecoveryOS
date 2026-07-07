import { useEffect, useState } from 'react';
import { fetchDashboard, fetchTimeline } from '../api';

export default function PatientDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [dashboardData, timelineData] = await Promise.all([fetchDashboard(), fetchTimeline()]);
        setDashboard(dashboardData);
        setTimeline(timelineData);
      } catch (err) {
        setError(err.message || 'Unable to load patient dashboard');
      }
    }

    loadData();
  }, []);

  return (
    <section className="page-stack">
      <div className="card wide-card">
        <div className="card-header">
          <p className="eyebrow">RecoveryOS workspace</p>
          <h2>Patient dashboard</h2>
        </div>
        {dashboard ? (
          <>
            <p><strong>Patient:</strong> {dashboard.patient_id}</p>
            <p><strong>Focus:</strong> {dashboard.focus}</p>
            <ul>
              {dashboard.daily_goals.map((goal) => (
                <li key={goal}>{goal}</li>
              ))}
            </ul>
          </>
        ) : (
          <p>Loading…</p>
        )}
      </div>

      <div className="card wide-card">
        <h2>Care timeline</h2>
        {timeline ? (
          <ul>
            {timeline.events.map((event) => (
              <li key={`${event.kind}-${event.timestamp}`}>
                <strong>{event.kind}</strong> — {event.timestamp}
              </li>
            ))}
          </ul>
        ) : (
          <p>Loading…</p>
        )}
        {error ? <p className="error">{error}</p> : null}
      </div>
    </section>
  );
}
