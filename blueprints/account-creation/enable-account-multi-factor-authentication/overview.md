In this step, you'll verify MFA configuration and guide administrator users through enabling multi-factor authentication. This ensures privileged accounts have an additional layer of security beyond passwords.

**Account Context:** This step should be executed from the newly created account.

## **Why is this important?**

MFA significantly reduces the risk of account compromise:
- Even if a password is stolen, the attacker needs the second factor
- Protects against phishing, credential stuffing, and password breaches
- Required for compliance with many security frameworks (SOC2, HIPAA, PCI)

For administrator accounts, MFA is especially critical given their elevated privileges.

## **Prerequisites**

- Administrator users created or provisioned
- Users have access to an authenticator app (Duo, Google Authenticator, Microsoft Authenticator)
- MFA support contact identified for user assistance

## **Key Concepts**

**TOTP (Time-based One-Time Password)**
The most common MFA method. Users install an authenticator app and scan a QR code to set up. The app generates a new 6-digit code every 30 seconds.

**MFA Enrollment**
Users must enroll in MFA before it's enforced. During enrollment, they scan a QR code with their authenticator app.

**Authentication Policy and MFA**
If your authentication policy includes password authentication, users should be required to enroll in MFA. MFA enforcement is configured via user settings or organizational policy.

**MFA for SSO Users**
If users authenticate via SAML SSO, MFA is typically handled by your Identity Provider, not Snowflake. Ensure your IdP enforces MFA.

**More Information:**
* [Multi-factor Authentication (MFA)](https://docs.snowflake.com/en/user-guide/security-mfa) — MFA overview
* [MFA Best Practices](https://docs.snowflake.com/en/user-guide/security-mfa-migration-best-practices) — Implementation guidance

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

#### Who should users contact for MFA assistance? (`account_mfa_support_contact`: text)
**What is this asking?**
Provide a contact (email, Slack channel, or help desk) where users can get help with MFA issues.

**Why does this matter?**
MFA issues (lost device, locked out, enrollment problems) need quick resolution. Having a clear support path prevents users from being stuck.

**Examples:**
- `it-helpdesk@company.com`
- `#snowflake-support` (Slack)
- `https://helpdesk.company.com/snowflake`

**Recommendation:**
Use your organization's standard IT support channel. If you have a dedicated Snowflake support team, use their contact.
