In this step, you'll configure network rules and policies to control which IP addresses and networks can access your Snowflake account.

**Account Context:** These network policies apply to your Organization Account (if created) or your primary account. Network rules are stored in the Infrastructure Database's governance schema.

## Why is this important?

Network policies are a critical security control that restricts access to your Snowflake account based on network location. Without network policies, anyone with valid credentials could access your account from anywhere in the world.

Network policies provide:
- **IP Allowlisting**: Only allow connections from trusted networks
- **Defense in Depth**: Additional layer beyond authentication
- **Compliance**: Meet regulatory requirements for network access controls
- **Reduced Attack Surface**: Limit exposure to credential-based attacks
- **Geographic Restrictions**: Prevent access from unexpected locations

## External Prerequisites

- List of corporate network IP ranges (offices, VPN, etc.)
- List of cloud service IPs that need access (ETL tools, BI tools)
- Understanding of your organization's network topology

## Key Concepts

**Network Rule**
A Snowflake object that defines a list of IP addresses or CIDR ranges. Think of network rules as "guest lists" that define who's allowed in from where.

**Network Policy**
A Snowflake object that combines network rules into allow/block lists. This is the "bouncer" that checks IP addresses against the guest list before allowing access.

**Account-Level Policy**
A network policy applied to the entire account—the "front door security" that applies to everyone by default.

**User-Level Policy**
A network policy applied to specific users. This is like a "VIP entrance" that overrides the standard front door rules for certain users.

**Best Practice: Defense in Depth**
Network policies are your first line of defense—even if credentials are stolen, attackers can't connect from unauthorized networks.

