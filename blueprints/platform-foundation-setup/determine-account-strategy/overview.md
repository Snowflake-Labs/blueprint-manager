In this step, you'll make a foundational decision that shapes your entire Snowflake platform:

1. **Account Strategy Selection** — Choose between Single Account or one of three Multi-Account patterns (Domain-based, Environment-based, or Domain + Environment)

This decision determines how every subsequent step in this workflow behaves. For example:

* **Single Account:** All databases, warehouses, and data products exist in one account  
* **Multi-Account:** You'll create additional accounts (in the Account Creation workflow) organized by domain, environment, or both

Your answer here (account_strategy) is referenced throughout this workflow to customize SQL output and guidance, and is inherited by the Account Creation and Data Product workflows.

## **Why is this important?**

Choosing your Snowflake account strategy is a critical foundational decision that determines how you’ll organize workloads, manage security boundaries, and allocate costs. The right strategy depends on your organization's size, compliance requirements, and operational model. This decision typically involves balancing **isolation** (for security and compliance) with **operational simplicity**. This guide helps you decide between a single-account or multi-account approach and whether to enable organization features. It details the decision criteria to help you choose between four primary strategies, listed by increasing complexity:

1. Single Account  
2. Multi-Account (Domain-based)  
3. Multi-Account (Environment-based)  
4. Multi-Account (Domain + Environment)

## **Prerequisites**

None

## **Key Concepts**

To select an account strategy, it is essential to understand what a Snowflake **account** is and the hierarchy of Snowflake objects:

**Snowflake Object Hierarchy**

![Snowflake Object Hierarchy](../../images/account_strategy_images/snowflake_object_hierarchy.png)

