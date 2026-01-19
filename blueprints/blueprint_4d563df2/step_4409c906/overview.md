In this step, you'll define the initial Account Administrators who will manage your Snowflake environment. These users will be provisioned through SCIM from your Identity Provider, and you'll grant them the appropriate administrative roles.

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

- SCIM integration configured in the previous step
- Users assigned to Snowflake application in your Identity Provider
- Users provisioned to Snowflake via SCIM

## Key Concepts

**ACCOUNTADMIN Role**
The most privileged system-defined role in Snowflake. Should be limited to 2-3 trusted individuals.

**SECURITYADMIN Role**
Can manage grants on all objects in the account. Use this for day-to-day security management instead of ACCOUNTADMIN.

**SYSADMIN Role**
Can create databases, warehouses, and other objects. Use this for day-to-day infrastructure management.

**USERADMIN Role**
Can create and manage users and roles. Often delegated for operational user management.

## More Information

* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles) — Overview of built-in administrative roles
* [Access Control Privileges](https://docs.snowflake.com/en/user-guide/security-access-control-privileges) — Detailed privilege reference

### Configuration Questions

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
