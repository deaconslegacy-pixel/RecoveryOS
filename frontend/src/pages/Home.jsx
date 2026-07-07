const apps = [
  { name: 'Patient', description: 'Daily check-ins, guided reflections, and a clear recovery timeline in one place.' },
  { name: 'Counselor', description: 'Caseload visibility, treatment planning support, and risk-aware coordination tools.' },
  { name: 'Family', description: 'Permission-based updates and compassionate support resources for loved ones.' },
  { name: 'Facility', description: 'Operational insights, compliance-ready reporting, and coordinated care oversight.' },
];

const pricingOptions = [
  {
    name: 'Subscription',
    price: '$49/user/month',
    subtitle: 'Flexible for growing programs and multi-site care teams.',
    features: [
      'Monthly or annual billing options',
      'Continuous updates and standard support',
      'Role-based access for all workspaces',
      'Predictable scaling as patient volume grows',
    ],
    licensing: 'Licensed as a recurring SaaS subscription with active support while subscribed.',
  },
  {
    name: 'Enterprise Lifetime License',
    price: 'From $125,000 one-time',
    subtitle: 'Built for enterprise providers with long-term platform ownership goals.',
    features: [
      'Perpetual platform usage rights',
      'Enterprise deployment and onboarding assistance',
      'Dedicated security and compliance review track',
      'Optional annual maintenance and premium support add-on',
    ],
    licensing: 'Licensed as a perpetual enterprise agreement with optional annual maintenance for upgrades and support.',
  },
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
            <button onClick={() => onNavigate('pricing')}>Open pricing calculator</button>
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

      <section className="pricing-section card wide-card" aria-label="Pricing and licensing">
        <div className="card-header">
          <p className="eyebrow">Pricing and licensing</p>
          <h2>Choose subscription flexibility or enterprise lifetime ownership.</h2>
        </div>
        <p className="pricing-intro">
          RecoveryOS by Deacons Legacy supports both modern subscription delivery and enterprise-grade lifetime licensing.
          Final pricing is tailored by seat count, deployment model, and compliance requirements.
        </p>
        <div className="pricing-grid">
          {pricingOptions.map((plan) => (
            <article key={plan.name} className="pricing-card">
              <p className="pricing-name">{plan.name}</p>
              <h3>{plan.price}</h3>
              <p>{plan.subtitle}</p>
              <ul>
                {plan.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              <p className="pricing-license">{plan.licensing}</p>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}
