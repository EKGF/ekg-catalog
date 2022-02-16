var __index = Promise.resolve({"config":{"indexing":"full","lang":["en"],"min_search_length":3,"prebuild_index":false,"separator":"[\\s\\-]+","tags":false},"docs":[{"location":"","text":"<p>Use Case Portal</p>","title":"Introduction"},{"location":"glos/","text":"<ul> <li>EKG</li> <li>EKG/Platform</li> <li>Primary Repository</li> <li>Use Case</li> <li>SPARQL</li> <li>Story</li> <li>Triplestore</li> </ul>","title":"Index"},{"location":"glos/api-gateway/","text":"","title":"API Gateway"},{"location":"glos/api/","text":"<p>The RedHat definition:</p>  <p>API stands for application programming interface, which is a set of definitions and protocols for building and integrating application software.</p>","title":"API"},{"location":"glos/ekg-id/","text":"<p>An EKG/ID is an Enterprise Knowledge Graph Identifier that has the form of a number.</p> <p>At higher levels of maturity for your overall EKG Platform Architecture you may wish to switch over from using EKG/IRIs for all your EKG identifiers to EKG/IDs in order to decouple the primary identifiers for any given \"thing\" in your Enterprise Knowledge Graph from their DNS host or domain name as that is encoded in each HTTP URL today.</p> <p>In other words, in the various backend data-stores of your EKG you then no longer use HTTP URLs as the identifier for any given thing but numbers (either large random numbers or large hash numbers, signed or not signed).</p>","title":"EKG/ID"},{"location":"glos/ekg-iri/","text":"<p>An EKG/IRI is an Enterprise Knowledge Graph Identifier that has the form of a URL/URI1</p>   <ol> <li> <p>We prefer to use the term IRI because a) that's the most recent name of the URI standard and b) IRIs support international encodings so that terms in non-latin languages like Chinese and Arab can also be supported.\u00a0\u21a9</p> </li> </ol>","title":"EKG/IRI"},{"location":"glos/ekg-platform/","text":"<p>An Enterprise Knowledge Graph Platform is a logical system architecture component, the layer of software services that provide and  serve the EKG to end-users and other systems. The platform logically is a set services that enforce any of the specified policies in the self-describing datasets (SDDs) that have been  published in the EKG.</p>","title":"EKG/Platform"},{"location":"glos/ekg/","text":"<p>much like \"the web\" is a virtual concept, an Enterprise Knowledge Graph (EKG) is a virtual concept  that stands for the combination of all information and knowledge of a given enterprise -- at any level in the organization -- or ecosystem.</p>","title":"EKG"},{"location":"glos/primary-repo/","text":"<p>The primary EKG repository is the git repository that holds all metadata that described an organization's Enterprise Knowledge Graph in terms of:</p> <ul> <li> <p>All Use Cases and their:</p> <ul> <li>Stories</li> <li>Concepts, Vocabularies &amp; Ontologies</li> <li>Personas</li> <li>Business Purposes &amp; Outcomes</li> <li>Test Scenarios</li> <li>(Descriptions of) Datasets</li> </ul> </li> <li> <p>Infrastructure of the EKG/Platform:</p> <ul> <li>Helm Charts</li> <li>Terraform   Terraform files that provision a Kubernetes cluster</li> <li>Software Components   Metadata for all the various software components e.g. services,   docker images, docker volumes etc.</li> </ul> </li> </ul>","title":"Primary EKG Repository"},{"location":"glos/sparql/","text":"<p>SPARQL (pronounced \"sparkle\" /\u02c8sp\u0251\u02d0k\u0259l/, a recursive acronym for SPARQL Protocol and RDF Query Language) is an RDF query language\u2014that is, a semantic query language for databases\u2014able to retrieve and manipulate data stored in Resource Description Framework (RDF) format.</p> <pre><code>PREFIX lcc-cr: &lt;https://www.omg.org/spec/LCC/Countries/CountryRepresentation/&gt;\n\nSELECT DISTINCT\n    ?graph\n    ?region\n    ?regionLabel\nWHERE {\n    GRAPH ?graph {\n        ?region a lcc-cr:Country .\n        ?region ?p ?regionObject .\n        ?region rdfs:label ?regionLabel .\n\n        BIND(COALESCE(?searchText, \"\") AS ?searchTextBound)\n\n        FILTER (\n            CONTAINS(LCASE(?regionObject), LCASE(?searchTextBound))\n        )\n    }\n}\nORDER BY ?regionLabel\n</code></pre>","title":"SPARQL"},{"location":"glos/story/","text":"","title":"Story"},{"location":"glos/triple/","text":"","title":"Triple"},{"location":"glos/triplestore/","text":"<p>The term \"triplestore\" is the colloquial term for a database whose internal data structure is based on \"RDF Statements\" a.k.a. \"triples\", see triple for more information.</p>","title":"Triplestore"},{"location":"glos/use-case/","text":"","title":"Use Case"},{"location":"use-case/","text":"<ul> <li>Digital Twin / Connected Inventory</li> <li>Client 360</li> <li>Real-time Fraud Detection</li> <li>Real-time Enterprise Risk Management</li> <li>Cybersecurity</li> <li>Organization Management</li> </ul>","title":"Use Cases"},{"location":"use-case/strategic-use-cases/","text":"<ul> <li>Digital Twin / Connected Inventory</li> <li>Client 360</li> <li>Real-time Fraud Detection</li> <li>Real-time Enterprise Risk Management</li> <li>Cybersecurity</li> <li>Organization Management</li> </ul>","title":"Strategic use cases"},{"location":"use-case/client-360/","text":"","title":"Client 360"},{"location":"use-case/client-360/#summary","text":"<p>The arch-use case is \"Client 360\".</p> <p>Every large enterprise struggles with this, often for decades trying to  create one holistic view of their business with their customers,  across lines of business, globally.</p> <p>This is one of the core use cases where the EKG can shine and can really  add value and is the technology that can actually deliver a solution  for this use case.</p> <ul> <li>Relationships &amp; Connections</li> <li>Know Your Customer (KYC)</li> <li>Social Media</li> </ul>","title":"Summary"},{"location":"use-case/client-360/know-your-customer/","text":"<ul> <li>Core Record Management</li> <li>Money Laundering</li> <li>Identification Verification</li> <li>Politically Exposed Persons (PEPs)</li> <li>Crime Records</li> <li>Sanctions</li> <li>Risk Management</li> <li>Activity Monitoring</li> <li>High Net Worth Individuals (HNWI)</li> <li>GDPR</li> </ul>","title":"Know Your Customer"},{"location":"use-case/client-360/know-your-customer/#high-net-worth-individuals","text":"<p>This is especially the case in regard to High Net Worth (HNW) individuals. A large number of organizations monitor the transactions of HNW individuals in a separate complementary process along with a more formal annual KYC review. These traditional monitoring systems really struggle to handle the lifestyles of the new rich and produce meaningful warning or reports that can be used to assess customer behavior. With top end handbags often costing in excess of \u00a320,000 the alerts holistically triggered run the risk of simply creating noise rather than information.</p> <p>A traditional transaction monitoring platform does not provide any context to customer behavior. Has the customer\u2019s behaviour profile changed since the last review? Simply looking at income and outgoings for a customer is not enough it maybe exactly as the customer has said (say $4MM income $3.8MM expenditure) \u2014 so is an alert for a $20,000 handbag what KYC should really be looking for?</p> <p>What the organization really needs to do is to look at the sources of the income; the countries, investments, companies of familial links. The nature of the expenditure. The nature of the expenditure also need to be what has been brought, where and how? The nature of these transactions need to be reviewed holistically, perhaps a customer bought a company in a previous year and then continues funnelling money to this investment. It is only through using a holistic view that you can get analysis data to give you the context to knowing something different has happened in regard to entities and individuals concerned.</p> <p>A holistic view enables you to connect these counter parties to see if these financial interactions make sense. The ability to monitor activity in context of a holistic view enables the organization to have valuable insights on what these individuals are doing. This information can in turn be used to more effectively assess an individual for \\glsxtrshort{aml} issues and risk. This is an important lower level analysis task that knowledge graph excels at because as most large scale money laundering tends to involve networks of individuals and organizations with a controlling force. The EKG enables the easier identification of all networks (bank accounts, transactions and customers) which in turn allows for swift analysis of alerts. A cluster of automatic alerts all in a given network identified by the \\glsxtrshort{ekg} can be swifty escalated for review (this is detailed further in the use case \\usecaseref{uc:aml}).</p>","title":"High Net Worth Individuals"},{"location":"use-case/client-360/know-your-customer/#gdpr","text":"<p>By creating a holistic view of the data within the organization and leveraging both internally and externally available data (such as directors, shareholders, sanctions and adverse lists) the EKG can create a holistic view and analyse current and potential clients. This enables the identification of direct and indirect (i.e. beneficial ownership structures) risk factors.</p> <ul> <li>Tracking and tracing all activities and all facts around the end to end   life cycle of a customer, starting as a lead or prospect and bringing   that all together in one logical (but not physical) place would provide   tremendous value in many different ways.</li> <li>It would make any organization compliant with GDPR for instance.   (Btw GDPR compliance might be worth a chapter in itself or should be   in the title of this use case).</li> <li>Tying not only CRM systems to the EKG but also all their transactions,   again logically, not physically, all emails, documents, phone calls,   time registration, contracts, invoices, budgets, costs, projects,   SLAs, issues, tickets, market data, competitive analysis,   interest graphs, pattern detection, ML and AI and so forth.</li> <li>Last but not least: it allows for \u201cdiscovery\u201d of anything around a   customer, enabling your colleagues to learn about the customer and   gain understanding or even knowledge, overseeing it all,   seeing the customer and all their subsidiaries and global operations   for instance as one whole with infinite drill down capability.   And that knowledge can not only be provided to humans but also to   AIs by the way.</li> </ul>","title":"GDPR"},{"location":"use-case/client-360/know-your-customer/activity-monitoring/","text":"","title":"Activity Monitoring"},{"location":"use-case/client-360/know-your-customer/crime-records/","text":"","title":"Crime Records"},{"location":"use-case/client-360/know-your-customer/gdpr/","text":"","title":"GDPR"},{"location":"use-case/client-360/know-your-customer/gdpr/#gdpr","text":"<p>By creating a holistic view of the data within the organization and leveraging both internally and externally available data (such as directors, shareholders, sanctions and adverse lists) the EKG can create a holistic view and analyse current and potential clients. This enables the identification of direct and indirect (i.e. beneficial ownership structures) risk factors.</p> <ul> <li>Tracking and tracing all activities and all facts around the end to end   life cycle of a customer, starting as a lead or prospect and bringing   that all together in one logical (but not physical) place would provide   tremendous value in many different ways.</li> <li>It would make any organization compliant with GDPR for instance.   (Btw GDPR compliance might be worth a chapter in itself or should be   in the title of this use case).</li> <li>Tying not only CRM systems to the EKG but also all their transactions,   again logically, not physically, all emails, documents, phone calls,   time registration, contracts, invoices, budgets, costs, projects,   SLAs, issues, tickets, market data, competitive analysis,   interest graphs, pattern detection, ML and AI and so forth.</li> <li>Last but not least: it allows for \u201cdiscovery\u201d of anything around a   customer, enabling your colleagues to learn about the customer and   gain understanding or even knowledge, overseeing it all,   seeing the customer and all their subsidiaries and global operations   for instance as one whole with infinite drill down capability.   And that knowledge can not only be provided to humans but also to   AIs by the way.</li> </ul>","title":"GDPR"},{"location":"use-case/client-360/know-your-customer/high-net-worth-individuals/","text":"","title":"HNW Individuals"},{"location":"use-case/client-360/know-your-customer/high-net-worth-individuals/#high-net-worth-individuals","text":"<p>This is especially the case in regard to High Net Worth (HNW) individuals. A large number of organizations monitor the transactions of HNW individuals in a separate complementary process along with a more formal annual KYC review. These traditional monitoring systems really struggle to handle the lifestyles of the new rich and produce meaningful warning or reports that can be used to assess customer behavior. With top end handbags often costing in excess of \u00a320,000 the alerts holistically triggered run the risk of simply creating noise rather than information.</p> <p>A traditional transaction monitoring platform does not provide any context to customer behavior. Has the customer\u2019s behaviour profile changed since the last review? Simply looking at income and outgoings for a customer is not enough it maybe exactly as the customer has said (say $4MM income $3.8MM expenditure) \u2014 so is an alert for a $20,000 handbag what KYC should really be looking for?</p> <p>What the organization really needs to do is to look at the sources of the income; the countries, investments, companies of familial links. The nature of the expenditure. The nature of the expenditure also need to be what has been brought, where and how? The nature of these transactions need to be reviewed holistically, perhaps a customer bought a company in a previous year and then continues funnelling money to this investment. It is only through using a holistic view that you can get analysis data to give you the context to knowing something different has happened in regard to entities and individuals concerned.</p> <p>A holistic view enables you to connect these counter parties to see if these financial interactions make sense. The ability to monitor activity in context of a holistic view enables the organization to have valuable insights on what these individuals are doing. This information can in turn be used to more effectively assess an individual for \\glsxtrshort{aml} issues and risk. This is an important lower level analysis task that knowledge graph excels at because as most large scale money laundering tends to involve networks of individuals and organizations with a controlling force. The EKG enables the easier identification of all networks (bank accounts, transactions and customers) which in turn allows for swift analysis of alerts. A cluster of automatic alerts all in a given network identified by the \\glsxtrshort{ekg} can be swifty escalated for review (this is detailed further in the use case \\usecaseref{uc:aml}).</p>","title":"High Net Worth Individuals"},{"location":"use-case/client-360/know-your-customer/identification-verification/","text":"","title":"Identification Verification"},{"location":"use-case/client-360/know-your-customer/money-laundering/","text":"","title":"Money Laundering"},{"location":"use-case/client-360/know-your-customer/peps/","text":"","title":"Politically Exposed Persons (PEPs)"},{"location":"use-case/client-360/know-your-customer/risk-management/","text":"","title":"Risk Management"},{"location":"use-case/client-360/know-your-customer/sanctions/","text":"","title":"Sanctions"},{"location":"use-case/client-360/know-your-customer/core-record-management/","text":"<ul> <li>Countries</li> <li>Regions</li> <li>Jurisdictions</li> <li>Legal Entities</li> <li>Locations</li> <li>Buildings</li> <li>Addresses</li> <li>Audit</li> <li>...</li> </ul>","title":"Core Record Management"},{"location":"use-case/client-360/know-your-customer/core-record-management/addresses/","text":"","title":"Addresses"},{"location":"use-case/client-360/know-your-customer/core-record-management/audit/","text":"","title":"Audit"},{"location":"use-case/client-360/know-your-customer/core-record-management/buildings/","text":"","title":"Buildings"},{"location":"use-case/client-360/know-your-customer/core-record-management/countries/","text":"","title":"Countries"},{"location":"use-case/client-360/know-your-customer/core-record-management/jurisdictions/","text":"","title":"Jurisdictions"},{"location":"use-case/client-360/know-your-customer/core-record-management/legal-entities/","text":"<p>Client 360 / Know Your Customer depends on  Legal Entity Management.</p>","title":"Legal Entities"},{"location":"use-case/client-360/know-your-customer/core-record-management/locations/","text":"","title":"Locations"},{"location":"use-case/client-360/know-your-customer/core-record-management/regions/","text":"","title":"Regions"},{"location":"use-case/client-360/relationships-and-connections/","text":"<ul> <li>Business Connections </li> <li>Family Connections </li> <li>Political Connections </li> <li>Social Connections </li> </ul>","title":"Relationships &amp; Connections"},{"location":"use-case/client-360/relationships-and-connections/business-connections/","text":"","title":"Business Connections"},{"location":"use-case/client-360/relationships-and-connections/family-connections/","text":"","title":"Family Connections"},{"location":"use-case/client-360/relationships-and-connections/political-connections/","text":"","title":"Political Connections"},{"location":"use-case/client-360/relationships-and-connections/social-connections/","text":"<p>See also Social Graph.</p>","title":"Social Connections"},{"location":"use-case/client-360/social-media/","text":"<ul> <li>Social Graph</li> <li>Interest Graph</li> </ul>","title":"Social Media"},{"location":"use-case/client-360/social-media/interest-graph/","text":"","title":"Interest Graph"},{"location":"use-case/client-360/social-media/social-graph/","text":"","title":"Social Graph"},{"location":"use-case/cyber-security/","text":"","title":"Cybersecurity"},{"location":"use-case/digital-twin/","text":"<p>Digital Twin / Connected Inventory</p>","title":"Digital Twin"},{"location":"use-case/fraud-detection/","text":"<p>This is a test</p>","title":"Real-time Fraud Detection"},{"location":"use-case/legal-entity-management/","text":"<ul> <li>Corporate Actions<ul> <li>Merger &amp; Acquisition History</li> <li>Spin-offs</li> <li>Parents and Subsidiaries</li> <li>Stock Splits</li> <li>Dividends</li> </ul> </li> <li>Signatories</li> <li>Directorships</li> <li>Legal Form</li> <li>Business Registration</li> <li>Commercial Register</li> <li>Contacts</li> <li>Addresses</li> <li>Dissolution</li> <li>Liquidation</li> <li>Ownership</li> <li>Control</li> <li>Shares &amp; Ownership</li> <li>Share Capital</li> <li>Issued Capital</li> <li>Liability Terms</li> <li>Organizational structure</li> <li>Classification</li> <li>Ratings</li> <li>Assets</li> <li>Fundamentals</li> <li>Earnings estimates</li> </ul>","title":"Legal Entity Management"},{"location":"use-case/legal-entity-management/#depends-on","text":"<p>Legal Entity Management depends on the following generic use cases:</p> <ul> <li>Compliance</li> <li>Documents</li> <li>Currencies</li> </ul>","title":"Depends on:"},{"location":"use-case/legal-entity-management/addresses/","text":"","title":"Addresses"},{"location":"use-case/legal-entity-management/assets/","text":"","title":"Assets"},{"location":"use-case/legal-entity-management/business-registration/","text":"","title":"Business Registration"},{"location":"use-case/legal-entity-management/classification/","text":"","title":"Classification"},{"location":"use-case/legal-entity-management/commercial-register/","text":"","title":"Commercial Register"},{"location":"use-case/legal-entity-management/compliance/","text":"","title":"Compliance"},{"location":"use-case/legal-entity-management/contacts/","text":"","title":"Contacts"},{"location":"use-case/legal-entity-management/control/","text":"","title":"Control"},{"location":"use-case/legal-entity-management/currencies/","text":"","title":"Currencies"},{"location":"use-case/legal-entity-management/directorships/","text":"","title":"Directorships"},{"location":"use-case/legal-entity-management/dissolution/","text":"","title":"Dissolution"},{"location":"use-case/legal-entity-management/documents/","text":"","title":"Documents"},{"location":"use-case/legal-entity-management/earnings-estimates/","text":"","title":"Earnings Estimates"},{"location":"use-case/legal-entity-management/fundamentals/","text":"","title":"Fundamentals"},{"location":"use-case/legal-entity-management/issued-capital/","text":"","title":"Issued Capital"},{"location":"use-case/legal-entity-management/legal-form/","text":"","title":"Legal Forms"},{"location":"use-case/legal-entity-management/liability-terms/","text":"","title":"Liability Terms"},{"location":"use-case/legal-entity-management/liquidation/","text":"","title":"Liquidation"},{"location":"use-case/legal-entity-management/organizational-structure/","text":"","title":"Organizational Structure"},{"location":"use-case/legal-entity-management/ownership/","text":"","title":"Ownership"},{"location":"use-case/legal-entity-management/ratings/","text":"","title":"Ratings"},{"location":"use-case/legal-entity-management/share-capital/","text":"","title":"Share Capital"},{"location":"use-case/legal-entity-management/shares/","text":"","title":"Shares"},{"location":"use-case/legal-entity-management/signatories/","text":"","title":"Signatories"},{"location":"use-case/legal-entity-management/corporate-actions/","text":"","title":"Corporate Actions"},{"location":"use-case/legal-entity-management/corporate-actions/dividends/","text":"","title":"Dividends"},{"location":"use-case/legal-entity-management/corporate-actions/merger-and-acquisition-history/","text":"","title":"Merger &amp; Acquisition History"},{"location":"use-case/legal-entity-management/corporate-actions/parents-and-subsidiaries/","text":"","title":"Parents &amp; Subsidiaries"},{"location":"use-case/legal-entity-management/corporate-actions/spin-offs/","text":"","title":"Spin-offs"},{"location":"use-case/legal-entity-management/corporate-actions/stock-splits/","text":"","title":"Stock Splits"},{"location":"use-case/organization-management/","text":"","title":"Organization Management"},{"location":"use-case/risk-management/","text":"","title":"Real-time Enterprise Risk Management"}]})