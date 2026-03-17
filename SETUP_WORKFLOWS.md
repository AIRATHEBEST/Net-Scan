# Setting Up GitHub Actions Workflows

The GitHub App token used by this integration does not have the `workflows` permission
required to push `.github/workflows/` files via git. You need to add these manually.

## Option 1 — GitHub Web UI (Easiest)

1. Go to https://github.com/AIRATHEBEST/Net-Scan
2. Click **Add file → Create new file**
3. Type `.github/workflows/ci.yml` as the filename
4. Paste the content from the local file (see below)
5. Repeat for each workflow file

## Option 2 — Personal Access Token (PAT)

1. Go to https://github.com/settings/tokens/new
2. Select **repo** + **workflow** scopes
3. Generate token and copy it
4. Run:
   ```bash
   git remote set-url origin https://YOUR_PAT@github.com/AIRATHEBEST/Net-Scan.git
   git add .github/
   git commit -m "ci: add GitHub Actions workflows"
   git push origin main
   ```

## Workflow Files Location

All workflow files are ready locally at:
- `.github/workflows/ci.yml`        — Full integration check on every PR and push
- `.github/workflows/frontend.yml`  — Build + deploy to Vercel on push to main
- `.github/workflows/backend.yml`   — Test + deploy to Railway on push to main
- `.github/workflows/agent.yml`     — Build + push Docker image to Docker Hub
- `.github/workflows/mobile.yml`    — Expo EAS build for iOS/Android

## Required GitHub Secrets

After adding the workflows, add these secrets at:
https://github.com/AIRATHEBEST/Net-Scan/settings/secrets/actions

| Secret | Description |
|--------|-------------|
| `VERCEL_TOKEN` | Vercel personal access token |
| `VERCEL_ORG_ID` | Vercel organisation ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |
| `VITE_API_URL` | Railway backend URL |
| `RAILWAY_TOKEN` | Railway API token |
| `RAILWAY_SERVICE_ID` | Railway service ID |
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EXPO_TOKEN` | Expo account token |
