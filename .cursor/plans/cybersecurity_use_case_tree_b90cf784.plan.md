---
name: Cybersecurity use case tree
overview: Create an initial cybersecurity use case tree under `docs/use-case/cyber-security/`, using CSF-style top-level functions and capability-oriented decomposition where it adds business value, and use `is-used-in` links to environment/context nodes (Cloud/SaaS/OT) to avoid duplication. Every page must have a strong, EKG-free summary and business-analyst-oriented body text with an \"Outcomes\" section.
todos:
  - id: add-csf-branches
    content: Create CSF-style branch directories under `docs/use-case/cyber-security/` (govern/identify/protect/detect/respond/recover) with `index.md` files and correct `is-part-of`.
    status: pending
  - id: add-capability-pages
    content: Add capability pages under each branch with concise summaries and correct `is-part-of` (depth varies by business usefulness).
    status: pending
    dependencies:
      - add-csf-branches
  - id: add-digital-twin-shared-components
    content: Create shared Digital Twin component use cases (e.g., technology inventory, dependency mapping, data-flow mapping) that Cybersecurity can reference via `is-used-in` to avoid duplication and to prepare for the upcoming Digital Twin tree.
    status: pending
    dependencies:
      - add-csf-branches
  - id: update-digital-twin-index
    content: Update `docs/use-case/digital-twin/index.md` to match the business-facing content rules (no EKG-centric sections; include an \"Outcomes\" section; keep summary EKG-free).
    status: pending
    dependencies: []
  - id: author-business-copy
    content: Ensure each new use case page has (a) a summary that does not mention EKG, and (b) body text written for business analysts including an \"Outcomes\" section listing expected outcomes enabled by the use case.
    status: pending
    dependencies:
      - add-csf-branches
  - id: weave-genai-agents
    content: Weave GenAI + autonomous specialist agents into relevant cybersecurity pages (business-facing), describing what tasks agents can perform in-context and how they are guardrailed (policy, approvals, provenance, and EKG-backed context), without turning pages into implementation docs.
    status: pending
    dependencies:
      - add-csf-branches
  - id: add-context-nodes
    content: Add `cyber-security/contexts/*` nodes (cloud/saas/ot-ics) owned by cybersecurity.
    status: pending
    dependencies:
      - add-csf-branches
  - id: wire-is-used-in
    content: Add `is-used-in` links from relevant capability pages to context nodes to prevent content duplication.
    status: pending
    dependencies:
      - add-capability-pages
      - add-context-nodes
  - id: crosslink-other-usecases
    content: Cross-link cybersecurity pages into other use case trees (e.g., Digital Twin) using `is-used-in` for dotted edges and a \"Related Use Cases\" section for human navigation.
    status: pending
    dependencies:
      - add-capability-pages
  - id: validate-build
    content: Run the docs build/serve to confirm navigation + graph generation succeed with the new nodes.
    status: pending
    dependencies:
      - wire-is-used-in
      - crosslink-other-usecases
---

# Cybersecurity use case tree (hybrid + is-used-in)

## Goal

Produce an initial, navigable use case tree for the top-level use case `cyber-security`, using **hybrid NIST-CSF-style top-level branches** and **capability-oriented sub-branches** where it makes business-analysis sense, while leveraging **`is-used-in`** to model cross-cutting “contexts” (Cloud/SaaS/OT) without duplicating content.

## Approach

- Keep `cyber-security/index.md` as the top-level node (already exists).
- Add subdirectories under `[...]/docs/use-case/cyber-security/` for:
- **CSF-style functions**: `govern/`, `identify/`, `protect/`, `detect/`, `respond/`, `recover/`
- **Context nodes**: `contexts/` (e.g. cloud/saas/ot-ics) that are **owned by** cybersecurity, but **referenced via `is-used-in`** from relevant capability pages.
- Prepare for the upcoming Digital Twin tree by creating a small set of **Digital Twin-owned shared component pages** and linking them into Cybersecurity via `is-used-in` (dotted edges) and via \"Related Use Cases\" sections.
- For each new page, set:
- **`is-part-of`** to its ownership parent (directory structure mirrors ownership)
- **`is-used-in`** to one or more context nodes when the capability applies there
 - Keep depth flexible: some branches may only need an `index.md`; others may go deeper when there is clear business value in further decomposition.
- Content guidelines (apply to every new cybersecurity page):
  - Frontmatter `summary` must be written for a business audience and **must not mention EKG** (or any implementation technology).
  - Body text must speak to **business analysts / the business** (value, decisioning, governance, service outcomes), not to engineers.
  - Body text must include an **\"Outcomes\"** section describing expected outcomes enabled by the use case (e.g., reduced incident impact, improved audit readiness, faster detection, clearer accountability).
  - Include a short **\"Related Use Cases\"** section where it adds clarity, linking to other top-level use cases (e.g., Digital Twin, Risk Management, Data Privacy & Governance, Regulatory Reports) using normal markdown links.
  - Where relevant, include a short **\"GenAI-enabled execution\"** subsection (either under \"Outcomes\" or immediately after it) that explains, in business terms:
    - What **autonomous specialist agents** can do in this use case (e.g., triage, evidence gathering, control testing support, narrative report drafting, ticket routing, stakeholder comms drafts).
    - How those agents are **guardrailed** (e.g., operate only with approved scope, rely on authoritative context, require human approvals for high-impact actions, produce traceable evidence/provenance).
    - How the **use case context** (assets, policies, controls, incidents, dependencies) constrains and improves agent decisions. (OK to mention EKG in the body when describing guardrails/context; keep summaries EKG-free.)

## Files to change/add

- Update (if desired):
- [/Users/jgeluk/Work/ekg-catalog/docs/use-case/cyber-security/index.md](/Users/jgeluk/Work/ekg-catalog/docs/use-case/cyber-security/index.md) (optional: add brief “Components” section that links to the new branches)
- Update (required to match content rules):
  - `docs/use-case/digital-twin/index.md` (rewrite body for business analysts; remove \"Why EKG is Required\"; add \"Outcomes\" and \"GenAI-enabled execution\" where relevant)
- Add new shared Digital Twin pages (owned by `digital-twin/`, referenced from cybersecurity via `is-used-in`):
  - `docs/use-case/digital-twin/technology-estate-inventory.md`
  - `docs/use-case/digital-twin/dependency-and-relationship-mapping.md`
  - `docs/use-case/digital-twin/data-flow-and-lineage-mapping.md`
  - `docs/use-case/digital-twin/security-and-compliance-posture-visibility.md`
- Add new pages (ownership tree):
- `docs/use-case/cyber-security/govern/index.md`
    - `security-strategy-and-policy.md`
    - `risk-management.md`
    - `compliance-and-audit.md`
    - `third-party-and-supply-chain-risk.md`
    - `security-architecture-and-standards.md`
- `docs/use-case/cyber-security/identify/index.md`
    - (Prefer to reference Digital Twin inventory/mapping pages via `is-used-in` instead of duplicating them here)
    - `attack-surface-management.md`
    - `vulnerability-management.md`
    - `data-classification-and-criticality.md`
    - `threat-modeling-and-scenarios.md`
- `docs/use-case/cyber-security/protect/index.md`
    - `identity-and-access-management.md`
    - `privileged-access-management.md`
    - `secure-configuration-and-hardening.md`
    - `application-and-api-security.md`
    - `data-protection.md`
    - `network-and-segmentation.md`
    - `security-awareness-and-training.md`
    - `backup-and-resilience-controls.md`
- `docs/use-case/cyber-security/detect/index.md`
    - `logging-and-telemetry.md`
    - `soc-monitoring-and-alerting.md`
    - `detection-engineering.md`
    - `threat-intelligence.md`
    - `threat-hunting.md`
    - `anomaly-and-behavior-detection.md`
- `docs/use-case/cyber-security/respond/index.md`
    - `incident-intake-and-triage.md`
    - `investigation-and-forensics.md`
    - `containment-and-eradication.md`
    - `communications-and-disclosure.md`
    - `lessons-learned-and-improvement.md`
- `docs/use-case/cyber-security/recover/index.md`
    - `service-restoration.md`
    - `backup-restore-and-integrity.md`
    - `disaster-recovery-and-bcp.md`
    - `resilience-improvements.md`

## Context nodes (to avoid duplication via is-used-in)

Add:

- `docs/use-case/cyber-security/contexts/index.md`
- `cloud/index.md`
- `saas/index.md`
- `ot-ics/index.md`

Then, on selected capability pages, add `is-used-in` references to one or more of:

- `/cyber-security/contexts/cloud`
- `/cyber-security/contexts/saas`
- `/cyber-security/contexts/ot-ics`

Examples:

- `protect/application-and-api-security` is-used-in: cloud, saas
- `protect/network-and-segmentation` is-used-in: cloud, ot-ics
- `detect/logging-and-telemetry` is-used-in: cloud, saas, ot-ics

## Cross-linking to other use case trees (no duplication)

Use two complementary mechanisms:

1) `is-used-in` (graph-level, for dotted edges in diagrams):\n
   - Add `is-used-in` links from cybersecurity nodes to relevant **other** use cases to show where a cybersecurity capability is applied/consumed.\n
   - Example targets (top-level nodes): `/digital-twin`, `/risk-management`, `/data-privacy-governance`, `/regulatory-reports`.\n
   - Prefer to model shared capabilities as **owned by the most natural home use case** (e.g., Digital Twin owns inventory/mapping) and then link them into Cybersecurity via `is-used-in` (so Cybersecurity diagrams show dotted child links without duplicating content).

2) \"Related Use Cases\" section (reader navigation):\n
   - In the page body, add links like `../digital-twin/index.md` (relative) or `/use-case/digital-twin/` (absolute, if you prefer) so business readers can jump across trees directly.

## Validation

- Run the existing docs build/serve flow (whatever you normally use) and confirm:
- the new pages appear in navigation (auto `.pages.yaml` generation)
- the use case tree diagram generation picks up the new nodes