---
title: >-
  Inventory & Distribution Constraints
summary: >-
  Inventory and distribution constraints connects material availability, warehouse capacity, site storage constraints, lead times, and delivery routing to the estimate and schedule so pricing assumptions remain feasible. This use case uses EKG to relate materials to suppliers, locations, lots/serials, reservations, and project phases, enabling early detection of “we can’t hold it / we can’t deliver it on time” risks and improved buyout, phasing, and logistics planning.
keywords:
  - inventory
  - distribution
  - warehouse
  - constraints
  - availability
  - capacity
  - lead
  - time
  - logistics
parents:
  - ..
---

Connect material availability, warehouse/site capacity, and delivery
constraints to estimating and planning so bids reflect what you can
actually source, store, and deliver.

- **Typical inputs**: BOM/material lists, phasing/schedule, supplier
  lead times, warehouse capacity, site laydown constraints, transport
  routes
- **Typical outputs**: feasibility flags (storage/lead time),
  reservation plan, delivery schedule assumptions, alternates and
  substitutions
- **EKG**: relate materials ↔ suppliers ↔ locations ↔ capacity ↔
  project phases; query “what must arrive when” vs “what can we hold
  and where”

## Related Use Cases

- **[Estimating & Pricing](../estimating-and-pricing/index.md)** —
  constrain pricing/contingency based on availability and
  storage/delivery reality
- **[Supply Chain Management](../../supply-chain-management/index.md)**
  — broader network visibility, provenance, and disruption response