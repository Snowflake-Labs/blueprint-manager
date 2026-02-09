In this step, you'll choose how users will be managed and authenticated in Snowflake. This foundational decision determines the subsequent configuration steps.

**Account Context:** This step configures identity management for your Organization Account (if created) or your primary account.

## Why is this important?

Your identity management approach affects security, administrative overhead, and user experience across your entire Snowflake platform. The choices you make here determine:
- How users are created and removed
- How users authenticate (SSO vs password)
- How much manual administration is required

## External Prerequisites

- Understand your organization's identity management strategy
- Know which Identity Provider (IdP) your organization uses (if any)
- Determine if SAML/SSO will be part of your authentication strategy

## Key Concepts

**SCIM (System for Cross-domain Identity Management)**
An open standard protocol that enables automated user provisioning. Think of SCIM as a "sync cable" between your Identity Provider and Snowflake—when users are added, changed, or removed in your IdP, those changes automatically flow to Snowflake.

**Identity Provider (IdP)**
The authoritative source for user identities in your organization (e.g., Okta, Azure AD, Ping Identity). Your IdP is the "single source of truth" for who works at your organization.

**SAML/SSO (Single Sign-On)**
Allows users to authenticate to Snowflake using your Identity Provider credentials, providing a seamless login experience without separate Snowflake passwords.

**Manual User Management**
Creating and managing Snowflake users directly, without IdP integration. Users authenticate with Snowflake usernames and passwords (plus MFA).

**More Information:**
* [SCIM Overview](https://docs.snowflake.com/en/user-guide/scim) — Introduction to SCIM provisioning in Snowflake
* [SAML/SSO Overview](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth) — Federated authentication options

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
