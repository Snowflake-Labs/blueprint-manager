In this step, you'll configure authentication policies that define how different types of users must authenticate to this Snowflake account. The values from Platform Foundation are pre-populated as defaults—review them and adjust if this account requires different authentication settings.

**Account Context:** This step should be executed from the newly created account.

## **Why is this important?**

Authentication policies ensure appropriate security for different user types:
- **Human users**: May require SSO and/or MFA for interactive logins
- **Service accounts**: May use key-pair authentication for programmatic access
- **Break-glass accounts**: Need password-only for emergency scenarios

Think of authentication policies as "entry requirements at different doors"—different users enter through different doors with different requirements.

## **Prerequisites**

- SAML/SSO configured (if using SSO)
- Understanding of whether this account needs different authentication requirements than the Organization Account
- Knowledge of service account authentication requirements for this account

## **Key Concepts**

**Answer Inheritance**
This step uses the same answer titles as Platform Foundation. Your Platform Foundation values are pre-populated as defaults. You can accept them for consistency across accounts, or override them if this specific account has different requirements. Any changes apply only to this account instance.

**Authentication Policy**
A Snowflake object that defines allowed authentication methods and requirements. Policies can be applied at account level or to specific users.

**Authentication Methods**
- **PASSWORD**: Username and password
- **SAML**: Single Sign-On via Identity Provider
- **OAUTH**: OAuth-based authentication
- **KEYPAIR**: RSA key-pair for programmatic access
- **PAT**: Personal Access Tokens (PROGRAMMATIC_ACCESS_TOKEN)

**MFA Requirements**
Multi-Factor Authentication can be required as part of an authentication policy, adding a second factor beyond password or SSO.

**Policy Hierarchy**
- Account-level policy applies to all users by default
- User-level policy overrides account-level for specific users

**More Information:**
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Complete policy guide
* [CREATE AUTHENTICATION POLICY](https://docs.snowflake.com/en/sql-reference/sql/create-authentication-policy) — SQL reference
* [MFA in Snowflake](https://docs.snowflake.com/en/user-guide/security-mfa) — Multi-factor authentication setup

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
