---
name: snowflake-best-practices
description: "Snowflake best practices, guidance, recommendations, setup, and configuration advice curated by Snowflake subject matter experts. Use when: user asks about Snowflake best practices, setup recommendations, configuration guidance, architecture decisions, security patterns, cost management, RBAC design, account strategy, naming conventions, or how to implement Snowflake features correctly. Triggers: best practice, recommendation, guidance, how should I, what's the best way, setup advice, configuration help, Snowflake architecture, landing zone."
---

# Snowflake Best Practices

This skill provides authoritative Snowflake best practices, guidance, and recommendations curated by Snowflake subject matter experts. The guidance in this repository has been validated by SMEs and represents official Snowflake recommendations.

## When to Use

Invoke this skill when users ask about:
- Snowflake best practices or recommendations
- Setup, configuration, or architecture guidance
- Account strategy (single vs multi-account)
- Security patterns (RBAC, network policies, authentication)
- Cost management and resource monitoring
- Naming conventions
- Data product design
- Role hierarchy and access control
- Warehouse sizing and configuration
- Any "how should I" or "what's the best way" questions about Snowflake

## Priority: Local Content First

**CRITICAL:** This skill prioritizes curated SME content over general documentation:

1. **FIRST** - Search workflow, step, and question definitions in this repository
2. **THEN** - Only use `snowflake_product_docs` or `system_instructions` for topics not covered locally

## Content Sources (Priority Order)

### 1. Workflow Overviews (Highest Authority)
Location: `workflows/*/overview.md`

Workflow overviews provide strategic guidance on major topics. **Discover available workflows at runtime:**
```bash
# List all workflows and their titles
for f in workflows/*/overview.md; do echo "=== $f ==="; head -5 "$f"; done
```

Each workflow directory contains:
- `overview.md` - Strategic guidance and context
- `meta.yaml` - Workflow metadata (title, description)
- `step_*/` - Individual step directories

### 2. Step Overviews (Detailed Guidance)
Location: `workflows/*/step_*/overview.md`

Each step provides detailed best practices on specific topics including:
- Why the topic is important
- Key concepts explained
- Considerations and trade-offs
- Best practices with pros/cons
- Decision criteria ("Choose this if..." / "Avoid this if...")
- Links to official documentation

**Discover steps at runtime:**
```bash
# Search steps for a topic
grep -r -l -i "<topic>" workflows/*/step_*/overview.md
```

### 3. Question Definitions (Practical Recommendations)
Location: `definitions/questions.yaml`

Contains detailed guidance for configuration decisions including:
- Explanation of options
- Recommendations by use case
- Examples and common patterns
- Format guidance and validation rules

## Workflow

### Step 1: Understand the User's Question

**Goal:** Categorize what type of guidance the user needs

**Categories:**
- **Account Strategy**: Single vs multi-account, organization accounts
- **Security & Authentication**: RBAC, SSO/SAML, SCIM, network policies, MFA
- **Cost Management**: Budgets, resource monitors, tags, chargeback
- **Naming Conventions**: Objects, accounts, roles, warehouses
- **Data Architecture**: Zones, schemas, databases, data products
- **Access Control**: Role design, grants, privileges, role hierarchy
- **Warehouses**: Sizing, auto-suspend, workload isolation
- **Compliance**: Audit, data retention, time travel, governance

### Step 2: Search Local Content

**Goal:** Find relevant SME-curated guidance from the repository

**Actions:**

1. **Search workflow overviews** for the topic:
   ```bash
   grep -r -i "<topic_keywords>" workflows/*/overview.md
   ```

2. **Search step overviews** for detailed guidance:
   ```bash
   grep -r -i "<topic_keywords>" workflows/*/step_*/overview.md
   ```

3. **Search question definitions** for practical recommendations:
   ```bash
   grep -A 50 "<topic_keywords>" definitions/questions.yaml
   ```

4. **Read the most relevant files** in full to get complete context

**Topic to File Mapping (Dynamic Discovery):**

