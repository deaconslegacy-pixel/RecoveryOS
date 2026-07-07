# RecoveryOS by Deacons Legacy

RecoveryOS by Deacons Legacy is a privacy-first, recovery-oriented operating system concept for coordinating care across patients, counselors, families, facilities, and intelligent support systems.

## Vision

RecoveryOS is designed to support recovery journeys with secure, role-aware tools that help patients stay engaged, counselors manage risk and treatment planning, families stay informed with permission, and facilities monitor outcomes and compliance.

## Core Features

### 1. Patient App
- AI recovery companion
- Daily check-ins
- Journaling
- Crisis support tools
- Goals and progress tracking

### 2. Counselor Dashboard
- Caseload overview
- Risk alerts
- AI-supported documentation
- Treatment planning
- Homework and engagement planning

### 3. Family App
- Educational resources
- Communication tools
- Permission-based progress updates
- Family support materials

### 4. Facility Dashboard
- Analytics and outcomes reporting
- Compliance monitoring
- Operational alerts
- Staff insights

### 5. AI Intelligence Layer
- Predictive relapse scoring
- Engagement analysis
- Automated summaries
- Personalized recommendations

## Current Implementation Status

This repository currently contains a FastAPI-based backend scaffold that exposes endpoints for the five app areas and supports the foundational workflows described above.

## Branding Update (July 2026)

The frontend now reflects the product identity as **RecoveryOS by Deacons Legacy** and includes a phoenix-inspired recovery theme.

- Top-level app branding now displays RecoveryOS by Deacons Legacy.
- The home experience includes updated copy centered on renewal and coordinated recovery.
- A phoenix-inspired visual motif is applied across hero and navigation elements.
- Dashboard headers across patient, counselor, family, and facility views now use the full brand byline.

## Pricing and Licensing Model

RecoveryOS by Deacons Legacy is positioned with two commercial options so organizations can choose operating flexibility or long-term ownership.

### Subscription plan

- Indicative pricing: $49 per user per month
- Best fit: teams that want fast rollout, predictable monthly cost, and evergreen updates
- Includes: active support, ongoing feature releases, and standard security updates while subscribed

### Enterprise lifetime license

- Indicative pricing: starts at $125,000 one-time
- Best fit: enterprise providers and multi-facility organizations with long-term platform ownership goals
- Includes: perpetual usage rights under enterprise agreement terms
- Optional add-on: annual maintenance and premium support for continued upgrades and service coverage

Final commercial terms should be set through a formal quote based on seats, deployment model, integration scope, and compliance requirements.

## Security and Privacy Principles

RecoveryOS is being built with a strict privacy-first posture. The following principles guide the architecture:

- Least-privilege access for each role
- Minimal data collection and retention
- Encryption in transit and at rest where applicable
- Role-based access control for patient, counselor, family, and facility contexts
- Audit logging for sensitive actions
- Strong consent and permissions handling for family access and data sharing
- Secure error handling and response hardening

## Security Controls Implemented

The current implementation includes basic defensive response headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: no camera, microphone, or geolocation access

## Legal and Privacy Considerations

This system is intended for sensitive behavioral health and recovery contexts. Any production deployment must be reviewed with legal, compliance, and privacy experts to ensure alignment with applicable laws, including but not limited to:

- HIPAA (U.S. Health Insurance Portability and Accountability Act)
- 42 CFR Part 2 (federal confidentiality rules for substance use disorder records)
- State behavioral health privacy laws
- State medical record confidentiality requirements
- State consumer privacy statutes and breach notification laws
- Applicable telehealth and electronic record regulations
- Contractual obligations and internal governance requirements

## Recommended Compliance Checklist

Before production use, confirm that the system includes:

1. Privacy notice and consent language
2. Data retention and deletion policies
3. Business associate agreement (if applicable)
4. Security risk assessment
5. Incident response and breach notification procedures
6. Access logging and monitoring
7. Encryption standards for data at rest and in transit
8. Secure backup and disaster recovery plan
9. Third-party vendor review for any hosted services
10. Legal review for jurisdiction-specific handling of behavioral health data

