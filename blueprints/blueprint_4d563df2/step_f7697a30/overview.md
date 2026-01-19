In this step, you'll configure SAML (Security Assertion Markup Language) for Single Sign-On (SSO) to enable federated authentication from your Identity Provider to Snowflake.

**Account Context:** This step configures SSO for your Organization Account (if created) or your primary account.

## Why is this important?

SAML SSO provides centralized authentication through your Identity Provider, offering:
- **Single Sign-On**: Users authenticate once through their corporate IdP
- **Centralized Security**: Authentication policies are managed in one place
- **Improved User Experience**: No separate Snowflake passwords to manage
- **Enhanced Security**: Leverage existing MFA, conditional access, and security policies
- **Compliance**: Meet audit requirements with centralized authentication logs

## External Prerequisites

- An Identity Provider (IdP) that supports SAML 2.0
- Administrative access to your IdP to configure the SAML application
- ACCOUNTADMIN or SECURITYADMIN role in Snowflake
- Your IdP's SAML metadata (Certificate, SSO URL, Issuer)

## Key Concepts

**SAML (Security Assertion Markup Language)**
An open standard for exchanging authentication data between an Identity Provider and a Service Provider. Think of SAML as a "digital passport"—your IdP stamps the passport (creates the assertion), and Snowflake accepts it at the border (verifies and grants access).

**Identity Provider (IdP)**
The system that authenticates users and issues SAML assertions (e.g., Okta, Azure AD, Ping). The IdP is the "passport office" that verifies your identity.

**Service Provider (SP)**
The application that accepts SAML assertions (Snowflake). Snowflake is the "destination" that trusts passports issued by your IdP.

**SSO URL**
The URL where users are redirected to authenticate with the IdP. This is where users go to "get their passport stamped."

**X.509 Certificate**
The certificate used to verify SAML assertions from the IdP. This is how Snowflake knows the passport is genuine and not forged.

**More Information:**
* [Federated Authentication](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth) — Overview of SSO and federated auth in Snowflake
* [SAML Overview](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-overview) — Understanding SAML concepts and flow
* [Configuring Snowflake as SP](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-configure-snowflake) — Service provider setup guide

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

#### What name would you like to use for the SAML integration? (`saml_integration_name`: text)
**What is this asking?**
Provide a name for the SAML security integration that will be created in Snowflake.

**Why does this matter?**
The integration name is used to reference the SAML configuration and appears in the login URL for IdP-initiated SSO.

**Format:**
- Use uppercase letters and underscores
- Include the IdP name for clarity
- Examples: `OKTA_SSO`, `AZURE_AD_SAML`, `PING_SSO`

**Recommendation:**
Use a format like `<IDP>_SSO` or `<IDP>_SAML` where `<IDP>` is your Identity Provider name.

