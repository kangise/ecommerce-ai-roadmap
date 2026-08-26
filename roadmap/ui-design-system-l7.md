# Commerce Agent OS UI system — NovoChoice L7 adaptation

Date: 2026-08-26
Status: production UI contract for the embedded authenticated runtime

## Source design truth

This system adapts the UI principles and visible grammar from NovoChoice L7,
without importing NovoChoice research-domain content or its React runtime:

- `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/236-l7-user-experience-and-interface-architecture.md`
- `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/238-l7-1-ui-engineering-enforcement-contract.md`
- `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/239-l7-2-screen-atlas.md`
- `/Users/ken/Documents/Projects/Active/novochoice build/docs/v2-redesign/l7-ui-system/APPLE-PRINCIPLES.md`
- `manager-approvals-light.png`, `evidence-intake-light.png`,
  `run-execution-light.png`, and `03-refined-light-shell.png` under the L7
  screenshot archive.

The product remains Commerce Agent OS. Its canonical data continues to come
from the authenticated Runtime API and SQLite tenant state.

## Experience principles

1. One screen, one primary work object. Briefing, Evidence, Agent Runs,
   approvals, accounts, automation and audit retain distinct task compositions.
2. The Canvas owns the authoritative work. Agent findings support it and
   contextual detail remains secondary and collapsible by responsive layout.
3. Show the minimum sufficient decision set, not the fewest records. Same-layer
   comparisons stay together; evidence and audit detail appear on demand.
4. Every visible control performs its existing real action, opens a real
   dialog, navigates to a real workspace, or is disabled with a visible reason.
5. Persistence, processing and completion remain visibly distinct. Motion
   acknowledges input but never pretends a server operation has completed.
6. Reversible work stays direct; approval remains explicit for consequential
   operations. Human edits and approval decisions remain authoritative.
7. Selection is neutral gray. Green, amber and red are reserved for supported,
   attention and failure states.
8. Boundaries are surface-first and border-last. Continuous separators remain
   only where adjacent ownership would otherwise be ambiguous.
9. Collections use aligned rows and tables. Cards are reserved for concrete
   repeated objects, bounded dialogs and task summaries—not dashboard filler.
10. Responsive transformation preserves the same task meaning. Navigation and
    detail collapse before the primary Canvas is compressed or removed.
11. Accessibility changes behavior: reduced motion/transparency, stronger
    contrast, forced colors, keyboard focus and mobile touch geometry are
    first-class states.
12. Demo, blocked, empty, loading, reconnecting and failure states remain
    explicit. No visual layer may turn absent external dependencies into success.

## Canonical layout mapping

| L7 responsibility | Commerce Agent OS implementation |
| --- | --- |
| Global navigation | `.sidebar`, `.side-nav`, `.nav-item` |
| Scope toolbar | `.topbar`, `.platform-tabs`, `.topbar-meta` |
| Primary Canvas | `main`, `.view.active`, `.briefing-main`, task-specific workspaces |
| Agent context | `.agent-brief-section`, `.agent-roster-section`, Agent Run workspace |
| Contextual detail | `.decision-rail`, detail dialogs and evidence/audit dialogs |
| Complete screen header | `.page-heading`, `.kicker`, `.heading-summary`, `.heading-actions` |

Desktop uses a 226px global navigation and 52px scope toolbar. The Briefing
Canvas remains wider than its 280px contextual rail. At tablet widths the
navigation becomes compact and contextual content moves below the Canvas. At
mobile widths navigation becomes a bottom task bar and every workspace becomes
one readable column.

## Canonical component families

- Commands: `.primary-button`, `.secondary-button`, `.text-button`,
  `.icon-button`, `.quiet-button`.
- Selection: `.platform-tabs`, `.platform-tab`, `.chart-controls`,
  `.metric-toggle`, native choice controls.
- Page and section headers: `.page-heading`, `.section-title-row`,
  `.panel-heading`, `.decision-heading`.
- Async and unavailable states: `.designed-empty`, `.notice`,
  `.permission-note`, `.permission-reason`, failure and blocker families.
- Status: `.badge`, `.confidence`, `.live-indicator`, `.live-status-label`.
- Collections: `.data-list`, `.data-row`, task-specific lists and aligned
  metadata definitions.
- Bounded surfaces: `.tool-panel`, concrete record cards and native `dialog`.
- Evidence presentation: metric summary, trend Canvas, accessible table,
  provenance rows and hash-chained audit timeline.

One CSS file owns each family. Route-local colors, fonts, radii and spacing are
not allowed.

## Visual tokens

- Typography: self-hosted IBM Plex Sans for Latin/numerals and Source Han Sans
  SC for Simplified Chinese, weights 400 and 500 only.
- Type: page 28px, section 22px, object 16px, body 14px, control 12px,
  metadata 11px.
- Spacing ladder: 4 / 8 / 12 / 16 / 24 / 32 / 40 / 48px.
- Radius: 4 / 6 / 8px; fully rounded geometry is limited to status indicators.
- Light surfaces: `#f7f8f9`, `#f4f6f7`, `#ffffff`, selected `#e8ecef`.
- Light text: `#141a21`, `#34404c`, `#66717e`, `#7c8793`.
- Accent: teal `#157f89`; focus `#4e7fc9`; command surface `#141a21`.
- Semantic states: success `#257b60`, warning `#a66a20`, danger `#b84c46`.
- Motion: press 120ms, repeated UI 180ms, occasional panel 260ms. No
  `transition: all`, fake delay, bounce, parallax or decorative motion.

Dark mode preserves the same semantic hierarchy with separate surface depths;
it does not invert the light palette mechanically.

## Production invariants

- Existing element IDs, `data-action`, `data-view`, endpoint, authorization,
  Idempotency-Key and SSE contracts remain unchanged.
- API keys never enter DOM persistence or browser storage.
- Fonts and licenses ship inside the installable wheel.
- Every referenced CSS custom property must be defined.
- All visible static buttons must remain wired to a real action.
- `/app`, CSS, JavaScript, icons, brands and font assets must retain safe static
  serving headers and correct MIME types.
- Visual completion requires browser evidence at 1440px, 1024px and 390px,
  interaction checks, zero console errors and a passing `design-qa.md`.

## Deliberate non-copies

- No NovoChoice research wording, project objects, providers or fixture data.
- No React/Vite migration; the production embedded vanilla runtime stays intact.
- No standalone Unicode specimen icons; existing licensed Phosphor and brand
  assets remain the canonical icon language.
- No giant hero typography, Apple-blue universal selection, large pill controls,
  glass content surfaces, decorative card walls or permanent status rail.
