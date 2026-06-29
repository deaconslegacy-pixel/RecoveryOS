const API_BASE_URL = 'http://127.0.0.1:8000';

export async function fetchHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) throw new Error('Unable to reach backend');
  return response.json();
}

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE_URL}/patient/dashboard`, {
    headers: { Authorization: 'Bearer token-demo-patient' },
  });
  if (!response.ok) throw new Error('Unable to load patient dashboard');
  return response.json();
}

export async function fetchTimeline() {
  const response = await fetch(`${API_BASE_URL}/patient/timeline?patient_id=demo-patient`, {
    headers: { Authorization: 'Bearer token-demo-patient' },
  });
  if (!response.ok) throw new Error('Unable to load patient timeline');
  return response.json();
}
