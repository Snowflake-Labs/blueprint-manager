In this step, you'll define the schemas within each zone. Schemas organize related tables, views, and other objects within a database. Each schema will have its own set of database roles for granular access control.

For each schema you define, the following database roles will be created:
- `SC_R_<schema>` — Read access to the schema
- `SC_W_<schema>` — Write access to the schema
- `SC_C_<schema>` — Create access to the schema

**Account Context:** This is a planning step. Schemas are created in Task 2.

## Why is this important?

Schema organization provides:
- **Logical Grouping**: Related objects are grouped together
- **Fine-grained Access**: Different schemas can have different access policies
- **Namespace Management**: Prevents naming conflicts within a database
- **Governance**: Schemas can represent different subject areas or data sources

## Prerequisites

- Zone structure configured (Step 1.3)
- Understanding of your data sources and subject areas

## Key Concepts

**Schema Naming Patterns**

| Pattern | Example | Use Case |
|---------|---------|----------|
| By Source | `SAP`, `SALESFORCE`, `STRIPE` | Clear data lineage from source systems |
| By Subject Area | `CUSTOMERS`, `ORDERS`, `PRODUCTS` | Business-oriented organization |
| By Team | `MARKETING`, `FINANCE`, `OPS` | Team-based ownership |
| Functional | `STAGING`, `CORE`, `REPORTING` | Processing stage within a zone |

**Schema Access Roles (Database Roles)**

Each schema gets three database roles following a hierarchy:

```
SC_R_<schema> (Read)
    ↑
SC_W_<schema> (Write) - inherits Read
    ↑
SC_C_<schema> (Create) - inherits Write and Read
```

These schema-level roles roll up to database-level roles:
- `SC_R_*` → `DB_R`
- `SC_W_*` → `DB_W`
- `SC_C_*` → `DB_C`

**Managed Access Schemas**
All schemas are created with `MANAGED ACCESS`, meaning:
- Object owners cannot grant access to their objects
- Only the schema owner (ADMIN role) can manage grants
- Ensures centralized access control

**More Information:**
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-considerations#label-managed-access-schemas)


### Configuration Questions

#### What is the name of this data product? (`data_product_name`: text)
**What is this asking?**
Provide a descriptive name for your data product. This name will be used in database names, role names, and resource tags.

**Why does this matter?**
The data product name is a key component of object naming:
- Databases: `<domain>_<dataproduct>_<zone>_<env>` (based on your naming convention)
- Roles: `<dataproduct>_owner`, `<dataproduct>_reader`
- Tags: `DATAPRODUCT = '<dataproduct>'`

A clear, descriptive name makes resources easy to identify and manage.

**Naming Guidelines:**
- Use lowercase, single words or concatenated words (no underscores)
- Underscores are reserved for separating naming components (domain, zone, env)
- Be descriptive but concise
- Reflect the business purpose or use case
- Avoid technical jargon unless widely understood
- Avoid reserved words or special characters

**Examples:**
| Name | Description |
|------|-------------|
| `customer360` | Unified customer data and analytics |
| `salesanalytics` | Sales reporting and analysis |
| `supplychain` | Supply chain operations data |
| `finreporting` | Financial reporting and compliance |
| `marketing` | Marketing campaign attribution |
| `productcatalog` | Product information management |
| `inventory` | Inventory tracking and forecasting |

**Recommendation:**
Choose a name that business users would recognize. Ask: "If someone searched for this data, what would they type?"

**More Information:**
* [Identifier Requirements](https://docs.snowflake.com/en/sql-reference/identifiers-syntax) — Valid characters and length limits

#### Define the schemas for each zone in your data product. (`schema_configuration`: object-list)
**What is this asking?**
Define schemas within each zone. Schemas organize tables by source system 
or subject area.

**Example Configuration:**

**RAW Zone:**
| Schema | Purpose |
|--------|---------|
| SALESFORCE | Salesforce CRM data |
| SAP | SAP ERP data |
| STRIPE | Payment processing data |

**CURATED Zone:**
| Schema | Purpose |
|--------|---------|
| CUSTOMERS | Unified customer data |
| ORDERS | Order history |
| PRODUCTS | Product catalog |

**CONSUMPTION Zone:**
| Schema | Purpose |
|--------|---------|
| REPORTING | BI-ready tables |
| ANALYTICS | Aggregations and metrics |

**Best Practices:**
- Use consistent naming across zones
- Group by source system in RAW, by subject in CURATED
- Keep schema count manageable (2-5 per zone)

