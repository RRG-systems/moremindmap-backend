# Vercel Deployment Status

## Current Status

Vercel deployment is intentionally disabled during MOREMindMap recovery stabilization.

This repository is currently being used as the GitHub source of truth for:
- project recovery docs
- governance files
- Mini V2 reconstruction planning
- artifact/state preservation

It is not currently ready for production deployment because the app/render pipeline is still being reconstructed.

## Why Deployment Is Disabled

Recent pushes to `origin/main` triggered Vercel production deployment attempts, causing failed deployment emails.

This is expected because the repo currently lacks a finalized production app structure.

## Re-enable Deployment Only After

Deployment should only be re-enabled after:

1. Mini V2 templates exist.
2. Scoring pipeline exists.
3. HTML generation works.
4. PDF generation works.
5. Stripe/Formspree/email flow is wired.
6. Production build command is known and tested.
7. Vercel project settings are intentionally configured.

## GitHub Remains Source of Truth

GitHub remains the source of truth for recovery and production rebuild work.

Vercel should not be treated as authoritative until production deployment is deliberately restored.
