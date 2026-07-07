# Release Notes Template

Use this template for the next release (example: v0.1.1).

## Release Title

RecoveryOS by Deacons Legacy vX.Y.Z

## Release Body

```md
## RecoveryOS by Deacons Legacy: [Release Theme]

[One-paragraph summary of this release and why it matters.]

## Highlights

- [Top user-visible improvement #1]
- [Top user-visible improvement #2]
- [Top user-visible improvement #3]

## What's Changed

### Frontend

- [UI/UX update]
- [Branding/theme/content update]
- [Accessibility or responsiveness update]

### Backend

- [API/storage/security update]
- [Performance or reliability update]

### Documentation

- [README/docs update]
- [Runbook/deployment notes update]

### CI/CD and Operations

- [Workflow, deployment, container, or monitoring update]

## Validation

- Frontend build: [pass/fail + command]
- Backend tests: [pass/fail + command]
- Integration checks: [pass/fail + brief notes]

## Breaking Changes

- None.

OR

- [Describe breaking change]
- [Migration step 1]
- [Migration step 2]

## Known Limitations

- [Known issue #1]
- [Known issue #2]

## Upgrade Notes

1. Pull latest changes on `main`.
2. Rebuild frontend assets and backend image.
3. Apply any environment/config updates.
4. Redeploy and run smoke checks.

## Full Changelog

- [short-sha] - [commit message]
- [short-sha] - [commit message]
```

## Publish Command

```bash
gh release create vX.Y.Z \
  --repo deaconslegacy-pixel/RecoveryOS \
  --title "RecoveryOS by Deacons Legacy vX.Y.Z" \
  --notes-file .github/release-notes-template.md
```

Tip: copy the markdown body into a separate versioned note file before publishing, such as `docs/releases/vX.Y.Z.md`.
