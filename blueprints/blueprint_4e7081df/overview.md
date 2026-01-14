# Account Creation

Create and configure additional Snowflake accounts within your organization with security, identity, and cost management.

This workflow guides you through creating a new Snowflake account within your organization. It's a repeatable workflow designed to be run once for each account you need to provision.

Starting from your Organization Account, you'll define the account's purpose based on your multi-account strategy (domain-based, environment-based, or both), configure technical parameters, and execute the account creation. You'll then set up the new account with security controls (network policies, authentication, SCIM/SAML), establish emergency access procedures, and configure cost management (budgets, resource monitors, and cost allocation tags).

By the end of this workflow, you'll have a fully configured Snowflake account that:
- Follows your organization's naming conventions
- Has access to shared governance objects from your Organization Account
- Is secured with appropriate network and authentication policies
- Includes break-glass emergency access procedures
- Has budget monitoring and resource controls in place
- Is properly tagged for cost allocation and chargeback reporting

**Prerequisites**: This workflow assumes you have an existing Snowflake Organization Account. While designed to work with the Platform Foundation workflow, it can also run independently if you provide the required configuration values.
