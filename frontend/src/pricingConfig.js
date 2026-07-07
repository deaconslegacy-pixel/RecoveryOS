export const PRICING_CONFIG = {
  subscription: {
    seatRateMonthly: 49,
    annualDiscountRate: 0.1,
  },
  enterprise: {
    baseLicenseFee: 125000,
    maintenanceRate: 0.18,
    deploymentOptions: {
      cloud: { label: 'Cloud hosted', setupFee: 0 },
      self_hosted: { label: 'Self-hosted', setupFee: 15000 },
      hybrid: { label: 'Hybrid environment', setupFee: 25000 },
    },
    complianceOptions: {
      standard: { label: 'Standard care controls', multiplier: 1 },
      hipaa: { label: 'HIPAA enhanced controls', multiplier: 1.1 },
      hipaa_part2: { label: 'HIPAA + 42 CFR Part 2 controls', multiplier: 1.18 },
    },
  },
};
