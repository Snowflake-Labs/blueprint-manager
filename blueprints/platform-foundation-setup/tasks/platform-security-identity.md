# Platform Security & Identity

## Summary
Configure user provisioning via SCIM or manual management, provision platform
administrators, configure single sign-on, create emergency access, implement
network security, define authentication policies, and enable multi-factor authentication.

## External Requirements
- Task 1 (Platform Foundation) completed
- Identity Provider Access (Okta, Azure AD, etc.)
- Network Information (corporate IP ranges, VPN endpoints, cloud service IPs)
- Administrator Details (names and email addresses)

## Personas
- Security Administrator
- Identity Team
- Platform Administrator

## Role Requirements
- ACCOUNTADMIN privileges
- Logged into Organization Account (if created) or primary account

## Details
## Steps in This Task

| Step | Title | Purpose |
|------|-------|---------|
| 2.1 | Configure SCIM Integration | Set up automated user provisioning from your IdP (or choose manual management) |
| 2.2 | Provision/Create Account Administrators | Assign ACCOUNTADMIN and other admin roles (method varies based on 2.1) |
| 2.3 | Configure SAML/SSO | Enable federated authentication (optional) |
| 2.4 | Create Break-Glass Access | Establish emergency access account |
| 2.5 | Configure Network Policies | Set up IP allowlisting and network rules |
| 2.6 | Configure Authentication Policies | Define auth requirements by user type |
| 2.7 | Enable Multi-Factor Authentication | Guide MFA enrollment for users |

**Note on administrator provisioning:** Based on your choice in Configure SCIM Integration:
- **If using SCIM:** You'll provision administrators by granting roles to SCIM-provisioned users
- **If using manual management:** You'll create administrator users directly in Snowflake

**Note on SAML/SSO:** SAML/SSO configuration is optional. In Configure SCIM Integration, you'll choose whether to configure SAML now or later. If you skip SAML, users will authenticate with password + MFA.

**⚠️ All Task 2 steps configure the account you are currently logged into.**

## Time Estimate

This task typically takes **45-60 minutes** to complete. Additional time may be required for:

- IdP configuration (performed outside Snowflake)
- Coordination with your identity/security team
- Network policy testing and validation

## Key Decisions

Several questions in this task have security implications:

1. **SCIM Provisioner Role**: Determines what the IdP can manage in Snowflake
2. **Administrator Assignments**: ACCOUNTADMIN grants full account control - limit to 2-3 trusted individuals
3. **Break-Glass Credentials**: Must be securely stored and access documented
4. **Network Policies**: Overly restrictive policies can lock out legitimate users
5. **Authentication Policies**: Balance security with usability

Involve your security team when making these decisions.

## Deliverables

Upon completion, you will have:

- User provisioning configured (SCIM integration or manual management approach documented)
- Initial administrators provisioned with appropriate roles
- SAML/SSO configured for federated authentication (if using an IdP)
- Break-glass emergency access account created and documented
- Network policies configured for IP allowlisting
- Authentication policies defined for different user types
- MFA enrollment guidance distributed to administrators

## Security Best Practices

This task implements several security best practices:

| Practice | Implementation |
|----------|----------------|
| **Least Privilege** | Separate admin roles (ACCOUNTADMIN, SECURITYADMIN, SYSADMIN, USERADMIN) |
| **Centralized Identity** | SCIM + SAML for single source of truth (or documented manual process) |
| **Emergency Access** | Break-glass account with restricted network policy |
| **Defense in Depth** | Layered authentication + network + MFA policies |
| **Audit Trail** | All authentication attempts logged |

## More Information

- [SCIM Provisioning](https://docs.snowflake.com/en/user-guide/scim)
- [SAML/SSO Configuration](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth)
- [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies)
- [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies)
- [Multi-Factor Authentication](https://docs.snowflake.com/en/user-guide/ui-mfa)