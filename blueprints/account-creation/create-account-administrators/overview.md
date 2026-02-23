In this step, you'll establish the administrator users for this account. Depending on your identity management approach, you'll either assign admin roles to SCIM-provisioned users or create local users with admin privileges.

**Account Context:** This step should be executed from the newly created account.

## Why is this important?

Administrator users are critical for account governance:
- **ACCOUNTADMIN**: Full control over the account (use sparingly)
- **SECURITYADMIN**: Manages users, roles, and security policies
- **SYSADMIN**: Manages databases, warehouses, and other resources
- **USERADMIN**: Creates and manages users (often delegated to SCIM)

Having multiple administrators ensures continuity if one person is unavailable.

## External Prerequisites

- SCIM integration configured (if using SCIM)
- List of users who need administrator access to this account
- Understanding of which admin roles each user needs

## Key Concepts

**Dual Path Approach**
Depending on your identity management choice:
- **SCIM**: Users are created by your IdP; you assign admin roles to their Snowflake accounts
- **Manual**: You create local users directly with admin roles

**Principle of Least Privilege**
Grant the minimum necessary role:
- Most users need only SYSADMIN for resource management
- SECURITYADMIN for those managing access control
- ACCOUNTADMIN should be limited to 2-3 senior administrators

**Role Hierarchy**
ACCOUNTADMIN inherits from SECURITYADMIN and SYSADMIN. Users with ACCOUNTADMIN can perform all admin functions.

**More Information:**
* [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview) — Role hierarchy and privileges
* [System Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles) — Built-in role descriptions

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

#### Who should have administrator access to this account? (`account_admin_users`: object-list)
**What is this asking?**
Define the users who need administrator privileges in this account.

**Why does this matter?**
Administrator access is critical for account governance. Having the right people with the right level of access ensures:
- Proper security oversight
- Continuity if someone is unavailable
- Principle of least privilege is maintained
- Clear accountability for administrative actions

**SSO-Ready Recommendation: Use Email as Login Name**
We strongly recommend using the user's **email address** as the `login_name`, even if you are not currently using SSO. This provides several benefits:
- **SSO-Ready:** Most identity providers (Okta, Azure AD, etc.) use email as the default identifier. Using email now means seamless SSO integration later.
- **Uniqueness:** Email addresses are globally unique and prevent naming conflicts.
- **Consistency:** Users log in with the same identifier across all systems.
**Example:** Use `john.doe@company.com` instead of `JDOE` or `JOHNDOE`.

**If using SCIM (automated provisioning):**
Users are created automatically from your IdP. You only need to specify:
- **login_name**: The username as it appears in Snowflake (typically the email address—check `SHOW USERS;` after SCIM sync)
- **admin_role**: The administrative role to assign

Leave `email`, `first_name`, and `last_name` blank for SCIM users—these are managed by your IdP.

**If using Manual User Management:**
Users will be created directly in Snowflake. Provide:
- **login_name**: The username for Snowflake login (**recommended: use email address** for SSO-readiness)
- **admin_role**: The administrative role to assign
- **email**: Email address for notifications (can match login_name)
- **first_name**: User's first name
- **last_name**: User's last name

**Admin Role Options:**
| Role | Responsibility | Recommended For |
|------|---------------|-----------------|
| `ACCOUNTADMIN` | Full account control | 2-3 senior platform/security leads |
| `SECURITYADMIN` | User and role management | Security team members |
| `SYSADMIN` | Resource management | Platform engineers, DBAs |
| `USERADMIN` | User creation/modification | HR integrations (if not using SCIM) |

**⚠️ Important:** Enter role names exactly as shown (uppercase).

**Best Practices:**
- Limit ACCOUNTADMIN to 2-3 trusted individuals
- Each person should use their own account (no shared accounts)
- Ensure at least 2 people have ACCOUNTADMIN for redundancy

**More Information:**
* [System Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles) — Built-in role descriptions
* [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview) — Role hierarchy and privileges
