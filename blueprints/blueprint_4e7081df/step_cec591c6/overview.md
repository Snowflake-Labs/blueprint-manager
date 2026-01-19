In this step, you'll configure custom network rules and policies for this account. This allows you to define different network access controls than your Organization Account's standard configuration.

**Account Context:** This step should be executed from the newly created account.

## Why is this important?

Network policies act as a "bouncer" for your Snowflake account:
- **Allow only trusted IPs**: Corporate networks, VPNs, known data centers
- **Block suspicious sources**: Prevent access from unknown locations
- **Defense in depth**: Even with compromised credentials, unauthorized IPs can't connect

## External Prerequisites

- List of IP addresses/ranges that should access this account
- Knowledge of your corporate network, VPN, and data center IPs
- Understanding of any cloud service IPs (ETL tools, BI platforms) that need access

## Key Concepts

**Network Rules**
Define lists of IP addresses that are allowed or blocked. Rules are building blocks that are combined into policies.

**Network Policies**
Combine network rules to define access control. A policy can include allowed rules (whitelist) and blocked rules (denylist).

**Allowed vs Blocked**
- **Allowed Network Rules**: Only these IPs can access Snowflake
- **Blocked Network Rules**: These IPs are explicitly denied, even if they match an allowed rule

**Account-Level vs User-Level Policies**
- **Account-level**: Applies to all users by default
- **User-level**: Overrides account-level for specific users (like break-glass)

**More Information:**
* [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) — Complete network policy guide
* [Network Rules](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule) — Creating network rules

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

#### Define the allowed network rules for this account. (`account_allowed_network_rules`: object-list)
**What is this asking?**
Define the IP addresses that should be allowed to access this Snowflake account.

**Why does this matter?**
Network rules are your first line of defense, blocking access attempts from unauthorized locations before authentication even begins. Overly permissive rules increase attack surface; overly restrictive rules lock out legitimate users.

**For Consistency with Organization Account:**
To maintain consistent network policies across accounts, review your Organization Account's network rules (`SHOW NETWORK RULES IN ACCOUNT`) and enter the same values here.

**Format for each rule:**
- **rule_name**: Descriptive name (e.g., `corporate_network`, `vpn_endpoints`, `etl_servers`)
- **ip_addresses**: Comma-separated list of IPs or CIDR blocks

**Examples:**
| Rule Name | IP Addresses |
|-----------|--------------|
| `corporate_network` | `10.0.0.0/8, 192.168.0.0/16` |
| `vpn_endpoints` | `203.0.113.1, 203.0.113.2` |
| `cloud_services` | `52.0.0.0/8, 34.0.0.0/8` |

**Best Practices:**
- Start restrictive and add IPs as needed
- Document what each rule covers
- Use descriptive names for easy identification
- Include all necessary IPs before applying the policy

#### Define any blocked network rules for this account. (`account_blocked_network_rules`: object-list)
**What is this asking?**
Define IP addresses that should be explicitly blocked, even if they fall within an allowed range.

**Why does this matter?**
Block rules provide fine-grained control when you have broad allow rules. For example, you might allow your entire corporate network but need to block a guest WiFi subnet.

**When to use blocked rules:**
- Block specific IPs within a larger allowed range
- Explicitly deny known malicious sources
- Carve out exceptions from broad allow rules

**Example:**
If you allow `10.0.0.0/8` but want to block a specific subnet:
| Rule Name | IP Addresses |
|-----------|--------------|
| `blocked_guest_network` | `10.50.0.0/16` |

**Note:** If you don't need any blocked rules, you can leave this empty.

#### How would you like to configure security for this account? (`security_config_approach`: multi-select)
**What is this asking?**
Choose whether to replicate the Platform Foundation security settings or create custom settings for this account.

**Why does this matter?**
Consistent security settings across accounts simplify administration, reduce configuration errors, and make security audits easier. Custom settings are needed when an account has unique regulatory requirements or serves external users.

**Options explained:**

**Use Organization Configuration:**
- Applies the same settings from Platform Foundation
- Same IdP integration ({{ identity_provider }})
- Same network policy IP ranges
- Same authentication policy requirements
- Recommended for most accounts to maintain consistency

**Configure Custom Settings:**
- Allows different security settings for this account
- Can use a different IdP or manual user management
- Can have different network restrictions
- Can have different authentication requirements
- Best for: Accounts with unique regulatory requirements, partner accounts, or isolated environments

**Recommendation:**
Use organization configuration unless this account has specific requirements that differ from the standard. Consistency simplifies administration, auditing, and troubleshooting.

**More Information:**
* [Security Best Practices](https://docs.snowflake.com/en/user-guide/security-best-practices) — Snowflake security recommendations

**Note:** Even with organization configuration, this account will have its own:
- SCIM security integration (if applicable)
- Network rules and policies
- Authentication policies
- Administrator users
- Break-glass access
**Options:**
- Use Organization Configuration
- Configure Custom Settings
