In this step, you'll create a network policy for this account that references the shared network rules from your Organization Account. This ensures consistent network access controls across all accounts in your organization.

**Account Context:** This step should be executed from the newly created account.

## **Why is this important?**

Using the shared network rules provides:
- **Consistency**: All accounts use the same IP allowlists
- **Centralized Management**: Update rules once in the Organization Account, applied everywhere
- **Reduced Configuration Errors**: No need to re-enter IP addresses
- **Simplified Auditing**: Single source of truth for network access

## **Prerequisites**

- Infrastructure database replica created (access to replicated network rules)
- Network rules created in Platform Foundation (Configure Network Rules and Policies step)

## **Key Concepts**

**Replicated Network Rules**
Network rules are schema-level objects that were created in your Organization Account's Infrastructure database. When you created the infrastructure database replica, these rules became local objects in this account — and unlike shared rules, replicated rules can be referenced in local network policies.

**Account-Level Network Policy**
While network rules can be shared, network policies are account-level objects. You'll create a policy in this account that references the shared rules.

**Policy References Replicated Rules**
The network policy in this account will reference the fully-qualified names of the replicated network rules (e.g., `{{ platform_database_name | upper }}.GOVERNANCE.CORPORATE_VPN`).

**More Information:**
* [Network Rules](https://docs.snowflake.com/en/user-guide/network-rules) — Schema-level network rules
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) — Account-level policies

### Configuration Questions

#### What name should be used for this account? (`new_account_name`: text)
**What is this asking?**
Confirm or customize the account name. Based on your Platform Foundation naming conventions, a suggested name was generated in the previous step.

**Naming Requirements:**
- Must be unique within your organization
- Can contain letters, numbers, and underscores
- Cannot start with a number
- Maximum 255 characters
- Will be converted to uppercase internally

**Recommended Format:**
Based on your Platform Foundation settings, follow this pattern:
- If prefix is used: `{prefix}_{domain}_{environment}` or `{prefix}_{environment}_{domain}`
- If no prefix: `{domain}_{environment}` or `{environment}_{domain}`

**Examples:**
- `ACME_SALES_PROD`
- `ACME_DEV_FINANCE`
- `ANALYTICS_TEST`

**Best Practice:**
Use the suggested name from the previous step unless you have a specific reason to customize it. Consistent naming makes governance and cost allocation easier.

#### What do you want to name the platform database? (`platform_database_name`: text)
**What is the Platform/Infrastructure Database?**  
  The Infrastructure Database is a centralized "hub" database that houses platform-wide objects including tags, network rules, governance policies, and shared procedures. It is owned by the central platform team and shared across all accounts in multi-account deployments.  
  **Recommended Naming Approach:**  
  Use a name that clearly identifies this as a platform-owned, infrastructure-focused database. The format should be: \<domain\>\_\<dataproduct\>  
  * **Domain:** Use plat (short for "platform") or your platform team's acronym (e.g., cdp, snow, data)  
  * **Data Product:** Use infra or another term indicating infrastructure purpose  
* **Example:** PLAT\_INFRA — clearly indicates Platform team ownership and Infrastructure purpose  
  **Alternative Examples:**  
  * CDP\_INFRA — Cloud Data Platform Infrastructure  
  * SNOW\_ADMIN — Snowflake Administration  
  * DATA\_PLATFORM — Data Platform database  
* **Important:** Choose carefully\! This name will eventually be referenced by dozens to hundreds of objects, policies, and procedures. Changing it later can be complex and risky.  
  **More Information:**  
  * [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)  
  * [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)

#### What do you want to name the governance schema? (`governance_name`: text)
**What is the Governance Schema?**  
  The Governance schema is created within the Infrastructure Database and contains objects related to security, compliance, and platform governance. This includes platform and FinOps tags, network rules, audit views, and administrative procedures.  

  **Recommended Name:** GOVERNANCE  

  This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:  
  * ADMIN — Administration  
  * SECURITY — Security-focused objects  
  * PLATFORM — Platform-level objects  

**Schema Configuration:**  
  This schema will be created with **Managed Access** enabled, which means:  
  * Only the schema owner (typically [SYSADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system) - aka System Administrator) can grant privileges on objects  
  * Prevents "shadow" security configurations where object creators grant their own access  
  * Provides centralized control over who can access governance objects  

**Best Practice:** Use a simple, single-word name that represents the functional purpose.  
  
**More Information:**  
  * [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)  
  * [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)  
  * [System Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system)

#### Define the network rules for allowed IP addresses (`allowed_network_rules`: object-list)
**What is this asking?**
Create one or more network rules, each with a descriptive name and a list of IP addresses or CIDR ranges that should be allowed to connect to Snowflake.

**Why does this matter?**
Network rules define which IP addresses can access your Snowflake account. Grouping related IPs into named rules makes management and auditing easier.

**Fields:**
- **rule_name**: A descriptive name for the rule (e.g., `corporate_vpn`, `fivetran`, `tableau_cloud`)
- **cidr_blocks**: Comma-separated list of IP addresses or CIDR ranges (e.g., `192.168.1.0/24, 10.0.0.1`)

