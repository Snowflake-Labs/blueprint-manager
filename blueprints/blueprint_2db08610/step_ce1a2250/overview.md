In this step, you'll configure who receives notifications when resource monitor thresholds are triggered. This step produces:

1. **Email Recipients** (`resource_monitor_emails`) — List of email addresses that receive threshold alerts
2. **Updated Monitor Configuration** — Resource monitor is modified to include notification recipients

When thresholds are reached, Snowflake sends email notifications to all configured recipients. This enables timely response—teams can investigate usage spikes before limits are reached.

**Notification Timing**:
- Alerts are sent when Snowflake's monitoring process detects a threshold breach
- There may be a slight delay (up to 30 minutes) between actual usage and notification
- For immediate awareness, configure multiple thresholds (75%, 90%, 100%)

This is the final step of the Data Product Configuration workflow. After completing this step, your data product is fully provisioned with databases, schemas, roles, warehouses, and cost controls.

**Account Context:** Execute this SQL from the target account with ACCOUNTADMIN role.

## **Why is this important?**

Notifications enable timely response:
- **Early Warning**: Act before limits are reached
- **Accountability**: Right people get the alerts
- **Governance**: Documented cost awareness

Think of notifications as smoke detectors — they alert you to problems before they become emergencies.

## **Prerequisites**

- Resource monitor created and assigned (Create Resource Monitors, Assign Monitors to Warehouses)
- Email addresses for notification recipients
- Notification integration configured (if using webhooks)

## **Key Concepts**

**Email Notifications**
The default notification method:
- Sent to account administrators by default
- Can add additional recipients
- Arrive when thresholds are triggered

**Notification Delay**
Alerts may have slight delay:
- Snowflake checks usage every 15-30 minutes
- Threshold crossing detected on next check
- Email sent within minutes of detection

**Webhook Integration**
For Slack, Teams, or custom integrations:
- Requires notification integration setup
- More complex but enables automation
- Configured at account level in Platform Foundation

