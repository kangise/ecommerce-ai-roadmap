# Provider Smoke browser QA

State: persisted Demo tenant, authenticated admin session, schema v22, Chinese
Light theme. No production provider credentials were injected.

## Verified interactions

- OpenAI: the visible action called the real Provider Smoke endpoint. Missing
  deployment credentials produced a durable `blocked / missing_credential`
  record without an outbound request. The record remained after reload.
- Shopify: the tenant connector action reused the real health adapter. Missing
  referenced credentials produced a durable blocked record and updated the
  connector health card to `misconfigured` with the same persisted timestamp.
- Amazon SP-API: the tenant connector action followed the same safe missing-
  credential path and updated the original connector health state. Amazon Ads
  remained on its separate capability-gate workflow.
- Audit: terminal smoke outcomes appeared as immutable
  `provider_smoke.execute` events in the tenant hash chain.
- Responsive: the OpenAI result card and command fit at 390px; the document
  reported zero horizontal overflow and the primary target measured 276x44px.
- Localization: controlled smoke status, stable error codes, health errors,
  provider metadata, disclosure copy, and environment-variable guidance were
  checked in Chinese. Existing bilingual catalog tests cover English output.
- Browser console: zero warnings/errors after the final sweep.

## Evidence

- `02-openai-smoke-result.png`
- `04-marketplace-layout-final.png`
- `05-marketplace-results-final.png`
- `06-openai-mobile-390.png`

## Honest external boundary

The repository and Demo environment do not contain real OpenAI, seller-
authorized Amazon SP-API, or Shopify credentials. No live external success is
claimed. Successful network paths are covered with injected transports that
verify request shape and prove that secrets, model output, and raw provider
bodies are not persisted or returned.

final result: passed