**Common rule examples:**
| Rule Name | CIDR Blocks | Purpose |
|-----------|-------------|---------|
| `corporate_vpn` | `203.0.113.0/24, 198.51.100.50` | Corporate VPN and office IPs |
| `fivetran` | `52.0.2.4, 34.75.100.0/24` | Fivetran ETL service |
| `tableau_cloud` | `44.192.0.0/16` | Tableau Cloud BI |
| `aws_lambda` | `3.5.0.0/16` | AWS Lambda functions |

**How to find IP ranges:**
- Corporate networks: Check with your IT/network team or use `curl ifconfig.me`
- Cloud services: Check the provider's documentation for published IP ranges
- Many services publish static IP lists that you can add

**Naming conventions:**
- Use lowercase with underscores: `corporate_vpn`, `dbt_cloud`
- Be descriptive: `ny_office` instead of just `office`
- Include the service name for third-party tools

**More Information:**
* [Network Rules](https://docs.snowflake.com/en/user-guide/network-rules)
* [CREATE NETWORK RULE](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule)

#### Define any network rules for blocked IP addresses (`blocked_network_rules`: object-list)
**What is this asking?**
Optionally create network rules for IP addresses that should be explicitly blocked from accessing Snowflake.

**Why does this matter?**
Block rules take precedence over allow rules. This is useful for blocking specific IPs within an otherwise allowed range.

**Fields:**
- **rule_name**: A descriptive name for the block rule (e.g., `blocked_regions`, `former_vendor`)
- **cidr_blocks**: Comma-separated list of IP addresses or CIDR ranges to block

**Example block rules:**
| Rule Name | CIDR Blocks | Purpose |
|-----------|-------------|---------|
| `blocked_countries` | `185.0.0.0/8, 91.0.0.0/8` | Block traffic from specific regions |
| `former_vendor` | `203.0.113.100, 203.0.113.101` | Block former vendor's static IPs |
| `known_malicious` | `192.0.2.0/24` | Known malicious IP range |
| `excluded_subnet` | `10.0.5.0/24` | Exclude specific subnet from broader allow |

**Use cases:**
- Blocking known malicious IP ranges
- Blocking specific hosts within an allowed CIDR range
- Blocking IPs from former vendors or partners
- Geographic restrictions (blocking entire country IP ranges)

**Leave empty** if you don't need to explicitly block any IPs. Most organizations only use allow rules.

**More Information:**
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies)

#### What is your Snowflake organization name? (`snowflake_org_name`: text)
Your Snowflake organization name is the first part of your account URL and connection identifiers. This is a required component of all Account Identifiers.  
  **How to find your organization name:**  
  Look at your current Snowflake URL. The organization name is the portion before the dash:  
  * https://\*\*ACME\*\*-prod.snowflakecomputing.com → Organization name is ACME  
  * https://\*\*XY12345\*\*-prod.snowflakecomputing.com → Organization name is XY12345  
* **Types of Organization Names:**  
  * **Custom Name:** A human-readable name like ACME or INITECH that was requested from Snowflake. These provide better branding and more readable URLs.  
  * **System-Generated:** An auto-assigned alphanumeric code like XY12345 or AB98765, created automatically during self-service sign up. Companies typically keep this name if transparency of your organization name in the URL is unnecessary or undesirable.   
* **To request a custom name:** If you have a system-generated name and want to change it, [contact Snowflake Support](https://community.snowflake.com/s/article/How-To-Submit-a-Support-Case-in-Snowflake-Lodge) or your account team. Custom names must be globally unique, start with a letter, and contain only letters and numbers.  
  **More Information:**  
  * [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) 

#### How would you like to configure security for this account? (`security_config_approach`: multi-select)
**What is this asking?**
Choose whether to replicate the Platform Foundation security settings or create custom settings for this account.

**Why does this matter?**
Consistent security settings across accounts simplify administration, reduce configuration errors, and make security audits easier. Custom settings are needed when an account has unique regulatory requirements or serves external users.

**Options explained:**

**Use Organization Configuration:**
- Applies the same settings from Platform Foundation
- Same IdP integration ({{ identity_provider }})
- Same network policy IP ranges
- Same authentication policy requirements
- Recommended for most accounts to maintain consistency

**Configure Custom Settings:**
- Allows different security settings for this account
- Can use a different IdP or manual user management
- Can have different network restrictions
- Can have different authentication requirements
- Best for: Accounts with unique regulatory requirements, partner accounts, or isolated environments

**Recommendation:**
Use organization configuration unless this account has specific requirements that differ from the standard. Consistency simplifies administration, auditing, and troubleshooting.

**More Information:**
* [Security Best Practices](https://docs.snowflake.com/en/user-guide/security-best-practices) — Snowflake security recommendations

**Note:** Even with organization configuration, this account will have its own:
- SCIM security integration (if applicable)
- Network rules and policies
- Authentication policies
- Administrator users
- Break-glass access
**Options:**
- Use Organization Configuration
- Configure Custom Settings