**More Information:**
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) — Overview of IP-based access control
* [Network Rules](https://docs.snowflake.com/en/user-guide/network-rules) — Creating and managing network rules
* [CREATE NETWORK RULE](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule) — SQL command reference

### Configuration Questions

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

#### Should the network policy be applied at the account level? (`enable_account_network_policy`: multi-select)
**What is this asking?**
Decide whether to apply the network policy to all users in the account by default, or only to specific users.

**Why does this matter?**
- **Yes (Account-level)**: All users must connect from allowed networks. More secure but requires complete IP list upfront.
- **No (User-level only)**: Network policy only applies to users you explicitly assign it to. More flexible during rollout.

**Recommendation:**
- Start with **No** during initial setup and testing
- Move to **Yes** once you've validated all required IPs are included
- Always ensure break-glass accounts can bypass the policy

**Caution:**
If you enable account-level policy without including all necessary IPs, you could lock yourself out!

**More Information:**
* [Activating Network Policies](https://docs.snowflake.com/en/user-guide/network-policies#activating-a-network-policy)
**Options:**
- Yes - Apply to all users by default
- No - Apply only to specific users

#### Which Identity Provider will you use for SCIM integration? (`identity_provider`: multi-select)
**What is this asking?**
Select the Identity Provider (IdP) that your organization uses to manage user identities. This IdP will be the source of truth for user provisioning to Snowflake.

**Why does this matter?**
Different IdPs have different configuration steps and capabilities. Snowflake provides specific documentation for major IdPs like Okta and Azure AD, while other SCIM 2.0 compatible providers use a generic configuration.

**Options explained:**
- **Okta**: Enterprise IdP with native Snowflake SCIM integration
- **Microsoft Entra ID (Azure AD)**: Microsoft's cloud identity service with gallery app for Snowflake
- **Other SCIM 2.0 Compatible IdP**: Any IdP that supports SCIM 2.0 protocol
- **None - Manual User Management**: Skip SCIM and manage users manually (not recommended)

**Recommendation:**
If your organization has an enterprise IdP, we strongly recommend configuring SCIM integration. The initial setup effort is minimal compared to the ongoing benefits of automated provisioning.

**More Information:**
* [SCIM Overview](https://docs.snowflake.com/en/user-guide/scim)
* [Supported Identity Providers](https://docs.snowflake.com/en/user-guide/scim#supported-identity-providers)
**Options:**
- Okta
- Microsoft Entra ID (Azure ID)
- Other SCIM 2.0 Compatible IdP
- None - Manual User Management

#### Who should be set up as administrators? (`manual_admin_users`: object-list)
**What is this asking?**
Define the administrators who will manage your Snowflake account. For each administrator, provide their details and specify their administrative role.

**SSO-Ready Recommendation: Use Email as Username**
We strongly recommend using the user's **email address** as the `username`, even if you are not currently using SSO. Benefits include:
- **SSO-Ready:** Most identity providers (Okta, Azure AD, etc.) use email as the default identifier. Using email now ensures seamless SSO integration later.
- **Uniqueness:** Email addresses are globally unique and prevent naming conflicts.
- **Consistency:** Users log in with the same identifier across all systems.

**Administrative Role (admin_role field)**

Enter ONE of the following values exactly as shown:

| Value to Enter | Purpose | Recommended Count |
|----------------|---------|-------------------|
| `ACCOUNTADMIN` | Full account control - most privileged role | 2-3 only |
| `SECURITYADMIN` | Manage security, grants, and access control | 2-5 |
| `SYSADMIN` | Manage databases, warehouses, infrastructure | 3-10 |
| `USERADMIN` | Manage users and custom roles | 2-5 |

**Important:** The `admin_role` field must be entered exactly as shown above (case-insensitive, but use uppercase for consistency).

**Example Entries (SSO-Ready):**

| username | email | first_name | last_name | admin_role |
|----------|-------|------------|-----------|------------|
| `john.smith@company.com` | `john.smith@company.com` | `John` | `Smith` | `ACCOUNTADMIN` |
| `jane.doe@company.com` | `jane.doe@company.com` | `Jane` | `Doe` | `ACCOUNTADMIN` |
| `bob.wilson@company.com` | `bob.wilson@company.com` | `Bob` | `Wilson` | `SYSADMIN` |

**Recommendations:**
- Create at least **2 ACCOUNTADMIN users** to prevent lockout scenarios
- Use individual accounts, not shared/generic accounts
- Use email addresses as usernames for SSO-readiness
- Use corporate email addresses (not personal emails)

**Security Notes:**
- All users will be created with `MUST_CHANGE_PASSWORD = TRUE`
- Users will receive an initial password that must be changed on first login
- Consider enabling MFA after initial setup (Enable Multi-Factor Authentication step)

**More Information:**
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user)
* [ACCOUNTADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-accountadmin-role)

#### Who should be granted administrative roles? (`scim_admin_users`: object-list)
**What is this asking?**
Define which SCIM-provisioned users should receive administrative roles. For each administrator, provide their login name and the role to grant.

**Login Name Format**

The login name must match exactly how the user was provisioned via SCIM from your Identity Provider:
- **Most common:** Email address (e.g., `john.smith@company.com`) - default for Okta, Azure AD
- **Alternative:** Username format (e.g., `john.smith`) - if your IdP is configured differently

**Tip:** Run `SHOW USERS;` in Snowflake to see the exact `LOGIN_NAME` format your IdP uses.

**Administrative Role (admin_role field)**

Enter ONE of the following values exactly as shown:

| Value to Enter | Purpose | Recommended Count |
|----------------|---------|-------------------|
| `ACCOUNTADMIN` | Full account control - most privileged role | 2-3 only |
| `SECURITYADMIN` | Manage security, grants, and access control | 2-5 |
| `SYSADMIN` | Manage databases, warehouses, infrastructure | 3-10 |
| `USERADMIN` | Manage users and custom roles | 2-5 |

**⚠️ Important:** The `admin_role` field must be entered exactly as shown above (case-insensitive, but use uppercase for consistency).

**Example Entries:**

| login_name | admin_role |
|------------|------------|
| `john.smith@company.com` | `ACCOUNTADMIN` |
| `jane.doe@company.com` | `ACCOUNTADMIN` |
| `bob.wilson@company.com` | `SYSADMIN` |
| `alice.chen@company.com` | `SECURITYADMIN` |

**Recommendations:**
- Create at least **2 ACCOUNTADMIN users** to prevent lockout scenarios
- Use individual accounts, not shared/generic accounts
- ACCOUNTADMIN users will also be granted SECURITYADMIN and SYSADMIN for role hierarchy

**SCIM Provisioning Reminder:**
Users must first be provisioned through SCIM before roles can be granted. Run the SQL **after** users appear in `SHOW USERS;`.

**More Information:**
* [ACCOUNTADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-accountadmin-role)
* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles)