[**Organization**](https://docs.snowflake.com/en/user-guide/organizations) - An organization is a first-class Snowflake object that links the accounts owned by your business entity. This object exists whether or not you choose to create an organization account. An [**organization account**](https://docs.snowflake.com/en/user-guide/organization-accounts) (optional) is a special type of account that organization administrators use to perform tasks that affect all accounts under the organization (e.g., view org level data and query history, manage users across accounts, etc). 
* **[Snowflake Accounts](https://docs.snowflake.com/en/user-guide/organizations-connect)** - customers can create one or more accounts within an Organization. Each has its own distinct URL composed of the organization and account name. Each account is deployed in a single Cloud Provider (AWS, Azure, GCP) region with a specific [Snowflake Edition](https://docs.snowflake.com/en/user-guide/intro-editions).  
  * **Accounts contain [databases](https://docs.snowflake.com/en/guides-overview-db)** - each database belongs to a single Snowflake account; databases can be replicated to other accounts but they cannot span multiple accounts  
    * **Databases contain [schemas](https://docs.snowflake.com/en/sql-reference/commands-database#schema)** - each schema belongs to a single Snowflake database  
      * **Schemas contain objects** - objects include tables, views, file formats, sequences, UDFs, procedures, etc.

## **Considerations**

The key decision you’ll need to make is whether or to pursue a single or multi-account strategy for your Snowflake setup. Before reviewing the strategies, we recommend answering the following questions:

1. **Data Storage Requirements**: Do your source systems reside in **multiple cloud providers** (AWS, Azure, GCP) or **multiple regions**, necessitating multi-cloud/multi-region organization?  
2. **Isolation Requirements:** Do you have strict compliance rules (e.g., HIPAA, PCI, GDPR) that require physical separation of production data by environment or region?  
3. **Cost Management:** Do you need precise, separate invoices for different business units, or is a single bill acceptable?  
4. **Governance Model:** Is your governance centralized (one team manages everything) or decentralized (autonomous business units manage their own data)?  
5. **Operational Complexity:** How large is your platform team? Does your team have the staffing/maturity to manage the infrastructure of many accounts?  
6. **Future Growth:** Are you planning to expand into new regions or acquire other companies?  
7. **Disaster Recovery (DR) / Business Continuity**: Is multi-region or multi-cloud failover a requirement?

## **Best Practices**

### Always create an Organization Account

Even if you’re leaning toward a single account initially, if there is any potential in the future for more than one account, it will be best to set up the [Organization Account]((https://docs.snowflake.com/en/user-guide/organization-accounts)) at the onset as this allows for centralization of several key features.

### Common Multi-Account Strategies

For customers wanting to implement a multi-account strategy, we recommend segregating accounts by one or both of the following:

**By Environment**

An **Environment** represents a stage in the Software Development Life Cycle (SDLC). It is used to isolate the data/app product development stages based on their maturity and stability.

* **Definition:** An SDLC phase used to separate development, testing, and production workloads  
* **Examples:** SBX (Sandbox), DEV (Development), TST (QA/Testing), PRD (Production)  
* **Role in Strategy:** Environments isolate changes to prevent non-production activities from impacting production stability. In an environment-based multi-account strategy, distinct accounts are created for each stage (e.g., <org>_DEV, <org>_PROD)

**By Domain**

A **Domain** represents a logical grouping of business functions, data, or ownership. It is typically used to define boundaries for governance, cost allocation, and data stewardship.

* **Definition:** A business unit/entity, and/or departments  
* **Examples:** SupplyChain, Retail, Manufacturing, and/or Finance, Marketing, HR  
* **Role in Strategy:** In multi-account strategies, domains often serve as one of the primary boundaries for separate Snowflake accounts (e.g., a dedicated HR account to ensure autonomy or Manufacturing for clear chargeback)

### **Account Strategy Options**

NOTE: The options in this guide are common Snowflake account strategies, synthesized from industry best practices and typical customer requirements. They are oriented towards customers using [Snowflake Standard or Enterprise editions](https://docs.snowflake.com/en/user-guide/intro-editions). While our experience is that following these patterns typically leads to successful outcomes for organizations, each organization is unique. If after reading this guide you believe additional support is required to choose the right solution, please reach out to your account and/or services team before proceeding to the next steps.

Customers should also seek additional guidance if they have highly complex, specialized, or strict regulatory requirements. We recommend checking out [Snowflake Professional Services](https://www.snowflake.com/en/solutions/professional-services/) and/or our [Partner offerings](https://www.snowflake.com/en/why-snowflake/partners/)\!

|  | Single Account | Multi-Account (Environment) | Multi-Account (Domain) | Multi-Account (Domain + Env) |
| :---- | :---- | :---- | :---- | :---- |
| **Requirement** | "We need to get started quickly with minimal overhead for a PoC or a small team." | "Production data must be physically separated from developers." | "The Marketing team pays for their own compute and manages their own admins." | "We need strict regulatory compliance AND autonomous business units." |
| **Ideal For** | Proof-of-concept or Small Orgs | Compliance Software Development | Autonomous business units | Larger enterprises |
| **Primary Data Isolation** | Logical (Database/Schema) | Physical (Account) | Physical (Account) | Physical (Account) |
| **Cost Tracking** | Requires Tagging | Separate bills per eomain | Separate bills per domain | Precise granularity |
| **Data Sharing** | Zero Copy Cloning | Data Sharing | Secure Data Sharing | Complex Sharing |
| **Complexity** | Low | Medium | Medium | High |

### **Which strategy is right for my organization?**

**1. Single Account Strategy**  
**Best For:** Small organizations, centralized data teams, and proof-of-concepts.

**How does this strategy work?**

In this model, all data environments (Dev, Test, Prod) and business domains exist within one Snowflake account.

**Pros and Cons**

* **Pros:**  
  * **Simplified Operations:** Provides for an integrated, enterprise view of your data; lowest administrative overhead; single pane of glass for monitoring.  
  * **Data Accessibility:** Easiest cross-database queries and joins; zero-copy cloning is available between environments (e.g., cloning Prod to Dev).  
  * **Centralized Governance:** Security and policies are managed in one place.  
* **Cons:**  
  * **Risk:** Lower isolation; a change in a non-production environment could theoretically impact production resource limits.  
  * **Security Boundaries:** Single security boundary for all data.

**Is this right for you?**

✅ **Choose this strategy if:**

* You have a **centralized data team** that manages all data assets and security.  
* You want the **simplest possible administration** with a "single pane of glass" for monitoring  
* You prioritize **developer agility**, such as the ability to use "Zero-Copy Cloning" to instantly create Dev environments from Prod data  
* You have **simple cost allocation** needs that can be handled by tagging resources rather than separate invoices.

❌ **Avoid this strategy if:**

* You have strict compliance requirements that mandate **physical isolation** of production data  
* You have distinct business units that require **complete autonomy** over their own security and release schedules.

---

**2. Multi-Account (Environment-based)**  
**Best For:** Organizations requiring strong isolation between Software Development Lifecycle (SDLC) stages (e.g., Dev, Test, Prod).

**How does this strategy work?**

This strategy separates environments into distinct Snowflake accounts. A common pattern is one account for Production and separate accounts for each of the Non-Production environments (Dev & Test).

**Pros & Cons**

* **Pros:**  
  * **Maximum SDLC Isolation:** Strongest separation between production and non-production workloads; reduces the risk of non-prod impacting production performance.  
  * **Independent Security:** Security controls and access policies can be distinct for each environment.  
  * **Cost Optimization:** Ability to use different Snowflake Editions per environment to optimize costs
  * **Compliance:** Often required for strict regulatory environments.  
* **Cons:**  
  * **Data Friction:** You cannot "clone" databases across accounts. Moving data from Prod to Dev requires data sharing or replication, which adds complexity.  
  * **Operational Overhead:** Requires managing security and users across multiple accounts.

**Is this right for you?**

✅ **Choose this strategy if:**

* **Environment isolation is critical:** You need to ensure that non-production workloads (Dev/Test) strictly cannot impact Production performance or security limits  
* **Security policies differ by environment:** For example, you need strict IP allow-listing for Production but looser access for Development  
* **Compliance is a driver:** Your audit or regulatory requirements specify distinct boundaries for production environments  
* You want to enable **different Snowflake Editions** (e.g., Standard for Dev, Business Critical for Prod) to optimize costs.

❌ **Avoid this strategy if:**

* Your teams rely heavily on **instant cloning** of production data for testing. Moving data between accounts requires replication or data sharing, which adds friction

---

**3. Multi-Account (Domain-based)**  
**Best For:** Large enterprises with autonomous business units (Domains) that operate independently.

**How does this strategy work?**

In this federated model, distinct business units (e.g., Finance, Marketing, HR) are given their own accounts. This aligns with a **Data Mesh** architecture where domains have decentralized accountadmin level ownership.

**Pro & Cons**

* **Pros:**  
  * **Cost Allocation:** precise chargeback; you know exactly how much each business unit is spending.  
  * **Autonomy:** Domains can govern their own data, release schedules, and maintenance windows independently.  
  * **Scalability:** Independent scaling of compute resources per domain.  
* **Cons:**  
  * **Complexity:** Higher complexity in governance and standardization.  
  * **Silos:** Requires a robust data sharing framework to prevent data silos and enable cross-domain analytics.

**Is this right for you?**

✅ **Choose this strategy if:**

* **Decentralized ownership is the goal:** You follow a **Data Mesh** architecture where business units (e.g., Finance, Marketing) operate as independent entities with their own administrators  
* **Chargeback is a priority:** You need clear, separate billing for each business unit without complex tagging logic  
* **Data sovereignty/Residency:** Your domains operate in different geographic regions (e.g., EU data must stay in an EU account)  
* Different domains have **different release cadences** or maintenance windows

❌ **Avoid this strategy if:**

* Your business units frequently need to **join data across domains**. Cross-account data sharing works well but requires more setup than simple cross-database joins

---

**4. Multi-Account (Domain + Environment)**  
**Best For:** Large organizations requiring maximum isolation and precise control over both domains and environments.

**How does this strategy work?**

This is the most complex and granular strategy. Each Business Unit has separate accounts for their environments (e.g., Finance_Prod, Finance_Dev, Marketing_Prod).

**Pros & Cons**

* **Pros:**  
  * **Total Isolation:** Strongest security and compliance posture with clear ownership boundaries.  
  * **Granular Chargeback:** Most precise tracking of costs by team and lifecycle stage.  
* **Cons:**  
  * **High Overhead:** Highest operational complexity; requires automation to manage the large number of accounts.  
  * **Data Movement:** Requires extensive data sharing and replication configuration to move data between domains and environments.

**Is this right for you?**

✅ **Choose this strategy if:**

* You are a **large enterprise** with complex governance needs that cannot be met by the other strategies  
* You require the **highest level of isolation**: A breach or issue in "Marketing Dev" must technically be impossible to affect "Finance Prod"  
* You have a **mature platform team** capable of automating the management of dozens or hundreds of accounts

❌ **Avoid this strategy if:**

* You do not have robust **automation (Infrastructure as Code)**. Managing this many accounts manually is operationally prohibitive

## **More Information**

* [Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Overview of Snowflake organizations  
* [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts) — Managing multiple accounts with an organization account  
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) — Feature comparison across editions  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) — Understanding account naming and URLs  
* [Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) — Sharing data across accounts  
* [Database Replication](https://docs.snowflake.com/en/user-guide/database-replication-intro) — Replicating data between accounts

### Configuration Questions

#### What account strategy do you wish to implement? (`account_strategy`: multi-select)
Choose the account strategy that best fits your organization. Your choice determines how domain (business unit/entity) and environment are organized:  
  **Single Account:**  
  * Best for: Small to medium organizations, centralized teams, simpler governance  
  * Naming: Domain \+ Environment \+ Data Product at database level  
  * Pros: Lower operational overhead, easier cross-database queries, centralized management  
  * Cons: Less isolation, shared resource limits, single security boundary  
  * Recommendation: Consider setting up an organization account even for single-account deployments to enable future growth  
* **Multi-Account (Environment-based):**  
  * Best for: Organizations requiring strong environment isolation (dev/test/prod)  
  * Naming: Environment at account level, Domain \+ Data Product at database level  
  * Pros: Complete environment isolation, independent security controls, separate billing  
  * Cons: More complex data sharing, higher operational overhead  
  * Requirement: Organization account required  
* **Multi-Account (Domain-based):**  
  * Best for: Large enterprises with autonomous business units/domains  
  * Naming: Domain at account level, Environment \+ Data Product at database level  
  * Pros: Clear cost allocation per domain, independent governance, domain autonomy  
  * Cons: Higher complexity, requires data sharing for cross-domain analytics  
  * Requirement: Organization account required  
* **Multi-Account (Domain \+ Environment):**  
  * Best for: Large organizations needing both domain and environment isolation  
  * Naming: Domain \+ Environment at account level, Data Product at database level  
  * Pros: Maximum isolation, clear ownership and environment separation  
  * Cons: Highest complexity and operational overhead, most accounts to manage  
  * Requirement: Organization account required  
* **More Information:**  
  * [Organizations](https://docs.snowflake.com/en/user-guide/organizations)  
  * [Managing Multiple Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts)  
**Options:**
- Single Account
- Multi-Account (Environment-based)
- Multi-Account (Domain-based)
- Multi-Account (Domain + Environment)
