# Politically Exposed Persons (PEPs)

<object data="../../../../diagrams/out/peps.svg#darkable" type="image/svg+xml"></object>

## Summary

Politically Exposed Persons (PEPs) are individuals who hold or have held prominent public positions, making them potentially higher risk for corruption, bribery, or money laundering. PEP screening is a mandatory component of KYC and AML compliance, requiring financial institutions to identify PEPs, assess their risk, and apply enhanced due diligence measures.

## The Challenge

Financial institutions face complex challenges in PEP screening:

- **Definition complexity** — PEP definitions vary by jurisdiction and regulatory framework (FATF, FinCEN, EU directives)
- **Dynamic status** — Political positions change through elections, appointments, and resignations
- **Indirect connections** — Family members and close associates of PEPs pose similar risks
- **False positive management** — Name matching alone creates excessive false positives requiring manual review
- **Data quality** — PEP databases have varying quality, coverage, and update frequency
- **Cross-border complexity** — Understanding foreign political structures and positions
- **Risk assessment** — Determining appropriate risk levels and due diligence measures for different types of PEPs
- **Continuous monitoring** — PEP status changes require ongoing monitoring and re-assessment

Traditional screening approaches rely on periodic batch checks that miss real-time changes and indirect connections.

## Why EKG is Required

Enterprise Knowledge Graphs provide sophisticated PEP screening capabilities:

- **Relationship traversal** — Automatically identify connections through family, business, or social relationships
- **Multi-hop analysis** — Find indirect PEP connections that may not be caught by direct screening
- **Temporal tracking** — Maintain historical PEP positions and understand risk decay over time
- **Contextual risk scoring** — Weight PEP connections based on relationship strength, recency, and jurisdiction
- **Continuous monitoring** — Real-time updates as political positions change or new connections are discovered
- **Enhanced entity resolution** — Disambiguate individuals with similar names using relationship context
- **Integration with other risk factors** — Combine PEP status with transaction patterns and other red flags
- **Compliance documentation** — Maintain complete audit trail of PEP screening and risk decisions

## Business Value

- **Regulatory compliance** — Meet AML/KYC requirements for PEP screening and enhanced due diligence
- **Risk mitigation** — Avoid corruption, bribery, and money laundering risks associated with PEPs
- **Reputational protection** — Prevent association with sanctioned or compromised political figures
- **Efficiency gains** — Reduce false positives and manual review effort through contextual analysis
- **Proactive monitoring** — Identify emerging PEP risks before they become compliance violations
- **Audit trail** — Maintain complete record of PEP screening and decisions for regulatory review

## Related Topics

See also [Political Connections](../relationships-and-connections/political-connections.md) for analysis of political relationship networks.
