In this step, you'll configure authentication policies to define how different types of users must authenticate to Snowflake.

**Account Context:** These authentication policies apply to your Organization Account (if created) or your primary account.

## **Why is this important?**

Authentication policies control which authentication methods are allowed for users. Different user types have different security requirements:

* **Human users**: Should authenticate via SSO with MFA for security  
* **Service accounts**: Should use OAuth, key pairs, or tokens (not passwords)  
* **Break-glass accounts**: Need password access as a fallback

Without proper authentication policies:

* Service accounts might use insecure password authentication  
* Human users might bypass MFA requirements  
* Break-glass accounts might be used for routine operations

## **External Prerequisites**

* SAML/SSO integration configured  
* Break-glass account created  
* Understanding of your organization's authentication requirements

## **Key Concepts**

**Authentication Policy** A Snowflake object that specifies allowed authentication methods, MFA requirements, and client type restrictions. Think of authentication policies as "entry requirements" at different doors—you can have strict requirements at the front door (human users) and different requirements at the service entrance (service accounts).

**Authentication Methods** How a user proves their identity:

* PASSWORD: Username and password  
* SAML: SSO via SAML assertion  
* OAUTH: OAuth 2.0 tokens  
* KEYPAIR: RSA key pair authentication  
* PAT: Personal Access Tokens

**MFA Authentication Methods** Multi-factor authentication options:

* TOTP: Time-based One-Time Password (authenticator apps)  
* PASSKEY: FIDO2/WebAuthn passkeys

**Client Types** Which clients can use the authentication:

* SNOWFLAKE\_UI: Web interface  
* SNOWSIGHT: Snowsight web app  
* DRIVERS: JDBC, ODBC, Python, etc.  
* SNOWSQL: SnowSQL CLI

**Best Practice: Layered Security** Different user types need different policies—like having VIP entrances, employee entrances, and delivery entrances at a building, each with appropriate security checks.

**More Information:**

* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Overview of authentication policy options  
* [CREATE AUTHENTICATION POLICY](https://docs.snowflake.com/en/sql-reference/sql/create-authentication-policy) — SQL command reference  
* [MFA in Snowflake](https://docs.snowflake.com/en/user-guide/security-mfa) — Multi-factor authentication setup

### Configuration Questions

#### What authentication methods should be allowed for human users in this account? (`human_auth_methods`: multi-select)
**What is this asking?**
Choose how human users (interactive users) should authenticate to this account. The value from Platform Foundation is pre-populated—accept it for consistency or change it if this account has different requirements.

**Why does this matter?**
Authentication policies are the gateway to your data. The right balance between security and usability ensures:
- Protection against unauthorized access
- Compliance with security requirements
- Good user experience for legitimate users
- Alignment with your organization's security posture

**Inherited Value:**
This answer is pre-populated from your Platform Foundation configuration. Most organizations keep authentication consistent across accounts, but you may want different settings for:
- Development accounts (less strict for agility)
- Production accounts (stricter requirements)
- External-facing accounts (stricter or different IdP)

**Options explained:**

**SAML Only (SSO required):** *(Only visible if SAML is configured)*
- Users must authenticate via your Identity Provider
- Provides strongest centralized control
- Recommended for production accounts
- **Note:** Requires break-glass accounts for emergency access

**SAML or Password with MFA:** *(Only visible if SAML is configured)*
- Users can use SSO or password + MFA
- Provides flexibility while maintaining security
- Good for accounts where SSO might not always be available

**Password with MFA Only:**
- Users authenticate with Snowflake password plus MFA
- Strong security without SSO dependency
- Use if this account doesn't integrate with your IdP

**Recommendation:**
Accept the Platform Foundation value unless this account has specific requirements that differ from your standard.

**More Information:**
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Policy configuration guide
**Options:**
- SAML Only (SSO required)
- SAML or Password with MFA
- Password with MFA Only

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

#### What MFA method should be required for password authentication? (`mfa_method`: multi-select)
**What is this asking?**
Select the multi-factor authentication method(s) to require when users authenticate with passwords.

**Why does this matter?**
MFA significantly reduces the risk of account compromise from password theft.

**Options explained:**
- **TOTP (Authenticator Apps)**: Time-based codes from apps like Google Authenticator, Microsoft Authenticator, Duo. Widely supported.
- **Passkey (FIDO2/WebAuthn)**: Hardware keys or biometric authentication. Most secure but requires compatible devices.
- **Either TOTP or Passkey**: Users can choose. Recommended for flexibility.

**Recommendation:**
**Either TOTP or Passkey** provides the best balance of security and user flexibility.

**More Information:**
* [MFA in Snowflake](https://docs.snowflake.com/en/user-guide/security-mfa)
**Options:**
- TOTP (Authenticator Apps)
- Passkey (FIDO2/WebAuthn)
- Either TOTP or Passkey

#### What authentication methods should be allowed for service accounts? (`service_auth_methods`: multi-select)
**What is this asking?**
Define how service accounts (automated processes, applications) should authenticate.

**Why does this matter?**
Service accounts should not use password authentication, which is less secure and harder to rotate.

**Options explained:**
- **OAuth Only**: Services must use OAuth tokens. Best for cloud applications with OAuth support.
- **Key Pair Only**: Services must use RSA key pairs. Best for on-premise or custom applications.
- **OAuth or Key Pair**: Either method allowed. Recommended for flexibility.
- **OAuth, Key Pair, or PAT**: Adds Personal Access Tokens. PATs are easier to manage but less secure.

**Recommendation:**
**OAuth or Key Pair** provides security while accommodating different integration patterns.

**More Information:**
* [Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth)
* [OAuth](https://docs.snowflake.com/en/user-guide/oauth)
**Options:**
- OAuth Only
- Key Pair Only
- OAuth or Key Pair
- OAuth, Key Pair, or PAT

#### Should authentication policies be applied at the account level? (`apply_auth_policies_account_level`: multi-select)
**What is this asking?**
Decide whether to enforce the human user authentication policy for all users by default.

**Why does this matter?**
- **Yes**: All users must comply with the policy unless they have a specific override (like break-glass)
- **No**: Policies only apply to users you explicitly assign them to

**Recommendation:**
- Start with **No** during initial rollout and testing
- Move to **Yes** once you've validated policies work correctly
- Ensure break-glass accounts have their own policy first

**More Information:**
* [Activating Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies#activating-an-authentication-policy)
**Options:**
- Yes - Apply default policy to all users
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
