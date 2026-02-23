# Account Security & Identity

## Summary
Configure user provisioning (SCIM or manual), establish administrator access,
set up network rules and policies, configure authentication policies,
create break-glass emergency access, and enable multi-factor authentication.

## External Requirements
- Account created and accessible (Task 1 completed)
- Infrastructure share consumed
- Identity Provider selection (Okta, Azure, None)
- SAML/SSO configuration preference
- Network policy IP ranges

## Personas
- Security Administrator
- Platform Administrator
- Network Team

## Role Requirements
- ACCOUNTADMIN role access
- Logged into the new account

## Details
## Steps in This Task

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 2.1 | Select Security Configuration Approach | Choose to use org configuration or custom | Always shown |
| 2.2 | Configure SCIM Integration | Set up automated user provisioning | If SCIM provider selected |
| 2.3 | Create Account Administrators | Assign admin roles for this account | Always shown |
| 2.4 | Configure SAML/SSO | Enable federated authentication | If SAML selected |
| 2.5 | Create Break-Glass Emergency Access | Establish emergency access | Always shown |
| 2.6 | Apply Organization Network Configuration | Use shared network rules | If using org config |
| 2.6 | Configure Custom Network Rules | Create custom network rules | If using custom config |
| 2.7 | Configure Authentication Policies | Define auth requirements by user type | Always shown |
| 2.8 | Enable Multi-Factor Authentication | Guide MFA enrollment | Always shown |

**Note:** Only one of Step 2.6a or 2.6b will be displayed based on your security configuration approach.

**From Platform Foundation (inherited):**
- Identity Provider selection (Okta, Azure, None)
- SAML/SSO configuration preference
- Network policy IP ranges (can be reused)
- Authentication policy settings

## Account Execution Context

All steps in this task should be executed from the **newly created account**.

| Steps | Execute From |
|-------|--------------|
| 2.1 - 2.8 | **New Account** (the account you just created) |

## Time Estimate

- **Security approach selection:** 2-5 minutes
- **SCIM configuration (if applicable):** 5-10 minutes
- **Administrator setup:** 5-10 minutes
- **Network policies:** 5-10 minutes
- **Authentication policies:** 5-10 minutes
- **Break-glass setup:** 5-10 minutes
- **MFA enablement:** 2-5 minutes
- **Total:** 30-60 minutes

## Key Decisions

| Decision | Who Should Decide | Impact |
|----------|-------------------|--------|
| Use org security config or new | Security/Platform Team | Consistency vs flexibility |
| Account-specific administrators | Security/HR | Who has privileged access to this account |
| Network restrictions | Security/Network Team | Access control scope |
| Authentication requirements | Security Team | User experience vs security |
| Break-glass access | Security Team | Emergency access procedures |

## Configuration Approach

**Option 1: Use Organization Configuration**
- Reuses the same settings established in Platform Foundation
- Ensures consistency across all accounts
- Recommended for most accounts

**Option 2: Configure Custom**
- Allows account-specific security settings
- Useful for accounts with unique requirements
- Requires additional configuration questions

**Note:** Even when using organization configuration, you still need to:
- Create the SCIM integration (account-level object)
- Create a network POLICY referencing shared network RULES
- Set up break-glass access for THIS account
- Configure administrators for THIS account

**Shared Network Rules:** When using organization configuration, the network rules from Platform Foundation are shared via the Infrastructure database. You only need to create a network policy in this account that references those shared rules.

## Deliverables

Upon completing this task, you will have:
- ✅ User provisioning configured (SCIM or manual)
- ✅ Administrator users with ACCOUNTADMIN, SECURITYADMIN, SYSADMIN, USERADMIN roles
- ✅ Network rules and policies restricting access to allowed IPs
- ✅ Authentication policies defining login requirements
- ✅ Break-glass emergency access account
- ✅ MFA enabled for privileged users

## More Information

* [SCIM Overview](https://docs.snowflake.com/en/user-guide/scim) — Automated user provisioning
* [SAML/SSO Configuration](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth) — Federated authentication
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) — IP allowlisting
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies) — Auth requirements
* [MFA Best Practices](https://docs.snowflake.com/en/user-guide/security-mfa) — Multi-factor authentication