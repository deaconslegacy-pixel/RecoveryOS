import { useMemo, useState } from 'react';
import { PRICING_CONFIG } from '../pricingConfig';

const SUBSCRIPTION = PRICING_CONFIG.subscription;
const ENTERPRISE = PRICING_CONFIG.enterprise;

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

export default function Pricing() {
  const [seats, setSeats] = useState(50);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [deployment, setDeployment] = useState('cloud');
  const [compliance, setCompliance] = useState('standard');
  const [includeMaintenance, setIncludeMaintenance] = useState(true);

  const normalizedSeats = Number.isNaN(Number(seats)) ? 0 : Math.max(1, Number(seats));
  const monthlySubscription = normalizedSeats * SUBSCRIPTION.seatRateMonthly;
  const annualSubscription = monthlySubscription * 12 * (1 - SUBSCRIPTION.annualDiscountRate);

  const complianceMultiplier = ENTERPRISE.complianceOptions[compliance].multiplier;
  const deploymentFee = ENTERPRISE.deploymentOptions[deployment].setupFee;
  const enterpriseBase = ENTERPRISE.baseLicenseFee * complianceMultiplier + deploymentFee;
  const annualMaintenance = includeMaintenance ? enterpriseBase * ENTERPRISE.maintenanceRate : 0;
  const enterpriseYearOne = enterpriseBase + annualMaintenance;

  const subscriptionQuote = useMemo(() => {
    if (billingCycle === 'annual') {
      return {
        label: 'Estimated annual subscription',
        total: annualSubscription,
        detail: `${formatCurrency(monthlySubscription)} monthly equivalent before annual discount`,
      };
    }

    return {
      label: 'Estimated monthly subscription',
      total: monthlySubscription,
      detail: `${formatCurrency(annualSubscription)} if billed annually with 10% discount`,
    };
  }, [annualSubscription, billingCycle, monthlySubscription]);

  return (
    <section className="page-stack">
      <div className="card wide-card">
        <div className="card-header">
          <p className="eyebrow">Commercial options</p>
          <h2>Pricing calculator for subscription or enterprise lifetime licensing</h2>
        </div>
        <p>
          Use this estimator to compare recurring subscription costs versus a perpetual enterprise license.
          Final quotes are tailored to integration scope, legal requirements, and deployment constraints.
        </p>
      </div>

      <div className="pricing-calculator-grid">
        <article className="card">
          <div className="card-header">
            <p className="eyebrow">Subscription</p>
            <h2>$49 per user/month</h2>
          </div>

          <label className="calc-label">
            Seats
            <input
              className="calc-input"
              type="number"
              min="1"
              value={seats}
              onChange={(event) => setSeats(event.target.value)}
            />
          </label>

          <label className="calc-label">
            Billing cycle
            <select
              className="calc-input"
              value={billingCycle}
              onChange={(event) => setBillingCycle(event.target.value)}
            >
              <option value="monthly">Monthly</option>
              <option value="annual">Annual (10% discount)</option>
            </select>
          </label>

          <div className="quote-box">
            <p className="quote-label">{subscriptionQuote.label}</p>
            <h3>{formatCurrency(subscriptionQuote.total)}</h3>
            <p>{subscriptionQuote.detail}</p>
          </div>
        </article>

        <article className="card">
          <div className="card-header">
            <p className="eyebrow">Enterprise lifetime</p>
            <h2>From $125,000 one-time</h2>
          </div>

          <label className="calc-label">
            Deployment model
            <select
              className="calc-input"
              value={deployment}
              onChange={(event) => setDeployment(event.target.value)}
            >
                {Object.entries(ENTERPRISE.deploymentOptions).map(([value, option]) => (
                <option key={value} value={value}>{option.label}</option>
              ))}
            </select>
          </label>

          <label className="calc-label">
            Compliance profile
            <select
              className="calc-input"
              value={compliance}
              onChange={(event) => setCompliance(event.target.value)}
            >
                {Object.entries(ENTERPRISE.complianceOptions).map(([value, option]) => (
                <option key={value} value={value}>{option.label}</option>
              ))}
            </select>
          </label>

          <label className="calc-checkbox">
            <input
              type="checkbox"
              checked={includeMaintenance}
              onChange={(event) => setIncludeMaintenance(event.target.checked)}
            />
            Include optional annual maintenance (18%)
          </label>

          <div className="quote-box">
            <p className="quote-label">Estimated enterprise year-one total</p>
            <h3>{formatCurrency(enterpriseYearOne)}</h3>
            <p>
              Base perpetual license: {formatCurrency(enterpriseBase)}
              {includeMaintenance ? ` + ${formatCurrency(annualMaintenance)} maintenance` : ''}
            </p>
          </div>
        </article>
      </div>
    </section>
  );
}
