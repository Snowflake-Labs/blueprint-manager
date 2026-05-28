<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll create and configure service accounts for automated workloads (ETL pipelines, BI tools, applications). Service accounts use key-pair authentication instead of passwords and are assigned dedicated functional roles and warehouses.

**Account Context:** Execute from the target account with USERADMIN (user creation) and SECURITYADMIN (role grants).

## Why is this important?

Service accounts differ from human user accounts in important ways:
- **No interactive login** — They authenticate via key-pair (RSA), not passwords
- **Dedicated warehouses** — Their compute consumption is tracked and budgeted separately
- **Least-privilege roles** — They get exactly the access needed for their workload
- **No MFA** — Key-pair authentication provides equivalent security without MFA

Without dedicated service accounts:
- Shared credentials create accountability gaps
- Human users' credentials are used in automation (revocation breaks pipelines)
- Compute costs are impossible to attribute to specific workloads

## Prerequisites

- Data Product roles exist (from Data Product Setup)
- Designated warehouses exist for each service account
- RSA key pairs generated for each service account (2048-bit minimum)
- Service account specifications approved (name, purpose, role, warehouse)

## Key Concepts

**Service Account Properties**
| Property | Value | Reason |
|----------|-------|--------|
| TYPE | SERVICE | Distinguishes from human users |
| DEFAULT_ROLE | Functional role | Auto-activates on connection |
| DEFAULT_WAREHOUSE | Dedicated WH | Isolates compute costs |
| RSA_PUBLIC_KEY | Base64-encoded | Key-pair authentication |
| MUST_CHANGE_PASSWORD | FALSE | Not using password auth |

**Key-Pair Authentication**
```bash
# Generate key pair (run locally, NOT in Snowflake)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

The public key (contents of `rsa_key.pub`, without headers) is stored in Snowflake. The private key is stored securely in your secrets manager.

## Best Practices

- Name service accounts with a consistent prefix (e.g., `SVC_`, `SA_`)
- One service account per workload/pipeline
- Rotate RSA keys annually
- Monitor service account activity with the views in Task 4
- Never assign ACCOUNTADMIN or SECURITYADMIN to a service account
- Set `DAYS_TO_EXPIRY` for temporary service accounts
- **Apply a user-level network policy** to restrict each service account to its expected IP range (see below)

## Network Policies for Service Accounts

Snowflake supports network policies at two levels:

| Level | Scope | Precedence |
|-------|-------|-----------|
| Account-level | All users in the account | Lower |
| User-level | A specific user | **Higher — overrides account-level** |

**Snowflake explicitly recommends user-level network policies for service accounts** (and other highly privileged users). If the account-level policy allows office or VPN IP ranges, a leaked service account credential could be used from those addresses. A user-level policy scoped to ETL or BI tool IPs eliminates that exposure.

**Recommended approach:**
1. Create a network rule scoped to the expected source IPs (e.g., your ETL cluster's egress CIDR):
   ```sql
   CREATE NETWORK RULE etl_network_rule
     TYPE = IPV4
     VALUE_LIST = ('203.0.113.0/24')
     MODE = INGRESS;
   ```
2. Create a network policy referencing the rule:
   ```sql
   CREATE NETWORK POLICY etl_network_policy
     ALLOWED_NETWORK_RULE_LIST = ('etl_network_rule');
   ```
3. Provide the policy name as `network_policy_name` in the service account configuration. The step generates `ALTER USER ... SET NETWORK_POLICY` automatically.

If your `platform-foundation-setup` blueprint already created network rules, reuse them rather than creating duplicates.

If `network_policy_name` is omitted for a service account, that account inherits the account-level network policy — no error, just lower restriction.

## How to Test

1. Connect using the service account's private key
2. Verify the default role is automatically activated
3. Verify the default warehouse is used
4. Confirm the service account can only access objects within its role's scope

## More Information

* [Key-Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth) — Setup guide
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user) — User properties
* [Service Users](https://docs.snowflake.com/en/user-guide/admin-user-management#service-users) — Service account best practices


### Configuration Questions

#### What service accounts need to be provisioned? (`rbac_service_accounts`: object-list)
**What is this asking?**
Define service accounts (non-human users) that need Snowflake access for
automated workloads like ETL pipelines, BI tool connections, or application
integrations.

**Why does this matter?**
Service accounts should:
- Have dedicated users (not shared human accounts)
- Use key-pair authentication (not passwords)
- Be granted the minimum required functional role
- Be restricted to specific warehouses
- Have descriptive names for auditability

**Fields:**
- **account_name**: Service account user name (e.g., SVC_AIRFLOW_SALES)
- **purpose**: Brief description of what this account does
- **role_level**: One of READ, WRITE, CREATE (avoid ADMIN for service accounts)
- **data_product_prefix**: The data product role prefix for access
- **warehouse**: The warehouse this account should use
- **network_policy_name** *(optional)*: Name of an existing Snowflake network policy
  to attach to this service account. User-level policies override account-level
  policies. Omit to inherit the account-level policy.

**Naming Convention:**
Use `SVC_<TOOL>_<DATAPRODUCT>` format:
- `SVC_AIRFLOW_SALES` — Airflow pipeline for sales data product
- `SVC_DBT_FINANCE` — dbt transformations for finance
- `SVC_TABLEAU_ANALYTICS` — Tableau reporting connection

**Examples:**
```yaml
- account_name: SVC_AIRFLOW_SALES
  purpose: Airflow ETL pipeline for sales ingestion
  role_level: WRITE
  data_product_prefix: SALES_ANALYTICS_PROD
  warehouse: SALES_ANALYTICS_PROD_WH_INGEST
  network_policy_name: ETL_NETWORK_POLICY
- account_name: SVC_TABLEAU_SALES
  purpose: Tableau reporting dashboard connection
  role_level: READ
  data_product_prefix: SALES_ANALYTICS_PROD
  warehouse: SALES_ANALYTICS_PROD_WH_BI
```

**Recommendation:** Every automated process should have its own service account.
Never share service accounts across tools or data products. Use WRITE level for
ETL tools and READ level for BI/reporting tools.

**More Information:**
* [Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth)
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user)

