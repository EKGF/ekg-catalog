---
title: >-
  Know Your Customer
summary: >-
  Know Your Customer (KYC) encompasses the processes for verifying customer identity, assessing risk, and ensuring regulatory compliance throughout the customer lifecycle. This use case addresses managing complex multi-jurisdictional requirements, verifying identities across channels, conducting risk assessments based on geography and relationships, continuously monitoring customer activities for suspicious behavior, reducing false positive alerts, and maintaining accurate customer information across systems for compliance reporting.
keywords:
  - know
  - customer
  - kyc
  - encompasses
  - processes
  - verifying
  - identity
  - assessing
  - risk
  - ensuring
  - regulatory
  - compliance
parents:
  - ..
---

## The Challenge

Organizations face significant challenges in KYC management:

- **Regulatory complexity** — Multiple jurisdictions with different
  KYC requirements and compliance obligations
- **Identity verification** — Verifying customer identity across
  different channels and jurisdictions
- **Risk assessment** — Assessing customer risk based on multiple
  factors including geography, relationships, and behavior
- **Data fragmentation** — Customer information scattered across
  multiple systems, channels, and jurisdictions
- **Real-time monitoring** — Continuous monitoring of customer
  transactions and activities for suspicious behavior
- **False positives** — High rates of false positive alerts requiring
  manual review
- **Compliance reporting** — Generating compliance reports for
  regulators and internal stakeholders
- **Data quality** — Maintaining accurate and up-to-date customer
  information across systems

Traditional KYC systems operate in silos and lack the integrated view
needed for comprehensive customer risk assessment and compliance.

## Why EKG is Required

Enterprise Knowledge Graphs provide powerful KYC capabilities:

- **Unified customer view** — Connect all customer information across
  systems, channels, and time periods
- **Identity resolution** — Link customer identities across different
  systems and channels
- **Relationship analysis** — Understand customer relationships and
  connections for risk assessment
- **Network analysis** — Identify suspicious networks and patterns
  through graph analysis
- **Real-time monitoring** — Continuously monitor customer activities
  and transactions
- **Regulatory integration** — Link customer data to regulatory
  requirements and compliance obligations
- **Risk aggregation** — Assess customer risk based on multiple
  factors and relationships
- **Pattern detection** — Identify suspicious patterns and behaviors
  through graph algorithms

## Business Value

- **Regulatory compliance** — Meet KYC requirements and avoid
  penalties and sanctions
- **Risk mitigation** — Identify and address customer risks before
  they become problems
- **Fraud prevention** — Detect and prevent fraud through network
  analysis and pattern detection
- **Operational efficiency** — Automate KYC processes and reduce
  manual review
- **Cost reduction** — Reduce false positives and improve alert
  accuracy
- **Customer experience** — Streamline onboarding and reduce friction
  for legitimate customers

## Components

- [Core Record Management](core-record-management/index.md)
  - [Addresses](core-record-management/addresses.md)
  - [Legal Entities](core-record-management/legal-entities.md)
  - [Locations](core-record-management/locations.md)
  - [Buildings](core-record-management/buildings.md)
  - [Countries](core-record-management/countries.md)
  - [Jurisdictions](core-record-management/jurisdictions.md)
  - [Regions](core-record-management/regions.md)
  - [Audit](core-record-management/audit.md)
- [Identification & Verification](identification-verification.md)
- [Anti-Money Laundering (AML)](anti-money-laundering/index.md)
  - [Transaction-Based AML](anti-money-laundering/transaction-based-aml.md)
  - [Network-Based AML](anti-money-laundering/network-based-aml.md)
  - [Correspondent-Based AML](anti-money-laundering/correspondent-based-aml.md)
- [Sanctions](sanctions.md)
- [Politically Exposed Persons (PEPs)](peps.md)
- [GDPR](gdpr.md)
- [Crime Records](crime-records.md)
- [Risk Management](risk-management.md)
- [Activity Monitoring](activity-monitoring.md)
- [High Net Worth Individuals](high-net-worth-individuals.md)

## Related Use Cases

Know Your Customer depends on and integrates with several other use
cases:

- **[Legal Entity Management](../../legal-entity-management/index.md)** -
  KYC uses Legal Entity Management for comprehensive information about
  corporate customers, their legal structures, ownership, and
  relationships. See
  [Legal Entities](core-record-management/legal-entities.md) for
  details.

- **[Vendor Management](../../supply-chain-management/vendor-management/index.md)** -
  Vendor vetting processes are similar to customer KYC, especially for
  regulated industries like banks. Vendor KYC requires similar
  identity verification, risk assessment, and compliance checks as
  customer KYC, and can leverage KYC processes and data.

### Shared Concepts

Know Your Customer uses these shared reference data concepts:

- **[Countries](../../../concept/countries.md)** - Geographic
  reference data for customer risk assessment
- **[Jurisdictions](../../../concept/jurisdictions.md)** - Legal and
  regulatory jurisdictions for compliance
- **[Regions](../../../concept/regions.md)** - Geographic regions for
  risk classification

These shared concepts are also used by Legal Entity Management and
other use cases.