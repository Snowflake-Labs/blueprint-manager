# Platform Foundation

## Summary
Define your account strategy, configure account identifiers, set up centralized management,
create shared infrastructure, and organize your platform with domains, environments,
FinOps tags, and naming conventions.

## External Requirements
- Snowflake account (trial or provisioned)
- Organization information (org name from account URL)

## Personas
- Platform Administrator
- Cloud/Infrastructure Team

## Role Requirements
- ORGADMIN or ACCOUNTADMIN privileges
- Enterprise Edition or higher for Organization Account features

## Details
## **Steps in This Task**

| Step | Title | Purpose |
| :---- | :---- | :---- |
| 1.1 | Determine Account Strategy | Choose between single or multi-account architectures |
| 1.2 | Configure Organization Name for Connectivity | Define how account URLs and identifiers are structured |
| 1.3 | Configure Organization Account | Decide whether to create a centralized management account |
| 1.4 | Create Organization Account | Provision the Organization Account (conditional—only if enabled in 1.3) |
| 1.5 | Create Infrastructure Database | Set up centralized metadata and governance storage |
| 1.6 | Define Domains, Environments & Naming Conventions | Establish domains, environments, FinOps tags, and account and object naming standards |
| 1.7 | Configure Infrastructure Database Sharing | Enable cross-account access to governance objects (multi-account only) |

### Network Policy for PAT Authentication (Trial Accounts)

If you are using a **trial account** and plan to authenticate using a **Programmatic Access Token (PAT)**, you must first create a network policy. Trial accounts require this for PAT authentication to work.

**Before running this blueprint with PAT authentication:**

1. Log into Snowsight manually using your username/password
2. Create a network policy allowing your IP address:

```sql
USE ROLE ACCOUNTADMIN;

-- Create network policy (replace YOUR_PUBLIC_IP with your actual IP address)
CREATE NETWORK POLICY allow_deployment_policy
  ALLOWED_IP_LIST = ('YOUR_PUBLIC_IP/32')
  COMMENT = 'Allow deployment from specific IP for PAT authentication';

-- Apply to your user (replace YOUR_USERNAME with your username)
ALTER USER YOUR_USERNAME SET NETWORK_POLICY = allow_deployment_policy;
```

3. Generate a PAT for your user in Snowsight (User Menu → Profile → Personal Access Tokens)
4. Configure the connection in `~/.snowflake/connections.toml`

**Note:** This requirement is specific to trial accounts. Production accounts provisioned by Snowflake typically do not have this restriction.

## **Account Execution Context**

Understanding where SQL commands are executed is critical:

| Steps | Account Context |
| :---- | :---- |
| 1.1 - 1.4 | Your **initial/trial account** - where you start |
| 1.5 - 1.7 | **Organization Account** (if created) OR initial account (if no org account) |

**Important**: If you create an Organization Account, you must **log into it** after it has been created. All remaining steps in the workflow will be executed from the Organization Account.

If you choose not to create an Organization Account, all steps are executed in your initial account.

## **Time Estimate**

This task typically takes **30-45 minutes** to complete, depending on the complexity of your organization's requirements and the level of discussion needed for strategic decisions.

## **Key Decisions**

Several questions in this task have long-term implications:

1. **Account Strategy**: Changing from single to multi-account (or vice versa) after implementation is a significant undertaking  
2. **Naming Conventions**: Object names are difficult to change after data is loaded and applications are connected  
3. **Domain/Environment Structure**: These become the foundation for access control, cost allocation, and data organization

Take time to involve relevant stakeholders when making these decisions.

## **Deliverables**

Upon completion, you will have:

* A documented account strategy with clear rationale  
* Configured (or documented) Organization Account settings  
* Infrastructure database with governance schema for platform-wide objects  
* Defined list of domains and environments with corresponding FinOps tags  
* Documented naming convention standards for databases, warehouses, and roles  
* Infrastructure database share configured for cross-account access (multi-account only)

## **More Information**

* [Snowflake Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Overview of organization structure  
* [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts) — Centralized management capabilities  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) — Understanding account URLs  
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) — Feature comparison across editions  
* [Introduction to Secure Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) — Cross-account data access