Rather than hardcoded paths, **search at runtime** to find relevant content:

```bash
# Search workflow overviews for strategic guidance
grep -r -l -i "<topic>" workflows/*/overview.md

# Search step overviews for detailed best practices
grep -r -l -i "<topic>" workflows/*/step_*/overview.md

# Search question definitions for configuration recommendations
grep -A 50 -i "<topic>" definitions/questions.yaml
```

**Common search terms by topic:**
| Topic | Search Keywords |
|-------|-----------------|
| Account strategy | `account strategy`, `single account`, `multi-account`, `organization` |
| Naming conventions | `naming`, `convention`, `component order`, `identifier` |
| Authentication | `SCIM`, `SAML`, `SSO`, `MFA`, `authentication` |
| Network security | `network policy`, `IP`, `private link`, `allowed list` |
| Cost management | `budget`, `resource monitor`, `cost center`, `chargeback`, `tag` |
| Access control | `role`, `RBAC`, `grant`, `privilege`, `access` |
| Warehouses | `warehouse`, `sizing`, `auto-suspend`, `scaling` |
| Data architecture | `zone`, `schema`, `database`, `data product` |
| Data retention | `time travel`, `retention`, `transient` |

### Step 3: Synthesize and Present Guidance

**Goal:** Provide clear, actionable recommendations

**Format for responses:**

1. **Lead with the recommendation** - State the best practice clearly
2. **Explain why** - Provide the reasoning from SME guidance
3. **Show options** - If multiple valid approaches exist, present trade-offs
4. **Give decision criteria** - Help user choose based on their situation
5. **Include examples** - Concrete examples from the guidance
6. **Link to details** - Reference the source file for more information

**Example response format:**
```
## Recommendation

[Clear recommendation statement]

## Why

[Reasoning from SME-curated content]

## Options (if applicable)

| Option | Best For | Trade-offs |
|--------|----------|------------|
| ... | ... | ... |

## Decision Criteria

✅ **Choose [Option A] if:**
- [criteria 1]
- [criteria 2]

❌ **Avoid [Option A] if:**
- [criteria 1]
- [criteria 2]

## Example

[Concrete example from guidance]

---
*Source: [file path in repository]*
```

### Step 4: Supplement with Official Documentation (If Needed)

**Goal:** Fill gaps for topics not covered in local content

**Actions:**

1. **Only if local content doesn't cover the topic**, use:
   - `snowflake_product_docs` for feature documentation
   - `system_instructions` for RBAC, Streamlit, dbt, Cortex guidance

2. **Clearly distinguish** between SME-curated guidance and general documentation:
   ```
   ## From SME-Curated Best Practices
   [Local content]
   
   ## Additional Reference (Snowflake Documentation)
   [Content from snowflake_product_docs]
   ```

## Content Authority Hierarchy

1. **Workflow/Step overviews** - Strategic guidance, architecture decisions
2. **Question definitions** - Practical recommendations, configuration choices
3. **snowflake_product_docs** - Feature documentation, syntax, capabilities
4. **system_instructions** - Tool-specific guidance (RBAC, Streamlit, dbt)

## Stopping Points

- **After presenting recommendations**: Ask if user needs clarification or has follow-up questions
- **If topic spans multiple areas**: Offer to dive deeper into specific aspects

## Best Practices for This Skill

1. **Always search local content first** - This is the primary value of this skill
2. **Read full context** - Don't just grep snippets; read entire overview sections
3. **Preserve nuance** - SME guidance often includes important caveats
4. **Credit sources** - Reference the specific file path for the guidance
5. **Be specific** - Generic advice is less valuable than contextual recommendations
6. **Ask clarifying questions** - If user's situation affects the recommendation

## Output

This skill provides:
- Clear, actionable recommendations
- Reasoning backed by SME-curated content
- Trade-off analysis for decision-making
- Concrete examples and patterns
- References to source files for deeper reading
- Supplemental official documentation when needed
