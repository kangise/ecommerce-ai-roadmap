# Commerce Agent OS — NovoChoice L7 adaptation design QA

- Source visual truth:
  - `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/l7-ui-system/screenshots/frontend-rebuild-phase4-baseline/decision-report-light.png`
  - `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/l7-ui-system/screenshots/frontend-rebuild-phase4-baseline/decision-report-dark.png`
  - `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/l7-ui-system/screenshots/frontend-rebuild-phase4-baseline/evidence-intake-dark.png`
  - `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/l7-ui-system/screenshots/frontend-rebuild-phase4-baseline/manager-approvals-dark.png`
  - `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/l7-ui-system/screenshots/ui-system-mobile-390-viewport.png`
- Implementation screenshots:
  - `artifacts/design-qa/l7-theme-final-light-1440.png`
  - `artifacts/design-qa/l7-theme-final-dark-1440.png`
  - `artifacts/design-qa/l7-theme-final-light-hover-1440.png`
  - `artifacts/design-qa/l7-theme-final-dark-hover-1440.png`
  - `artifacts/design-qa/l7-ui-final-briefing-dark-1440.png`
  - `artifacts/design-qa/l7-ui-final-evidence-dark-1440.png`
  - `artifacts/design-qa/l7-ui-final-approvals-dark-1440.png`
  - `artifacts/design-qa/l7-ui-final-tablet-dark-1024.png`
  - `artifacts/design-qa/l7-ui-final-mobile-dark-390.png`
  - `artifacts/design-qa/l7-ui-final-narrow-dark-320.png`
- Same-input comparisons:
  - `artifacts/design-qa/l7-theme-comparison-light-1440.png`
  - `artifacts/design-qa/l7-theme-comparison-dark-1440.png`
  - `artifacts/design-qa/l7-theme-comparison-dark-fix-1440.png`
  - `artifacts/design-qa/l7-theme-comparison-hover-1440.png`
  - `artifacts/design-qa/l7-ui-comparison-briefing-dark-1440.png`
  - `artifacts/design-qa/l7-ui-comparison-evidence-dark-1440.png`
  - `artifacts/design-qa/l7-ui-comparison-approvals-dark-1440.png`
  - `artifacts/design-qa/l7-ui-comparison-mobile-dark-390.png`
- Before evidence:
  - `artifacts/design-qa/l7-ui-before-desktop.png`
  - `artifacts/design-qa/l7-ui-before-mobile.png`
- Viewports: desktop `1440 × 900`, tablet `1024 × 900`, mobile `390 × 844`, narrow contract `320 × 800` CSS px.
- Source and implementation pixels: desktop sources and captures are exactly `1440 × 900`; mobile source and capture are exactly `390 × 844`; device scale is 1:1 with the CSS viewport.
- State: installed/source v1.3 Runtime, isolated persisted Demo tenant, explicit
  Light and Dark themes, Amazon selected, real seeded
  Evidence/Metric/Agent/Proposal/Assurance state.

## Findings

No actionable P0, P1 or P2 findings remain.

The implementation intentionally preserves Commerce Agent OS business tasks,
marketplace navigation and real API-backed content instead of copying
NovoChoice research wording or sample objects. The compared visual principles
match: cool-gray shell depth, 400/500 typography, compact geometry, neutral
selection, sparse semantic color, surface-first boundaries, one dominant work
Canvas, contextual detail, honest state language and task-preserving responsive
transformation.

## Required fidelity surfaces

### Fonts and typography

- Browser-computed body stack is `Commerce Plex`, `Commerce Han`, Source Han,
  then locale-correct system fallbacks.
- Browser font registry reports Plex 400, Plex 500 and Han 400 loaded.
- Body is 14px; desktop page title is 28px; section/object/control/metadata
  hierarchy follows 22/16/12/11px. Only weights 400 and 500 exist in CSS.
- Chinese/Latin mixed headings wrap without clipping at 1440, 1024, 390 and
  320px. No component-local typeface remains.

### Spacing and layout rhythm

- Desktop geometry measures 226px navigation, 52px scope toolbar, 870px
  Briefing Canvas and 280px contextual rail at 1440px.
- Tablet preserves an 896px Canvas and moves the 896px contextual surface below
  it rather than compressing the decision object.
- Mobile converts to one task column with a 66px bottom navigation. At 320px all
  seven targets measure 44 × 50px and document overflow remains zero.
- Governed spacing uses 4/8/12/16/24/32/40/48px. Ordinary component radii are
  4/6/8px; fully rounded geometry is restricted to status indicators.

### Colors and visual tokens

- Light is a complete, browser-rendered product theme rather than a static token
  promise. Light and Dark share one hierarchy and an explicit segmented control;
  the selected value, `aria-pressed` state and browser theme color survive reload.
- Dark browser state visibly preserves four depth levels instead of inverting
  light colors mechanically. Source and implementation comparisons show the
  same quiet neutral hierarchy.
- Selected navigation/platform/metric states are neutral. Teal is limited to
  evidence/chart/focus context; green, amber and red communicate semantic
  outcome only.
- Dark Demo warning contrast was corrected from a light-only fixed value to the
  governed warning token. Canvas chart grid, labels, points and line read the
  active CSS tokens instead of stale hardcoded colors.
- Dark foregrounds are role-specific: command icons are black on the light
  Primary surface; Amazon/TikTok, navigation, utility, Agent and upload glyphs
  are light on dark surfaces; Shopify/Walmart preserve their brand colors.

### Image and asset fidelity

- Existing licensed Phosphor icons and official marketplace brand assets remain
  intact; no emoji, CSS drawing, inline SVG or placeholder icon was introduced.
