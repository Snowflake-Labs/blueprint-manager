<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll enforce separation of duties for Snowflake system roles by restricting ACCOUNTADMIN to designated break-glass users only. All other users will have ACCOUNTADMIN revoked and should use SECURITYADMIN, SYSADMIN, or USERADMIN for their day-to-day work.

**Account Context:** Execute from the target account with SECURITYADMIN role.

## Why is this important?

ACCOUNTADMIN is the most powerful role in Snowflake. It can bypass all access controls, manage billing, and perform any operation. When too many users hold ACCOUNTADMIN:
- **Audit trails become meaningless** — you can't distinguish emergency access from routine use
- **Blast radius increases** — a compromised account with ACCOUNTADMIN can access everything
- **Compliance fails** — SOC 2, HIPAA, and PCI-DSS all require separation of duties

## Prerequisites

- Task 1 (RBAC Assessment) completed — Step 1.2 shows current ACCOUNTADMIN holders
- Break-glass user list approved by security team
- All ACCOUNTADMIN users should have MFA enabled

## Key Concepts

**System Role Responsibilities**
| Role | Purpose | Day-to-Day Use |
|------|---------|---------------|
| ACCOUNTADMIN | Account-level administration, billing | **Break-glass only** |
| SECURITYADMIN | Grant management, role hierarchy | Security operations |
| SYSADMIN | Database, schema, warehouse management | Platform operations |
| USERADMIN | User and role creation | Identity management |

**Break-Glass Pattern**
Break-glass users are emergency-access accounts used only when no other role can perform a required operation. They should:
- Be dedicated accounts (not shared with daily-use accounts)
- Have MFA enabled
- Be monitored for usage (any login should trigger an alert)
- Be documented in your incident response procedures

## Best Practices

- Limit ACCOUNTADMIN to 2-3 break-glass users
- Never use ACCOUNTADMIN for daily operations
- Ensure break-glass users have MFA enabled
- Monitor ACCOUNTADMIN usage with alerts (see Task 4)
- Document when and why ACCOUNTADMIN is used in your runbook

## How to Test

1. Verify authorized users can activate ACCOUNTADMIN when needed
2. Verify unauthorized users cannot activate ACCOUNTADMIN
3. Confirm daily operations work without ACCOUNTADMIN using appropriate system roles

## More Information

* [ACCOUNTADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#accountadmin-role) — Role definition
* [Separation of Duties](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system) — System role best practices
* [MFA](https://docs.snowflake.com/en/user-guide/security-mfa) — Multi-factor authentication


### Configuration Questions

#### Which users should retain ACCOUNTADMIN access (break-glass only)? (`rbac_accountadmin_users`: list)
**What is this asking?**
List the login names of users who are authorized to hold the ACCOUNTADMIN role.
All other users will have ACCOUNTADMIN revoked.

**Why does this matter?**
ACCOUNTADMIN is the most powerful role in a Snowflake account. It can:
- Create and drop any object
- Grant any privilege
- Manage billing and resource monitors
- Access all data

Best practice is to restrict ACCOUNTADMIN to 2-3 break-glass users and require
all other administration through SECURITYADMIN, SYSADMIN, or USERADMIN.

**Examples:**
- `BREAK_GLASS_USER_1`
- `BREAK_GLASS_USER_2`
- `PLATFORM_ADMIN`

**Recommendation:** Limit to 2-3 users maximum. These should be emergency
access accounts, not daily-use accounts. Ensure MFA is enabled for all
ACCOUNTADMIN users.

**More Information:**
* [ACCOUNTADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#accountadmin-role)

