In this step, you'll choose whether to use the same security configuration established in the Platform Foundation workflow, or to create custom security settings for this account.

**Account Context:** This step should be executed from the newly created account.

## Why is this important?

Consistency in security configuration simplifies administration and ensures compliance across your organization. However, some accounts may have unique requirements that necessitate different settings.

This choice affects:
- SCIM integration settings
- Network policy IP ranges
- Authentication policy requirements
- SAML/SSO configuration

## External Prerequisites

- Platform Foundation workflow completed
- Understanding of this account's security requirements
- Knowledge of any regulatory or compliance needs specific to this account

## Key Concepts

**Organization Configuration**
Using the same security settings established during Platform Foundation setup. This includes the same IdP, network rules, and authentication policies. While the objects must be created in each account (they can't be shared), the values and configuration are consistent.

**Custom Configuration**
Creating account-specific security settings that may differ from the organization standard. This provides flexibility for accounts with unique requirements (e.g., different network restrictions, stricter authentication policies, or integration with a different IdP).

**What Gets Reused vs. Recreated**
Even when using organization configuration:
- **Recreated in this account**: SCIM integration, network rules/policies, authentication policies (these are account-level objects)
- **Values reused**: IP ranges, IdP settings, policy configurations

**More Information:**
* [Security Overview](https://docs.snowflake.com/en/user-guide/admin-security) — Snowflake security features

### Configuration Questions

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

#### Will you configure SAML/SSO for this account? (`account_configure_saml`: multi-select)
**What is this asking?**
Decide whether to set up SAML-based Single Sign-On for this account.

**Why does this matter?**
SAML/SSO provides:
- Seamless user experience (no separate Snowflake passwords)
- Centralized authentication control via your IdP
- Automatic session termination when users are disabled in IdP
- Consistent access policies across your enterprise applications

**Platform Foundation Setting:** {{ configure_saml }}

**Options explained:**

**Yes - Configure SAML:**
- Users can log in using your IdP credentials
- Provides seamless SSO experience
- Requires IdP configuration for this specific account
- Recommended if you configured SAML in Platform Foundation

**No - Use password authentication:**
- Users authenticate with Snowflake username/password + MFA
- Simpler initial setup
- Can configure SAML later

**When to choose differently from org:**
- This account is for external partners who don't use your IdP
- This is a sandbox/development account where SSO isn't needed
- You want to get the account operational quickly and add SSO later

**More Information:**
* [SAML/SSO Overview](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth) — Federated authentication options
**Options:**
- Yes - Configure SAML for this account
- No - Use password authentication

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

#### Will you configure SAML/SSO for single sign-on? (`configure_saml`: multi-select)
**What is this asking?**
Decide whether to configure SAML-based Single Sign-On (SSO) as part of this setup, or defer it for later.

**Why does this matter?**
SAML/SSO allows users to authenticate to Snowflake using your Identity Provider, providing a seamless login experience and centralized authentication control.

**Options explained:**

**Yes - Configure SAML now:**
- A dedicated step will guide you through SAML configuration
- Recommended if your IdP is ready and you want SSO from day one

**No - Configure later:**
- Skip SAML configuration for now
- Users will authenticate with username/password + MFA
- You can configure SAML later without rebuilding

**When to choose "Configure later":**
- Your IdP isn't fully set up yet
- You want to get the basics working first
- You need to coordinate with your identity team
- You're doing a proof-of-concept

**Note:** Even without SAML, password + MFA provides strong authentication. SAML adds convenience and centralized control, not necessarily more security.

**Recommendation:**
If you selected a SCIM provider and your IdP is ready, configure SAML now for a complete SSO experience. Otherwise, defer and configure later.

**More Information:**
* [SAML/SSO Configuration](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth) — Federated authentication setup
**Options:**
- Yes - Configure SAML now
- No - Configure later or use password authentication
