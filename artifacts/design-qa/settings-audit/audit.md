# Multilingual and Connections Hub audit

## Scope and evidence

The audit used the authenticated persisted Demo tenant at
`http://127.0.0.1:8795/app`, not a static mock. It covered Briefing, the former
Accounts surface, the Runtime key dialog, Pilot readiness, all four new
Connections Hub sections, both locales, both themes, and 1280, 390, and 320px
viewports.

Before evidence:

- `01-briefing-mixed-language.png`
- `02-accounts-existing-connections.png`
- `03-runtime-key-dialog.png`
- `04-runtime-readiness.png`

Final evidence:

- `08-connections-zh-mobile-390-top.png`
- `12-connections-zh-dark-final.png`
- `14-connections-zh-light-final-clean.png`
- `15-connections-en-light-final.png`

## Findings and resolutions

### P1 — Fixed interface copy mixed Chinese and English

Resolved with a reversible `zh-CN` / `en` catalog, a visible language control,
locale-aware dates and numbers, translated controlled runtime states, and a
non-sensitive persisted locale preference. Static HTML coverage and runtime
feedback coverage now fail tests when English output contains Chinese or when a
placeholder translation appears. Tenant data and agent-generated business
content intentionally retain their source language.

### P1 — Connection settings were fragmented

Resolved with a dedicated Connections Hub in the primary navigation. It has
four keyboard-addressable sections: Runtime API, Marketplace APIs, AI Provider,
and Reports & Sync. Existing real tenant-scoped Amazon, Amazon Ads, Shopify,
report recipe, and sync actions were moved into this hierarchy rather than
duplicated or mocked.

### P1 — Model readiness had no repair path

Resolved with a deployment-owned AI Provider panel that shows OpenAI key/model
presence, labels the absence of live verification, documents the exact
environment variables, and links blocked Pilot readiness directly to the
relevant connection section. It does not claim a live model call occurred.

### P1 — Compact navigation lost visible labels and controls clipped

Resolved with visible icon-plus-short-label navigation at 390 and 320px,
44–50px targets, four equal-width platform controls, a two-by-two mobile
connection tab layout, full-width mobile connection actions, and an accessible
name on the icon-only Runtime control. Browser measurements report zero
horizontal overflow at both mobile widths.

### P1 — “Replace key” was not actually available while connected

Resolved by enabling a real validate-and-replace action. A failed replacement
restores the previous authenticated session and displays an error instead of
silently disconnecting the user. The key remains page-memory-only and never
enters browser storage or a URL.

### P2 — Dark controls and dense top bars lost clarity

Resolved with non-shrinking theme, locale, live, and Runtime controls; responsive
hiding of duplicate Demo/date metadata where the persistent Demo banner already
communicates the state; role-specific icon contrast; and the same semantic
surface hierarchy in Light and Dark.

## Interaction and accessibility checks

- Locale: Chinese → English → reload → Chinese; `lang`, active state, dates,
  metrics, status copy, and navigation stayed synchronized.
- Theme: Light → Dark → reload → Light; active state and dark icon contrast
  remained correct.
- Connections tabs: pointer and ArrowLeft/ArrowRight/Home/End behavior use one
  selected `tabpanel` with correct `aria-controls` and `aria-labelledby`.
- Runtime dialog: opens from both global and Connections controls, exposes a
  named password field, supports safe replacement, and closes back to the same
  page.
- Mobile: 390px and 320px show all seven navigation labels; measured document
  widths equal viewport widths and targets are at least 44px.
- Browser console: zero warnings or errors after the final interaction sweep.

## Honest limitations

- Imported Evidence, tenant names, and agent-authored business conclusions are
  not machine-translated; they remain in their source language.
- OpenAI readiness is configuration-presence only. A deployment smoke endpoint
  does not yet exist, so the UI does not expose a fake “Test OpenAI” success.
- Marketplace and model secret values remain deployment/Secret Manager owned;
  the UI stores only non-sensitive configuration and environment-variable
  references.

final result: passed