## Development

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/python -m app
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

### Run tests

```bash
.venv/bin/python -m pytest -q
```

## Deployment

### Docker

```bash
docker build -t recoveryos .
docker run -p 8000:8000 recoveryos
```

### Website integration

If you are integrating RecoveryOS with an existing website such as `deaconslegacy.site`, use the following pattern:

- On your backend service, set `ALLOWED_ORIGINS` to the website domain:
  - `ALLOWED_ORIGINS=https://deaconslegacy.site`
- If the frontend is served from the same backend origin, leave `VITE_API_BASE_URL` blank when building production.
- For local frontend development, create `frontend/.env` with:
  ```env
  VITE_API_BASE_URL=http://127.0.0.1:8000
  ```
- For a separate frontend host, set `VITE_API_BASE_URL` to your backend URL, for example:
  `VITE_API_BASE_URL=https://api.deaconslegacy.site`

The frontend now uses this env var and will call `/auth/login` relative to the configured backend origin.

### Platform options

The service is also ready for deployment to Render, Fly.io, Railway, Azure App Service, or similar platforms using the provided Procfile and Dockerfile.

## Notes

This repository is an early-stage technical foundation. It is not a substitute for legal advice, compliance review, or a completed production-ready platform.

## Implementation status & quick reference

- Backend server: `app/main.py` (FastAPI). Runs on Gunicorn + Uvicorn worker in production.
- Storage: `app/storage.py` now uses SQLAlchemy and reads `DATABASE_URL` for production; falls back to local SQLite at `data/recoveryos.db`.
- Frontend: `frontend/` (Vite + React) with a phoenix-inspired RecoveryOS by Deacons Legacy visual theme. Docker multi-stage build compiles frontend and copies the `dist` into the image at `/app/frontend_dist`.
- Docker: multi-stage build, non-root `app` user, `HEALTHCHECK` configured. See `Dockerfile`.
- CI: `.github/workflows/ci.yml` runs tests, builds the frontend, and pushes the Docker image to GitHub Container Registry (`ghcr.io`).

## How to build & run locally (recommended)

1. Build the Docker image (recommended for parity with production):

```bash
docker build -t recoveryos:local .
docker run --rm -p 8000:8000 recoveryos:local
```

2. Or run backend + frontend separately for development:

Backend:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (dev):
```bash
cd frontend
npm install
npm run dev
```

API endpoints remain under `/` (e.g. `/health`, `/auth/login`, `/patient/timeline`). When the Docker image contains a built frontend, the static app is served at `/`.

## CI / Registry notes

- The workflow uses the repository `GITHUB_TOKEN` to publish the image to GHCR as `ghcr.io/<owner>/<repo>:latest` on pushes to `main`.
- To pull the image from other contexts, you may need to grant package read permissions or create a PAT for external access.

## Release workflow

- Reuse `.github/release-notes-template.md` for each new GitHub release.
- Replace `vX.Y.Z` placeholders with the target tag and update each section before publishing.
- Recommended publish flow:
  1. `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
  2. `git push origin main --tags`
  3. `gh release create vX.Y.Z --repo deaconslegacy-pixel/RecoveryOS --title "RecoveryOS by Deacons Legacy vX.Y.Z" --notes-file .github/release-notes-template.md`

## Next steps (I can help with any of these)

- Scaffold Alembic migrations and add an initial migration.
- Add a deploy step to the GitHub Actions workflow for Cloud Run, ECS (ECR), or Render.
- Add authentication (OAuth / OIDC) or integrate with an identity provider.
- Draft a versioned release notes file for `v0.1.1` using the new template.

---

If you'd like, tell me which deployment target you prefer and I will scaffold the deploy steps in CI and produce any required environment/configuration templates.
