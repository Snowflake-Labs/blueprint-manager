In this step, you'll configure SCIM (System for Cross-domain Identity Management) integration to enable automated user provisioning from your Identity Provider to this Snowflake account.

**Account Context:** This step should be executed from the newly created account.

## Why is this important?

SCIM integration automates the user lifecycle:
- **Onboarding**: Users are automatically created when added to your IdP
- **Offboarding**: Users are automatically disabled when removed from your IdP
- **Attribute sync**: User attributes (name, email) stay synchronized

Without SCIM, you must manually create and remove users in each Snowflake account.

## External Prerequisites

- Identity Provider configured (Okta, Azure AD, or other SCIM 2.0 compatible)
- Network access from IdP to Snowflake (for SCIM API calls)
- Ability to configure a new SCIM application/integration in your IdP

## Key Concepts

**SCIM Security Integration**
A Snowflake object that enables SCIM provisioning. Each account needs its own integration—these cannot be shared between accounts.

**SCIM Provisioner Role**
A custom role that owns the SCIM integration and has privileges to create/manage users. The IdP uses this role when provisioning users.

**SCIM Network Policy**
(Optional but recommended) A network policy that restricts SCIM API access to your IdP's IP addresses, preventing unauthorized provisioning requests.

**SCIM Token**
A secret token generated when creating the SCIM integration. This token is provided to your IdP to authenticate SCIM API requests.

**More Information:**
* [SCIM Overview](https://docs.snowflake.com/en/user-guide/scim) — Introduction to SCIM provisioning
* [Okta SCIM Configuration](https://docs.snowflake.com/en/user-guide/scim-okta) — Okta-specific setup
* [Azure AD SCIM Configuration](https://docs.snowflake.com/en/user-guide/scim-azure) — Azure-specific setup

### Configuration Questions

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

#### What name should be used for the SCIM integration in this account? (`account_scim_integration_name`: text)
**What is this asking?**
Provide a name for the SCIM security integration object in this account.

**Why does this matter?**
The integration name identifies the SCIM connection in Snowflake. A consistent naming convention makes it easier to manage integrations across multiple accounts and troubleshoot provisioning issues.

**If using Organization Configuration:**
Consider using the same integration name as your Organization Account for consistency.

**Recommendations:**
- Use a descriptive name that identifies the IdP
- Use uppercase with underscores
- Include the account identifier if you want unique names per account

**Examples:**
- `OKTA_SCIM_INTEGRATION`
- `AAD_SCIM_INTEGRATION`
- `<ACCOUNT_NAME>_SCIM` (e.g., `SALES_PROD_SCIM`)

**More Information:**
* [SCIM Integration](https://docs.snowflake.com/en/user-guide/scim) — SCIM provisioning overview

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

#### What IP addresses should be allowed for SCIM provisioning? (`account_scim_allowed_ips`: list)
**What is this asking?**
Enter the IP addresses from which your Identity Provider will make SCIM API calls to Snowflake. This creates a network policy that restricts SCIM access.

**If using Organization Configuration:**
Use the same IdP IP addresses as your Organization Account for consistency.

**Why does this matter?**
Restricting SCIM access to known IdP IPs prevents unauthorized provisioning attempts.

**How to find your IdP's IP ranges:**
- **Okta**: [Okta IP Addresses](https://help.okta.com/en-us/Content/Topics/Security/IP-Ranges.htm)
- **Azure AD**: [Azure AD IP Ranges](https://docs.microsoft.com/en-us/azure/active-directory/enterprise-users/directory-service-limits-restrictions)

**Format:**
Enter each IP address or CIDR block on a separate line:
```
203.0.113.0/24
198.51.100.1
```

**Important:** If you don't know your IdP's IP ranges, you can skip the network policy and add it later. However, this is a security best practice.

**More Information:**
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) — IP-based access control

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
