In this step, you'll create break-glass emergency access account(s) that can bypass SSO/SAML authentication. These accounts are critical for maintaining access to Snowflake when your Identity Provider is unavailable.

**Account Context:** Break-glass account(s) are being created in your Organization Account (if created) or your primary account.

## **Why is this important?**

When you rely on SAML/SSO for authentication, you create a dependency on your Identity Provider. If your IdP experiences an outage, misconfiguration, or certificate expiration, you could be locked out of Snowflake entirely.

Break-glass accounts provide:

* **Emergency Access**: Bypass SSO when the IdP is down  
* **Recovery Capability**: Fix SSO misconfigurations  
* **Business Continuity**: Maintain operations during identity outages  
* **Compliance**: Meet regulatory requirements for emergency access procedures

## **External Prerequisites**

* A secure location to store emergency credentials (password vault, physical safe)  
* A process for generating and rotating one-time passwords (OTPs)  
* Documentation of break-glass procedures

## **Key Concepts**

**Break-Glass Account** A special-purpose account that bypasses normal authentication. Think of this as the "emergency key behind glass"—you break the glass only when the normal door won't open (IdP outage).

**One-Time Password (OTP)** A password that is used once and then changed. This is like a "single-use emergency key"—even if someone sees you use it, they can't reuse it.

**Authentication Policy** A Snowflake object that defines how users must authenticate. Break-glass accounts use a separate policy that allows password-only authentication—a different "entrance" with different rules.

**Client Types** Snowflake can restrict which clients (UI, drivers, etc.) can use certain authentication methods. Break-glass accounts should be limited to the web UI to reduce attack surface.

**Best Practice: Store Securely, Use Rarely** Break-glass credentials should be stored in a secure vault (physical or digital) and used only during genuine emergencies. Regular use defeats their purpose.

## **More Information**

* [MFA and Break-Glass Access](https://docs.snowflake.com/en/user-guide/security-mfa) — Setting up break-glass accounts and one-time passcodes  
* [MFA Migration Best Practices](https://docs.snowflake.com/en/user-guide/security-mfa-migration-best-practices) — Break-glass procedures during MFA/SSO rollout  
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Defining authentication methods per user  
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) — Restricting access by IP address

### Configuration Questions

#### Configure the break-glass emergency access account(s) (`breakglass_accounts`: object-list)
**What is this asking?**
Define one or more break-glass emergency access accounts. Each account can bypass SSO and authenticate with a password when your Identity Provider is unavailable.

**How Many Accounts?**
- **Minimum 1**: At least one break-glass account is required
- **Recommended 2**: Two accounts provide redundancy if one is compromised
- **Maximum 3**: More than 3 increases the attack surface

**Username**
- Use a descriptive name: `BREAKGLASS_ADMIN`, `EMERGENCY_ACCESS`, `SOS_ADMIN`
- Avoid personal names since this is a shared emergency account
- For multiple accounts, use suffixes: `BREAKGLASS_ADMIN_01`, `BREAKGLASS_ADMIN_02`
- **Important:** Do NOT use email addresses as usernames. Break-glass accounts must work when SSO is unavailable, so use simple identifiers without `@` or `.` characters.

**Email**
- Use a team distribution list, not a personal email
- Examples: `snowflake-security@company.com`, `platform-team@company.com`
- Ensure the email is monitored 24/7 if you have critical workloads

**Allowed IPs**
- Enter comma-separated IP addresses or CIDR ranges
- Example: `10.0.0.1, 192.168.1.0/24, 172.16.0.0/16`
- Include VPN egress IPs, office IPs, and backup locations
- Enter `NONE` to allow access from any IP (not recommended)

**Example Entries:**

| username | email | allowed_ips |
|----------|-------|-------------|
| `BREAKGLASS_ADMIN_01` | `platform-team@company.com` | `10.0.0.1, 192.168.1.0/24` |
| `BREAKGLASS_ADMIN_02` | `security-team@company.com` | `10.0.0.2, 192.168.1.0/24` |

**Security Notes:**
- All accounts are created with `MUST_CHANGE_PASSWORD = TRUE`
- Initial password must be changed on first login
- Use one-time passwords (OTPs) stored in a secure vault
- Restrict to Web UI only (no driver/CLI access)

**More Information:**
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user)
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies)

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
