#!/usr/bin/env bash
set -euo pipefail

# scripts/setup_gcp_for_ci.sh
# Creates Artifact Registry, service account, IAM bindings, and downloads a service-account key.json
# Usage: edit or export PROJECT_ID and REGION then run: ./scripts/setup_gcp_for_ci.sh

PROJECT_ID=${PROJECT_ID:-}
REGION=${REGION:-us-central1}
REPO=${REPO:-recoveryos}
SA_NAME=${SA_NAME:-github-actions-deployer}
CLOUD_RUN_SERVICE=${CLOUD_RUN_SERVICE:-recoveryos-api}

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud is not installed or not on PATH. Install the Google Cloud SDK first: https://cloud.google.com/sdk/docs/install"
  exit 1
fi

if [ -z "$PROJECT_ID" ]; then
  read -rp "Enter GCP project id: " PROJECT_ID
fi

echo "Using PROJECT_ID=$PROJECT_ID"
echo "Using REGION=$REGION"
echo "Using Artifact Registry repo name: $REPO"
echo "Using service account name: $SA_NAME"
echo "Using Cloud Run service name: $CLOUD_RUN_SERVICE"

echo "
Make sure you're authenticated to gcloud with an account that can create resources and IAM bindings."
read -rp "Continue? [Y/n] " confirm
if [[ "$confirm" =~ ^(n|N) ]]; then
  echo "Aborted"
  exit 1
fi

echo "Setting gcloud project to $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

echo "Enabling required APIs..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com iam.googleapis.com --quiet

echo "Creating Artifact Registry (if it doesn't exist)"
if gcloud artifacts repositories describe "$REPO" --location="$REGION" >/dev/null 2>&1; then
  echo "Artifact Registry $REPO already exists in $REGION"
else
  gcloud artifacts repositories create "$REPO" \
    --repository-format=docker --location="$REGION" --description="RecoveryOS Docker repo"
fi

SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Creating service account $SA_EMAIL (if not exists)"
if gcloud iam service-accounts describe "$SA_EMAIL" >/dev/null 2>&1; then
  echo "Service account already exists: $SA_EMAIL"
else
  gcloud iam service-accounts create "$SA_NAME" --display-name="GitHub Actions deployer"
fi

echo "Granting IAM roles to service account (Cloud Run admin, Artifact Registry writer, Service Account User)"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="roles/run.admin" --quiet || true
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="roles/artifactregistry.writer" --quiet || true
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA_EMAIL}" --role="roles/iam.serviceAccountUser" --quiet || true

KEYFILE="key.json"
echo "Creating service account key: $KEYFILE"
gcloud iam service-accounts keys create "$KEYFILE" --iam-account="$SA_EMAIL"

echo "Service account key written to $KEYFILE"
echo "Add the contents of $KEYFILE as the GitHub Actions secret 'GCP_SA_KEY'. You can run the following command if you have 'gh' CLI and the repo is the current directory's origin repo:"
echo
echo "  gh secret set GCP_SA_KEY --body \"\
$(sed -e 's/"/\\"/g' key.json)\""
echo
echo "Also add these repo secrets in GitHub:"
echo "  GCP_PROJECT=$PROJECT_ID" 
echo "  GCP_REGION=$REGION"
echo "  CLOUD_RUN_SERVICE=$CLOUD_RUN_SERVICE"
echo "  DATABASE_URL=<your_database_url>"

echo "
Done. Keep $KEYFILE secure. Consider deleting it after adding to GitHub secrets: rm key.json"
