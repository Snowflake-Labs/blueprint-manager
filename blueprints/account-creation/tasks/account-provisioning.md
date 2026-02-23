# Account Provisioning

## Summary
Define the new account's purpose (domain, environment, description), configure
account parameters (edition, region, initial administrator), create the account
in your Snowflake organization, and establish access to shared infrastructure objects.

## External Requirements
- Platform Foundation workflow completed with Multi-Account strategy (recommended)
- Infrastructure Database Sharing configured (Step 1.8 of Platform Foundation)

## Personas
- Platform Administrator
- Cloud Team
- Security Team

## Role Requirements
- ORGADMIN role access in the Organization Account

## Details
This is a **repeatable workflow** — run it once for each account you need to create.

## Steps in This Task

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 1.0 | Confirm Account Strategy | Confirm or set the multi-account strategy (org-level) | Always shown |
| 1.1a | Define Account Purpose (Domain-based) | Select domain, description | Domain-based strategy only |
| 1.1b | Define Account Purpose (Environment-based) | Select environment, description | Environment-based strategy only |
| 1.1c | Define Account Purpose (Domain + Environment) | Select domain, environment, description | Domain + Environment strategy only |
| 1.2 | Configure Account Parameters | Set edition, region, and initial administrator | Always shown |
| 1.3 | Create Account | Execute the account creation from the Organization Account | Always shown |
| 1.4 | Consume Infrastructure Share | Create database from shared governance objects in the new account | Always shown |

**Notes:**
- Step 1.0 captures the account strategy at the organization level. If you completed Platform Foundation or a previous Account Creation run, the value will be pre-populated.
- Only one of the Step 1.1 variants will be displayed based on the account strategy.

**Note on Platform Foundation:**
While this workflow can run independently, it's designed to work with the Platform Foundation workflow. If Platform Foundation was completed, the following values are inherited:
- Organization name and account prefix
- Domain and environment options
- Naming conventions (component order, required components)
- Infrastructure share name
- Account strategy (captured in Step 1.0)

If Platform Foundation was not completed, Step 1.0 will capture the account strategy, and you'll need to provide other values manually.

## Account Execution Context

| Steps | Execute From |
|-------|--------------|
| 1.0 - 1.3 | **Organization Account** (where you create accounts) |
| 1.4 | **New Account** (log into the newly created account) |

**Important:** After Step 1.3, you must log into the newly created account to continue with Step 1.4.

## Time Estimate

- **Define purpose and parameters:** 5-10 minutes
- **Create account:** 2-5 minutes
- **Consume infrastructure share:** 2-5 minutes
- **Total:** 10-20 minutes

## Key Decisions

| Decision | Who Should Decide | Impact |
|----------|-------------------|--------|
| Account Name | Platform/Cloud Team | Permanent identifier; follows naming conventions |
| Domain & Environment | Business/Platform Team | Determines cost allocation and governance |
| Edition | Platform/Finance Team | Feature availability and cost |
| Cloud Region | Platform/Compliance Team | Data residency, latency, disaster recovery |
| Initial Administrator | Security/Platform Team | First person with ACCOUNTADMIN access |

## Deliverables

Upon completing this task, you will have:
- ✅ A new Snowflake account created in your organization
- ✅ Account named according to Platform Foundation conventions
- ✅ Initial administrator with ACCOUNTADMIN role
- ✅ Access to shared governance objects (tags, views) from Organization Account

## More Information

* [CREATE ACCOUNT](https://docs.snowflake.com/en/sql-reference/sql/create-account) — SQL command reference
* [Managing Accounts in an Organization](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Account lifecycle management
* [Introduction to Secure Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) — Understanding shared databases
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) — Feature comparison
* [Supported Cloud Regions](https://docs.snowflake.com/en/user-guide/intro-regions) — Available regions