**More Information:**
* [CREATE SECURITY INTEGRATION (SAML2)](https://docs.snowflake.com/en/sql-reference/sql/create-security-integration-saml2)

#### What is your Identity Provider's Issuer/Entity ID? (`saml_issuer`: text)
**What is this asking?**
Provide the Issuer (also called Entity ID) from your Identity Provider. This uniquely identifies your IdP.

**Why does this matter?**
The Issuer is used to verify that SAML assertions are coming from the expected Identity Provider.

**How to find this:**
- **Okta**: Found in the SAML application settings under "Identity Provider Issuer"
- **Azure AD**: Found as "Azure AD Identifier" in the SAML configuration
- **Ping**: Found in the application connection settings as "Entity ID"

**Format:**
Typically a URL like: `http://www.okta.com/exk1234567890` or a URN.

**More Information:**
* [SAML Configuration](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-configure-snowflake)

#### What is your Identity Provider's SSO URL? (`saml_sso_url`: text)
**What is this asking?**
Provide the SSO URL from your Identity Provider. This is where Snowflake will redirect users for authentication.

**Why does this matter?**
This URL is required for SP-initiated SSO, where users start at Snowflake and are redirected to the IdP.

**How to find this:**
- **Okta**: Found in the SAML application settings under "Identity Provider Single Sign-On URL"
- **Azure AD**: Found in the Enterprise Application SAML configuration under "Login URL"
- **Ping**: Found in the application connection settings

**Format:**
A full URL, typically: `https://your-idp.com/app/snowflake/sso/saml`

**More Information:**
* [SAML Configuration](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-configure-snowflake)

#### What is your Identity Provider's X.509 signing certificate? (`saml_certificate`: text)
**What is this asking?**
Provide the X.509 certificate from your Identity Provider. This certificate is used to verify SAML assertions.

**Why does this matter?**
Snowflake uses this certificate to verify that SAML assertions actually came from your IdP and haven't been tampered with.

**How to find this:**
- Download the certificate from your IdP's SAML configuration
- Open the certificate file in a text editor
- Copy the entire contents including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`

**Format:**
The full certificate in PEM format, including the BEGIN and END markers.

**Security Note:**
The certificate is a public key and is safe to include in configuration. Do not confuse this with a private key.

**More Information:**
* [SAML Certificate Requirements](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-configure-snowflake#label-fed-auth-configure-cert)

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

#### What prefix (if any) should be added to all account names? (`account_name_prefix`: text)
An account name prefix is an optional string added to the beginning of every account name for consistency and organization identification.  

**When to use a prefix:**  
* If your organization name is system-generated (e.g., `XY12345`) and you want your company name visible in account names  
* If you want to enforce consistent naming across all accounts  
* If you have multiple organizations or business units sharing Snowflake and need differentiation  

**Example with prefix:**  
* Prefix: `acme`  
* Account names become: `acme_prod`, `acme_dev`, `acme_finance`  
* URL: `https://XY12345-acme_prod.snowflakecomputing.com`  

**Example without prefix:**  
* Account names: `prod`, `dev`, `finance`  
* URL: `https://ACME-prod.snowflakecomputing.com`  

**Recommendations:**  
* If you have a **custom organization name** (like `ACME`), a prefix is typically unnecessary since your identity is already in the URL  
* If you have a **system-generated name**, consider using an abbreviated company name as a prefix  
* Keep prefixes short (3-8 characters) with no underscores  

**Enter `NONE` if you do not want to use an account name prefix.**  

**More Information:**  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)

#### What do you want to name your organization account? (`org_account_name`: text)
**Recommended Name:** ORG  
  Since there can be only one Organization Account per organization, the name should clearly indicate this special purpose. We recommend simply naming it ORG.  
  
  **Example URLs with Organization Account name ORG:**  
  * With Custom Org Name: [https://ACME-ORG.snowflakecomputing.com](https://ACME-ORG.snowflakecomputing.com)  
    * Org Name \= ACME  
    * Org Account Name \= Org  
  * System-generated Org Name: [https://XY12345-ORG.snowflakecomputing.com](https://XY12345-ORG.snowflakecomputing.com)  
    * Org Name \= XY12345  
    * Org Account Name \= Org  
* **Requirements:**  
  * Snowflake Enterprise Edition or higher  
  * ORGADMIN role granted in the existing account  
* **More Information:**  
  * [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts)  
  * [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)

#### Should the Snowflake login page show a button to log in with SSO? (`saml_sso_login_page`: multi-select)
**What is this asking?**
Decide whether to add a "Log in using SSO" button to the Snowflake login page.

**Why does this matter?**
- **Yes**: Users see a button on the login page to authenticate via your IdP (recommended)
- **No**: Users must use IdP-initiated SSO or the direct SSO URL

**Recommendation:**
Select **Yes** to provide users with an easy SSO option on the login page.

**More Information:**
* [Login Page Options](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-configure-snowflake#label-fed-auth-configure-login-page)
**Options:**
- Yes
- No

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
