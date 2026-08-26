# Mission Control design QA

- Source visual truth: `/Users/ken/.codex/generated_images/01a02716-1355-7be0-b120-f47a1aed109f/exec-31ed1705-621e-4e35-a962-f1c0c0de59a9.png`
- Final implementation screenshot: `/Users/ken/Documents/Projects/Active/ecommerce-ai-roadmap/artifacts/design-qa/implementation-populated-final-v2.jpg`
- Final same-input comparison: `/Users/ken/Documents/Projects/Active/ecommerce-ai-roadmap/artifacts/design-qa/comparison-populated-final.jpg`
- Responsive evidence: `/Users/ken/Documents/Projects/Active/ecommerce-ai-roadmap/artifacts/design-qa/implementation-mobile.jpg`
- Demo-mode evidence: `/Users/ken/Documents/Projects/Active/ecommerce-ai-roadmap/artifacts/design-qa/demo-mode-final-v2.jpg`
- Auto-session evidence: `/Users/ken/Documents/Projects/Active/ecommerce-ai-roadmap/artifacts/design-qa/demo-auto-session-final.jpg`
- Viewport: desktop `1440 x 1024` CSS px; mobile `390 x 844` CSS px
- Source pixels: `1487 x 1058`, normalized to `1440 x 1024`
- Implementation pixels: `1440 x 1024`
- Density normalization: browser CSS viewport and captured pixels are 1:1; the source was downsampled once with Lanczos to the same comparison size
- State: Amazon selected; populated browser state uses an isolated test-only SQLite fixture and the real production UI/API code. The literal non-secret key `test` is accepted only by `tests/ui_preview_server.py`; production authentication is unchanged.

## Findings

No actionable P0, P1, or P2 differences remain.

- The implementation preserves the selected design's main composition: persistent left navigation, top marketplace switcher, answer-first daily heading, four-metric evidence strip, dominant trend area, ranked Agent Brief, and a narrow approval/agent rail.
- The implementation intentionally shows one selected metric series rather than mixing unlike units on one axis. Metric tabs switch between real Evidence-derived series. This is a correctness improvement, not design drift.
- The source's invented business actions were replaced with currently supported persisted Actions. The visual hierarchy and approval affordance match, while the content remains truthful to the production runtime.
- The official Walmart Spark is yellow rather than the mock's black approximation. This follows the official supplied brand asset instead of redrawing the trademark.

## Required fidelity surfaces

- Fonts and typography: matched with the closest dependency-free system stack (`Inter`, SF, PingFang SC, Microsoft YaHei), 15px product body, 40px desktop heading, compact 11–13px metadata, and matching weights/line heights. Residual system-font variation is P3 only.
- Spacing and layout rhythm: desktop sidebar, 86px top bar, content/decision split, section dividers, metric spacing, and ranked list rhythm match the normalized source. Mobile reflows to one column with a bottom navigation bar and no horizontal page overflow.
- Colors and tokens: ivory canvas, midnight ink, cobalt primary, coral risk, green success, subtle warm rules, restrained radii, and minimal elevation match the selected direction. CSS contains no decorative gradients.
- Image quality and assets: generated CA mark is packaged at 256px; UI icons come from vendored Phosphor assets; Shopify/TikTok use Simple Icons; Walmart uses the official Spark asset. No inline/custom SVG, emoji, placeholder illustration, or CSS-drawn icon is used.
- Copy and content: selected design copy is adapted only where production truth requires it. Evidence counts, observations, metrics, priorities, actions, roles, and task states all come from authenticated tenant data.

## Full-view comparison evidence

`comparison-populated-final.jpg` places the normalized selected design and final browser capture in one image. It confirms the same region proportions, hierarchy, density, color balance, navigation model, chart placement, Agent Brief rhythm, and decision-rail emphasis.

## Focused-region comparison evidence

The final full-view comparison remains readable at 1440px per side and exposes the highest-risk dense regions: top marketplace tabs, metric strip, chart labels, ranked brief rows, approval cards, and Agent roster. Separate crops were not necessary after the populated comparison; the earlier empty-state and mobile captures remain additional state evidence.

## Comparison history

1. Pass 1 (`implementation-desktop-pass1.jpg`)
   - P2: a CSS display rule overrode the `hidden` attribute and exposed the zero approval badge.
   - P2: the connection notice occupied document flow and pushed the answer-first heading below the source position.
   - P2: heading scale/top spacing was larger than the selected design.
   - P2: Walmart used a generic storefront icon.
2. Fixes
   - Added a global `[hidden]` rule, converted notices to non-layout toasts, reduced top spacing and heading maximum size, and replaced the generic mark with the official Walmart Spark.
3. Pass 2/3 (`implementation-desktop-pass3.jpg`)
   - Empty state matched the layout and contained no P0/P1/P2 defects, but populated density still needed evidence.
4. Final populated pass (`implementation-populated-final-v2.jpg`)
   - Verified 4 real metric summaries, a 7-observation canvas trend, 3 persisted priorities, 2 persisted approval actions, and 5 persisted Agent tasks.
   - Browser console: zero warnings/errors.
   - Layout: `scrollWidth == innerWidth == 1440`.

## Primary interactions tested

- Main navigation: Briefing → Evidence → Briefing
- Platform switcher: Amazon → Shopify → Amazon
- Local connection dialog and authenticated refresh through the test-only harness
- Evidence-derived metric tabs and canvas rendering
- Agent Brief evidence-detail controls
- Approval detail controls and role-aware approval affordance
- Desktop and 390px responsive reflow
- Persistent Demo badge/banner with the transient connection toast dismissed
- Loopback-only Demo reload with no pasted key: auto-connected, 4 metrics, 3 priorities, 2 approvals, and 5 Agent rows

## Follow-up polish

- P3: production screenshots may vary slightly by installed CJK system font.
- P3: a future locale-aware amount model can add currency codes when import schemas persist them; the current UI correctly labels amount metrics as source-currency values.

final result: passed