- IBM Plex and Source Han WOFF2 assets are self-hosted and their upstream
  licenses ship beside existing icon licenses.
- No raster illustration was required by the task screens, so no generated
  placeholder imagery was added.

### Copy and content

- All marketplace metrics, observations, priorities, approvals, run state and
  Assurance content continue to come from authenticated tenant data.
- Proposal hashes and internal graph/resource IDs moved to the existing detail
  dialog instead of competing with the decision at D0/D1.
- Demo and Amazon Ads blocked boundaries remain explicit. No fake success,
  business metric, progress percentage or external credential claim was added.

## Full-view comparison evidence

- Briefing vs Decision Report: both lead with one answer/title, one dominant
  command, restrained task tabs/controls, quiet soft work surface and supporting
  detail that cannot overtake the primary Canvas.
- Evidence vs Evidence Intake: the app preserves its required upload workbench
  while using the same collection rhythm, 28px title, neutral controls, aligned
  rows, semantic status and continuous separators.
- Approvals vs Manager Approvals: both make the bounded decision context and one
  primary action obvious. The app retains its real Proposal creation form and
  history because those are existing product tasks.
- Mobile vs L7 mobile constitution: both become one readable task surface with
  an obvious next action and detail below the fold; desktop columns are not
  squeezed into miniature cards.

## Focused-region comparison evidence

- Approval form primary action measured `160 × 42px` after correction; it no
  longer stretches to the textarea row height.
- Mobile Evidence heading and freshness state occupy separate rows; title text
  is no longer compressed into a narrow column.
- Desktop font, shell, Canvas and detail geometry were read from computed style,
  not inferred from source CSS.
- Focused interaction checks covered the metric segmented control, Evidence
  detail dialog open/close, platform selection and accessible mobile navigation.
- Dark computed-style evidence confirms the Primary icon uses
  `brightness(0)` on `rgb(243,245,246)` while Amazon/TikTok use
  `brightness(0) invert(1)`. The hovered TikTok surface is
  `rgb(42,48,53)` with light text/icon; Light hover uses `rgb(241,243,245)`
  with its original dark brand glyph.

## Comparison history

### Pass 1 findings

- P1: mobile navigation labels disappeared from the accessibility tree when
  visible text collapsed at compact widths.
- P2: the Proposal primary command stretched to the height of its neighboring
  textarea, creating an oversized white block.
- P2: full hashes and internal Daily/Agent/Graph IDs were exposed in the main
  Proposal collection instead of detail-on-demand.
- P2: mobile Evidence title and freshness pill competed in one row.
- P2: the 1024px layout retained a persistent detail rail and unnecessarily
  narrowed the Canvas.
- P2: several warning/error rules retained light-only fixed text/border colors.
- P2: seven 50px mobile navigation items would overflow the 320px contract.

### Fixes and post-fix evidence

- Added persistent `aria-label` values to all seven navigation controls; browser
  role lookup now resolves every compact control.
- Bounded the Proposal command at `160 × 42px` desktop and 44px full-width on
  mobile; moved technical lineage to the real detail dialog.
- Stacked mobile Evidence heading/freshness and moved tablet contextual detail
  beneath the full Canvas.
- Replaced fixed semantic values with theme tokens and normalized the bottom
  navigation to seven 44px-wide targets at 320px.
- Recaptured desktop, tablet and mobile evidence. All viewports report zero
  horizontal overflow and zero page console warnings/errors.

### Theme refinement findings from user review

- P1: Light existed only as CSS tokens and was not a visible selectable theme.
- P1: the Dark Primary command used a light command surface while its icon was
  also forced white, making the refresh glyph disappear.
- P1: Amazon/TikTok remained black on dark platform hover/active surfaces.
- P2: Agent, upload and account identity glyphs reused light-theme filters or
  foreground values that reduced dark-surface contrast.

### Theme refinement fixes and post-fix evidence

- Added a real Light/Dark segmented control, defaulted new sessions to Light,
  persisted the non-sensitive preference locally and synchronized native
  `color-scheme`, browser theme color and chart repaint.
- Replaced one universal Dark image filter with role-specific treatments for
  Primary commands, marketplace brands, navigation, Agent/upload utilities and
  identity anchors.
- Captured Light, Dark, Light-hover and Dark-hover at the same 1440 × 900
  viewport and placed each source/implementation or before/after pair in one
  comparison artifact. Theme reload persistence and zero console warnings/errors
  were verified in both themes.
- At 320px the two theme commands measure 44 × 44px and the page remains at zero
  horizontal overflow.

## Primary interactions tested

- Seven global workspaces: Briefing, Agents, Evidence, Approvals, Accounts,
  Automations and Audit.
- Platform selection: Amazon → Shopify → Amazon; `aria-pressed` and heading scope
  update together.
- Six real metric choices; selecting Conversion updates the active control and
  retains a visible Canvas chart.
- Evidence detail opens from a real record, renders its native dialog and closes
  back to the collection.
- Mobile navigation remains role-addressable when its text is visually hidden.
- Light → Dark → reload → Light was exercised through the visible theme controls;
  DOM theme, `aria-pressed`, browser theme color and Canvas colors stayed aligned.
- TikTok hover was measured in both themes, including its background, foreground,
  icon filter and opacity.
- Browser console warnings/errors: zero after final interaction sweep.

## Residual P3 / test boundaries

- The 14MB Source Han variable font is intentionally complete for dynamic
  Chinese tenant content. A future measured subset strategy could reduce wheel
  size only if it preserves unseen runtime glyph coverage.

final result: passed
