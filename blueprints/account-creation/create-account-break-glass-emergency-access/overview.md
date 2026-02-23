In this step, you'll create a break-glass emergency access account for situations where normal authentication methods are unavailable. This account provides a way to access Snowflake during IdP outages or other authentication emergencies.

**Account Context:** This step should be executed from the newly created account.

## Why is this important?

Break-glass access is your emergency key:
- **IdP Outage**: If your Identity Provider is down, SSO users can't log in
- **Configuration Errors**: If authentication policies are misconfigured, admins may be locked out
- **Disaster Recovery**: In crisis situations, you need guaranteed access

Think of it as an "emergency key behind glass"—you break the glass only when all other options fail.

## External Prerequisites

- Designated break-glass account owner identified
- Secure credential storage solution (vault, password manager)
- Understanding of your organization's emergency access procedures

## Key Concepts

**Break-Glass Account**
A dedicated user account that bypasses SSO and uses password-only authentication. It's exempt from standard authentication policies that might prevent login.

**Password-Only Authentication**
The break-glass account uses only username and password—no SSO, no MFA dependency. This ensures it works even when external services are unavailable.

**Credential Security**
Break-glass credentials must be stored securely with limited access. Consider:
- Password vault with restricted access
- Printed credentials in a physical safe
- Escrow service with controlled release

**IP Restrictions**
Even break-glass accounts should be restricted to known, trusted IP addresses to prevent unauthorized use if credentials are compromised.

**More Information:**
* [MFA Best Practices](https://docs.snowflake.com/en/user-guide/security-mfa) — Emergency access recommendations
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Exempting users from policies

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

#### What name should be used for the local infrastructure database? (`local_infra_database`: text)
**What is the Local Infrastructure Database?**
The Local Infrastructure Database is a writable database within this account that stores account-specific administrative and governance objects. This is separate from the replicated infrastructure database which is read-only.

**Why is this needed?**
The infrastructure database replicated from the Organization Account is **read-only**. Account-specific objects like authentication policies, local procedures, and account-level configurations must be created in a local, writable database.

**Recommended Naming Approach:**
Use a name that clearly identifies this as a local, account-specific infrastructure database. Follow the same naming pattern as your platform infrastructure database. Consider formats like:
- `<domain>_LOCAL` — e.g., `PLAT_LOCAL`, `CDP_LOCAL`
- `<domain>_<account>` — e.g., `PLAT_SALES`, `PLAT_DEV`
- `LOCAL_<purpose>` — e.g., `LOCAL_INFRA`, `LOCAL_ADMIN`

**Example:** `PLAT_LOCAL` — clearly indicates Platform team ownership and local (non-replicated) scope

**Alternative Examples:**
- `CDP_LOCAL` — Cloud Data Platform local objects
- `<ACCOUNT>_INFRA` — Account-specific infrastructure (e.g., `SALES_INFRA`)
- `LOCAL_ADMIN` — Local administration database

**Important:** This name should be distinct from the replicated infrastructure database to avoid confusion.

**More Information:**
* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)

#### What schema name should be used for security policies? (`local_policies_schema`: text)
**What is the Policies Schema?**
The Policies Schema is created within the Local Infrastructure Database and contains account-specific security objects including authentication policies, network policies, and other configurations that cannot be replicated.

**Recommended Name:** `POLICIES`

This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:
- `SECURITY` — Security-focused objects
- `AUTH` — Authentication and authorization objects
- `GOVERNANCE` — General governance objects

**Schema Configuration:**
This schema will be created with **Managed Access** enabled, which means:
- Only the schema owner (typically SECURITYADMIN or ACCOUNTADMIN) can grant privileges on objects
- Prevents "shadow" security configurations where object creators grant their own access
- Provides centralized control over who can access security policy objects

**Best Practice:** Use a simple, single-word name that represents the functional purpose.

**More Information:**
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies)

#### Configure break-glass emergency access account(s) for this Snowflake account. (`account_breakglass_accounts`: object-list)
**What is this asking?**
Define one or more break-glass emergency access accounts for this Snowflake account.

**Why does this matter?**
Break-glass accounts are your last resort when:
- SSO/IdP is down and normal login is impossible
- All regular administrators are locked out
- Emergency security response requires immediate access
- Critical business operations cannot wait for normal access restoration

Without break-glass access, an IdP outage or misconfiguration could leave you locked out of the account entirely.

**Recommendations:**
- Create at least one break-glass account
- Use a clearly identifiable name (e.g., `breakglass_admin`, `emergency_admin`)
- Restrict to known, trusted IP addresses

**Username recommendations:**
- `breakglass_admin`
- `emergency_access`
- `{{ new_account_name | lower }}_breakglass`

**Important:** Do NOT use email addresses as break-glass usernames. Break-glass accounts must work when SSO/IdP is unavailable, so they should use simple local identifiers without special characters like `@` or `.` in the username.

**Email considerations:**
- Use a monitored shared mailbox
- Avoid personal emails that may become inactive
- Example: `snowflake-emergency@yourcompany.com`

**Allowed IPs:**
- Enter IP addresses that should be able to use this break-glass account
- These should be trusted locations (e.g., secure admin workstations, VPN endpoints)
- Use CIDR notation for ranges: `10.0.0.0/8` or single IPs: `203.0.113.1`

**Example entry:**
- Username: `breakglass_admin`
- Email: `snowflake-emergency@company.com`
- Allowed IPs: `10.0.0.0/8, 192.168.1.0/24`

**More Information:**
* [MFA Best Practices](https://docs.snowflake.com/en/user-guide/security-mfa) — Emergency access recommendations
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Exempting users from policies
