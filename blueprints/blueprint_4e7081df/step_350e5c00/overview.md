In this step, you'll configure SAML-based Single Sign-On (SSO) for this account. This enables users to authenticate using your Identity Provider credentials rather than separate Snowflake passwords.

**Account Context:** This step should be executed from the newly created account.

## Why is this important?

SAML/SSO provides:
- **Seamless authentication**: Users log in with their corporate credentials
- **Centralized control**: Authentication policies managed in your IdP
- **Reduced password fatigue**: No additional password to remember
- **Improved security**: Leverage IdP's MFA and conditional access policies

Think of SAML as a "digital passport"—your IdP vouches for your identity, and Snowflake trusts that assertion.

## External Prerequisites

- Identity Provider configured with Snowflake application
- IdP metadata (certificate, SSO URL, issuer)
- Ability to configure application settings in your IdP

## Key Concepts

**SAML Security Integration**
A Snowflake object that configures SAML authentication. Each account needs its own integration—these cannot be shared.

**IdP Metadata**
Information from your Identity Provider needed to configure SAML:
- **SSO URL**: Where Snowflake redirects users for authentication
- **Certificate**: Public key to verify IdP signatures
- **Issuer/Entity ID**: Unique identifier for your IdP

**Assertion Consumer Service (ACS) URL**
The Snowflake URL where your IdP sends authentication responses. This is account-specific.

**More Information:**
* [SAML SSO Configuration](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth) — Complete SAML setup guide
* [Okta SAML Setup](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-okta) — Okta-specific configuration
* [Azure AD SAML Setup](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-azure) — Azure-specific configuration

### Configuration Questions

#### What name should be used for the SAML integration in this account? (`account_saml_integration_name`: text)
**What is this asking?**
Provide a name for the SAML security integration object.

**Why does this matter?**
The integration name identifies the SAML connection in Snowflake. A descriptive name helps with troubleshooting SSO issues and managing multiple integrations if needed.

**Recommendations:**
- Use a descriptive name that identifies the IdP
- Use uppercase with underscores
- Keep consistent with your organization's naming

**Examples:**
- `OKTA_SAML_INTEGRATION`
- `AAD_SAML_INTEGRATION`
- `CORPORATE_SSO`

**More Information:**
* [SAML Security Integration](https://docs.snowflake.com/en/sql-reference/sql/create-security-integration-saml2) — CREATE SECURITY INTEGRATION reference

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

#### What is your Identity Provider's Issuer (Entity ID)? (`account_saml_issuer`: text)
**What is this asking?**
The unique identifier for your Identity Provider in SAML assertions.

**Why does this matter?**
The issuer must exactly match what your IdP sends in SAML assertions. A mismatch causes authentication failures.

**How to find this:**
- **Okta**: Application > Sign On tab > Identity Provider Issuer
- **Azure AD**: Enterprise App > Single sign-on > Azure AD Identifier
- **Other IdPs**: Look for "Issuer", "Entity ID", or "IdP Identifier"

**Example formats:**
- Okta: `http://www.okta.com/abcdefghijklmnop`
- Azure: `https://sts.windows.net/tenant-id/`

#### What is your Identity Provider's SSO URL? (`account_saml_sso_url`: text)
**What is this asking?**
The URL where Snowflake redirects users for SAML authentication.

**Why does this matter?**
This URL is where users are sent to log in. An incorrect URL will break SSO completely, preventing users from authenticating via your IdP.

**How to find this:**
- **Okta**: Application > Sign On tab > Identity Provider Single Sign-On URL
- **Azure AD**: Enterprise App > Single sign-on > Login URL
- **Other IdPs**: Look for "SSO URL", "Login URL", or "SAML Endpoint"

**Example format:**
- Okta: `https://yourcompany.okta.com/app/snowflake/abcd1234/sso/saml`
- Azure: `https://login.microsoftonline.com/tenant-id/saml2`

#### What is your Identity Provider's X.509 certificate? (`account_saml_certificate`: text)
**What is this asking?**
The public certificate used to verify SAML assertions from your IdP.

**Why does this matter?**
Snowflake uses this certificate to verify that SAML assertions genuinely come from your IdP. Without a valid certificate, SSO authentication will fail with signature validation errors.

**How to find this:**
- **Okta**: Application > Sign On tab > Download certificate
- **Azure AD**: Enterprise App > SAML Signing Certificate > Download (Base64)
- **Other IdPs**: Look for "Download Certificate" or "X.509 Certificate"

**Format:**
Paste the entire certificate including the BEGIN and END lines:
```
-----BEGIN CERTIFICATE-----
MIIC8DCCAdigAwIBAgIQH...
-----END CERTIFICATE-----
```

**Tip:** If the certificate is downloaded as a file, open it in a text editor and copy the contents.

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
