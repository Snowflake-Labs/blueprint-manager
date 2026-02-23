In this step, you'll create the initial Account Administrators who will manage your Snowflake environment. Since you've chosen to manage users manually (without SCIM), these users will be created directly in Snowflake.

**Account Context:** These administrators are being configured for your Organization Account (if created) or your primary account. If you have a multi-account strategy, additional accounts will need their own administrators configured separately.

## Why is this important?

Account Administrators (ACCOUNTADMIN role) have the highest level of privileges in a Snowflake account. They can:
- Create and manage all objects
- Grant privileges to any role
- Manage account-level settings
- Access all data

Properly configuring your initial administrators ensures:
- **Redundancy**: Multiple admins prevent lockout scenarios
- **Accountability**: Named individuals are responsible for administrative actions
- **Security**: Limiting the number of admins reduces risk

## External Prerequisites

- Email addresses of designated administrators
- Administrators should have corporate email addresses (not personal emails)

## Key Concepts

**ACCOUNTADMIN Role**
The most privileged system-defined role in Snowflake. Should be limited to 2-3 trusted individuals.

**SECURITYADMIN Role**
Can manage grants on all objects in the account. Use this for day-to-day security management instead of ACCOUNTADMIN.

**SYSADMIN Role**
Can create databases, warehouses, and other objects. Use this for day-to-day infrastructure management.

**USERADMIN Role**
Can create and manage users and roles. Often delegated for operational user management.

**User Types**
- `PERSON`: Human users who log in interactively
- `SERVICE`: Automated processes and integrations
- `LEGACY_SERVICE`: Backward-compatible service accounts

## More Information

* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user) — SQL command reference for user creation
* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles) — Overview of built-in administrative roles
* [Access Control Privileges](https://docs.snowflake.com/en/user-guide/security-access-control-privileges) — Detailed privilege reference

### Configuration Questions

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