**More Information:**
* [Resource Monitor Notifications](https://docs.snowflake.com/en/user-guide/resource-monitors#notifications) — Alert configuration
* [Notification Integrations](https://docs.snowflake.com/en/user-guide/notifications/notification-integrations) — Webhook setup

### Configuration Questions

#### Who should receive resource monitor alerts? (`resource_monitor_emails`: list)
Enter the email addresses of people who should be notified when thresholds are triggered.

**Recommended recipients:**
- Data product owner
- FinOps or cloud cost team
- Engineering lead

**Why does this matter?**
The right notifications ensure:
- Timely response to cost alerts
- Accountability for spending
- No surprise bills

**Example:**
```
data.team@company.com
finance@company.com
john.smith@company.com
```

**Note:** Account administrators receive all notifications by default, regardless of this setting.

#### Which environment is this data product being deployed to? (`data_product_environment`: multi-select)
**What is this asking?**
Select the SDLC environment for this data product deployment.

**Auto-Detection for Multi-Account Strategies:**
- **Environment-based accounts**: Your environment is determined by your target account. Select the matching value.
- **Domain + Environment accounts**: Your environment is derived from the second part of your account name. Select the matching value.
- **Domain-based accounts**: Environment is not determined by your account. Select from the available options.
- **Single Account**: Environment is not determined by your account. Select from the available options.

**Why does this matter?**
Environment assignment determines:
- **Isolation**: Resources are created in the appropriate context
- **Access Controls**: Production typically has stricter access
- **Resource Sizing**: Dev environments may use smaller warehouses
- **Data Sensitivity**: Production may have real data vs. synthetic in dev

**Common Environments:**
| Abbreviation | Full Name | Purpose |
|--------------|-----------|---------|
| `dev` | Development | Building and testing code |
| `test` | Testing/QA | Quality assurance |
| `stg` | Staging | Pre-production validation |
| `prod` | Production | Live environment |

**Recommendation:**
For environment-based and domain+environment strategies, select the environment that matches your target account name.

#### What is the name of this data product? (`data_product_name`: text)
**What is this asking?**
Provide a descriptive name for your data product. This name will be used in database names, role names, and resource tags.

**Why does this matter?**
The data product name is a key component of object naming:
- Databases: `<domain>_<dataproduct>_<zone>_<env>` (based on your naming convention)
- Roles: `<dataproduct>_owner`, `<dataproduct>_reader`
- Tags: `DATAPRODUCT = '<dataproduct>'`

A clear, descriptive name makes resources easy to identify and manage.

**Naming Guidelines:**
- Use lowercase, single words or concatenated words (no underscores)
- Underscores are reserved for separating naming components (domain, zone, env)
- Be descriptive but concise
- Reflect the business purpose or use case
- Avoid technical jargon unless widely understood
- Avoid reserved words or special characters

**Examples:**
| Name | Description |
|------|-------------|
| `customer360` | Unified customer data and analytics |
| `salesanalytics` | Sales reporting and analysis |
| `supplychain` | Supply chain operations data |
| `finreporting` | Financial reporting and compliance |
| `marketing` | Marketing campaign attribution |
| `productcatalog` | Product information management |
| `inventory` | Inventory tracking and forecasting |

**Recommendation:**
Choose a name that business users would recognize. Ask: "If someone searched for this data, what would they type?"

**More Information:**
* [Identifier Requirements](https://docs.snowflake.com/en/sql-reference/identifiers-syntax) — Valid characters and length limits

#### What core component ordering will be used for account-level object names? (`object_component_order`: multi-select)
**Why Order Matters:**  
Snowflake displays objects alphabetically. The component order determines how objects cluster together in Snowsight, BI tools, and queries.  

**Option 1: `<domain>_<env>_<dataproduct>`**  
* Objects cluster by **domain first**, then by environment  
* All Finance objects together, all Marketing objects together  
* Example: `FIN_PROD_ANALYTICS`, `FIN_DEV_ANALYTICS`, `MKT_PROD_CAMPAIGNS`  
* Best for: Organizations where domain ownership is primary  

**Option 2: `<domain>_<dataproduct>_<env>`**  
* Objects cluster by **domain first**, then by data product  
* All Finance Analytics together across environments  
* Example: `FIN_ANALYTICS_PROD`, `FIN_ANALYTICS_DEV`, `MKT_CAMPAIGNS_PROD`  
* Best for: Data product-centric organizations  

**Option 3: `<env>_<domain>_<dataproduct>`**  
* Objects cluster by **environment first**  
* All Production objects together, all Development objects together  
* Example: `PROD_FIN_ANALYTICS`, `PROD_MKT_CAMPAIGNS`, `DEV_FIN_ANALYTICS`  
* Best for: Operations teams focused on environment-based management  

**Recommendation:** Most organizations prefer `<domain>_<env>_<dataproduct>` or `<domain>_<dataproduct>_<env>` for domain-centric clustering.  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  
**Options:**
- <domain>_<env>_<dataproduct>
- <domain>_<dataproduct>_<env>
- <env>_<domain>_<dataproduct>

#### Which account will this data product be deployed to? (`target_account_name`: text)

**What is this asking?**
Enter the name of the Snowflake account where this data product will be created.

**Why does this matter?**
This ensures all generated SQL is clearly documented with the target account, preventing deployment errors and providing clear audit trails.

**How to find your account name:**
- In Snowsight: Click your account name in the bottom-left corner
- Run SQL: `SELECT CURRENT_ACCOUNT_NAME();`
- From your URL: `https://<org>-<account>.snowflakecomputing.com`

**Examples based on strategy:**

**Domain-based strategy:**
- `ACME_SALES` - Sales domain account
- `ACME_FINANCE` - Finance domain account

**Environment-based strategy:**
- `ACME_DEV` - Development environment account
- `ACME_PROD` - Production environment account

**Domain + Environment strategy:**
- `ACME_SALES_DEV` - Sales domain, Development environment
- `ACME_FINANCE_PROD` - Finance domain, Production environment

**Recommendation:**
Copy the exact account name from your Snowflake session to avoid typos.

**More Information:**
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) — Understanding account names

#### What should happen when the credit limit is reached? (`resource_monitor_action`: multi-select)
Choose the action when 100% of credits are consumed:

- **Notify Only**: Warehouses continue running. Use for non-critical data products or when you'll manually intervene.
- **Suspend**: Warehouses stop after current queries complete. Recommended for most data products.
- **Suspend Immediately**: Kills in-flight queries and stops warehouses. Use for strict budget enforcement.

**Why does this matter?**
- Too aggressive → Queries fail unexpectedly
- Too permissive → Costs exceed budget

**Recommendation:** Start with "Suspend" for production, "Notify Only" for development.
**Options:**
- Notify Only (continue running)
- Suspend (stop warehouse gracefully)
- Suspend Immediately (kill queries and stop)

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

#### Which domain does this data product belong to? (`data_product_domain`: multi-select)
**What is this asking?**
Select the business domain (team, department, or organizational unit) that owns this data product.

**Auto-Detection for Multi-Account Strategies:**
- **Domain-based accounts**: Your domain is determined by your target account. Select the matching value.
- **Domain + Environment accounts**: Your domain is derived from the first part of your account name. Select the matching value.
- **Environment-based accounts**: Domain is not determined by your account. Select from the available options.
- **Single Account**: Domain is not determined by your account. Select from the available options.

**Why does this matter?**
Domain assignment determines:
- **Cost Allocation**: Credits consumed are attributed to this domain
- **Ownership**: The domain team is responsible for the data product
- **Access Patterns**: Domain-based roles may have different access levels
- **Governance**: Domain-specific policies may apply

**How domains are used:**
- Object names may include the domain abbreviation
- The `DOMAIN` tag is applied to all resources
- Cost reports can filter by domain

**Available Domains:**
Your organization defined these domains in Platform Foundation. If you need a new domain, update Platform Foundation first.

**If your domain isn't listed:**
Work with your platform team to add the domain to Platform Foundation, then return to this workflow.

**Recommendation:**
For domain-based and domain+environment strategies, select the domain that matches your target account name.
