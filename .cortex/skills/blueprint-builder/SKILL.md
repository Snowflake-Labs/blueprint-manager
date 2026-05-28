<!-- Copyright (c) 2026 Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. 
     Refer to the LICENSE file in the root of this repository for full terms. -->

---
name: blueprint-builder
description: "Guide users through constructing answer files for Snowflake Blueprint Manager blueprints. Use when: user wants to create or complete an answer file, configure a blueprint, or understand configuration questions. Triggers: create blueprint, build blueprint, configure blueprint, blueprint setup, fill out questionnaire, set up blueprint, set up my first Snowflake account, create my environment, establish my platform, create my account following best practices, configure my snowflake organization, set up my snowflake environment, initialize my snowflake platform, snowflake account best practices."
---

# Blueprint Builder

## CRITICAL: SQL/Output Generation Rules

**⚠️ MANDATORY: ALL SQL GENERATION AND OUTPUT RENDERING MUST USE `render_journey.py`**

When the user requests ANY of the following at ANY point during this skill's workflow:
- Generate SQL
- Generate infrastructure code
- Generate output
- Render the blueprint
- Create the SQL file
- Show me the SQL
- Build the code
- Export/produce/create infrastructure
- Any variation of "generate", "render", "create", "build", "export" combined with "SQL", "code", "output", "infrastructure"

**YOU MUST:**
1. Use the `scripts/render_journey.py` script to generate ALL SQL and documentation output
2. NEVER generate SQL code directly using ad-hoc logic or LLM inference
3. NEVER write SQL blocks manually based on answer file contents
4. NEVER attempt to "preview" or "show" SQL by constructing it yourself

**The ONLY valid method to generate SQL/output is:**
```bash
python scripts/render_journey.py \
  [answer_file_path] \
  --blueprint [blueprint_slug] \
  --lang sql \
  --project [project_name] \
  [--projects-dir <path>]  # optional, override projects/ output location
```

**WHY:** The `render_journey.py` script uses Jinja2 templates from the blueprint's step directories (`code.sql.jinja`, `dynamic.md.jinja`) to ensure:
- Consistent, tested, and validated SQL output
- Proper variable substitution from the answer file
- Correct handling of missing/null values (steps are skipped appropriately)
- Accurate documentation generation alongside code

**If user asks to "see the SQL" or "preview the code":**
- Run the render script first
- Then read and display the generated output file
- NEVER construct SQL manually

---

This skill guides users through constructing answer files for Snowflake Blueprint Manager blueprints by first understanding their organization through an open-ended description, then intelligently generating all configuration answers, and finally offering an optional step-by-step review.

## When to Use

Invoke this skill when users:
- Want to set up a Snowflake blueprint
- Need to create or complete an answer file for a blueprint
- Ask about blueprint configuration
- Want to configure their Snowflake environment
- Mention setting up infrastructure or governance

## Prerequisites

1. **Repository structure exists:**
   - `blueprints/` directory with blueprint definitions
   - `definitions/questions.yaml` with question definitions
   - `projects/` directory for organizing work by customer/use case

2. **Blueprint components:**
   - Each blueprint has a `meta.yaml` with blueprint metadata
   - Steps have `overview.md` files with context and guidance
   - Questions are defined with types: `single-select`, `multi-select`, `text`, `list`, or `object-list`

## Working Directory & Projects Path

The `blueprints/` and `definitions/` directories are always resolved relative to the script — they are not configurable.

The `projects/` directory (where rendered artifacts are written) is configurable via this priority:

1. `--projects-dir <path>` CLI flag (highest, passed to `render_journey.py`)
2. `BLUEPRINT_MANAGER_PROJECTS_DIR` environment variable
3. `<cwd>/projects` (current working directory, default)

When writing or reading project artifacts (e.g. `projects/<name>/answers/<blueprint>/<file>.yaml`), resolve the projects directory using this precedence and prefix paths accordingly. Bare relative paths to `blueprints/` and `definitions/` always work because they are script-relative.

## Experience-Level Rendering Profiles

This skill adapts verbosity to the user's stated familiarity with Snowflake. The level is captured once (Step 2.5) and persisted in the user's cortex memory so it applies across all blueprints and sessions.

Every text-heavy block (blueprint overview, task overview, step overview, summaries, recovery, transitions) maps the experience level to one of three rendering profiles:

| Tier | Profile | Length budget for prose blocks | Concept framing | Prerequisites |
|------|---------|---------------------------------|------------------|---------------|
| Beginner | **Verbose** | 4–8 sentences per block + concept primer | Always include "why this matters" + plain-language definitions | Full list with explanations |
| Intermediate | **Standard** | 2–4 sentences per block | Brief context only | Full list, no explanation |
| Advanced | **Concise** | 1 sentence + bulleted facts | Skip unless asked | Compact checklist |

These profiles are guidance for prose density. Structural elements (option lists, configuration questions, prerequisites bullets, persona tables, IaC commands) are rendered identically at every level — only the surrounding narrative scales.

### "Show Full Overview" Affordance

At every overview block (blueprint, task, step), the user may at any time say "show full overview", "show me the raw overview", "expand", or similar. When they do, the skill MUST:

1. Read and render the underlying source (`overview.md` for blueprint and step; `tasks/<task_slug>.md` for task) verbatim.
2. After displaying, return to the same menu/state the user came from — do not advance.

This affordance is available regardless of experience level so power users at any tier can drill into detail on demand.

### Changing the Level Mid-Session

If the user asks to change their experience level (e.g., "switch to advanced", "be more concise", "explain more"), update cortex memory immediately and apply the new profile to all subsequent output:
```bash
cortex ctx remember "Blueprint experience level: [new level]"
```

### Blueprint Overview Templates

**Beginner (Verbose):**
```
======================================================================
 Blueprint Overview: [Blueprint Name]
======================================================================

## What This Blueprint Will Do

[3–5 sentence conversational summary of overview.md, in your own words.
 Lead with the user-visible outcome ("By the end of this you'll have…"),
 then explain what gets built and why each piece matters. Use plain
 language and avoid Snowflake jargon without a quick definition.]

## How It's Structured

This blueprint has [N] tasks made up of [M] total configuration steps.
We'll go through them together, and at each task boundary I'll give you
a heads-up about what's coming.

## Before We Start — Things to Have Ready

**Snowflake roles you'll need access to:**
- [aggregated role_requirements, with a 1-line plain-language note for each]

**Things outside Snowflake you'll need:**
- [aggregated external_requirements, with a 1-line plain-language note for each]

**People who should be involved:**
- [aggregated personas with a 1-line note on what each typically reviews]

---

Ready to begin, or want me to expand any part of this overview?
```

**Intermediate (Standard):**
```
======================================================================
 Blueprint Overview: [Blueprint Name]
======================================================================

[2-sentence summary of overview.md.]

**Structure:** [N] tasks across [M] steps.

**Prerequisites:**
- Roles: [comma-separated role_requirements]
- External: [comma-separated external_requirements]
- Reviewers: [comma-separated personas]

Ready to begin?
```

**Advanced (Concise):**
```
======================================================================
 [Blueprint Name] — [meta.yaml `summary` line]
======================================================================
[N] tasks · [M] steps · Roles: [...] · External: [...] · Reviewers: [...]

Begin?
```

### Task Overview Templates

The structural sections (Prerequisites, Who Should Be Involved) are identical at every level — only the prose density and inclusion of supplementary content varies.

**Beginner (Verbose):**
```
======================================================================
 Starting Task [N] of [Total]: [Task Title]
======================================================================

## What You Will Accomplish
[Task `summary` field, plus 2–3 sentences explaining why this task block
 matters in the broader blueprint and what the user will have at the end.]

## Prerequisites

**Snowflake Role Requirements:**
- [role_requirement_1] — [1-line plain-language note on what this role does]
- [role_requirement_2] — [...]

**External Requirements:**
- [external_requirement_1] — [1-line plain-language note]
- [external_requirement_2] — [...]

## Who Should Be Involved
- [persona_1] — [1-line note on what they typically review or own]
- [persona_2] — [...]

[Include the FULL contents of tasks/<task_slug>.md if it exists, verbatim,
 after the structured fields above.]

---

This task contains [N] steps. Let's begin with the first one.
```

**Intermediate (Standard):**
```
======================================================================
 Starting Task [N] of [Total]: [Task Title]
======================================================================

## What You Will Accomplish
[Task `summary` field, as-is.]

## Prerequisites

**Snowflake Role Requirements:**
- [role_requirement_1]
- [role_requirement_2]

**External Requirements:**
- [external_requirement_1]
- [external_requirement_2]

## Who Should Be Involved
- [persona_1]
- [persona_2]

[If tasks/<task_slug>.md exists, include only its "Key Decisions" and
 "Deliverables" sections (omit the rest). If neither exists, omit the
 supplementary block entirely.]

---

This task contains [N] steps. Let's begin with the first one.
```

**Advanced (Concise):**
```
======================================================================
 Task [N]/[Total]: [Task Title] — [Task `summary` field]
======================================================================
Roles: [comma-separated role_requirements]
External: [comma-separated external_requirements]
Reviewers: [comma-separated personas]
[N] steps · Say "show full task overview" to see tasks/<task_slug>.md.

Beginning step 1.
```

### Step Overview Templates

Level-specific templates for the "## Step Overview" block (the Configuration Questions block is unaffected):

**Beginner (Verbose):**
```
**Concept Primer:** [1–2 sentences explaining the underlying Snowflake
concept(s) this step touches, in plain language. Skip if the step is
purely procedural with no new concept.]

**Why this step matters:** [1–2 sentences on why we do this and what
it unlocks for the rest of the blueprint.]

**What we're doing here:** [3–5 sentence summary of overview.md, in
your own words. Cover the key decision points without dumping the
raw markdown.]

*Want the full original write-up for this step? Say "show full step overview".*
```

**Intermediate (Standard):**
```
[1–2 sentence summary of overview.md, in your own words.]

*Say "show full step overview" for the complete write-up.*
```

**Advanced (Concise):**
```
[Step name and a 1-line purpose, then jump straight to the
 Configuration Questions block. No prose summary; the questions
 speak for themselves.]

*Say "show full step overview" if you want the original write-up.*
```

**At every level**, honor the "show full step overview" affordance: when the user requests it, dump the full contents of `blueprints/<blueprint_slug>/<step_id>/overview.md` verbatim, then redisplay the step menu.

### Step 6 Summary Verbosity

Apply the rendering profile based on the user's experience level:
- **Beginner (Verbose):** keep the full prose template — show full reasoning paragraphs for every answered question, multi-line "what's needed" / "how to find it" guidance for required values, and full "missing context" explanations for insufficient-context items.
- **Intermediate (Standard):** keep the section structure, but compress reasoning to one short clause per answered question (e.g., `enable_mfa: 'Yes' — SOC2 compliance`). Required-value entries keep their "what's needed" line but drop "how to find it" unless non-obvious.
- **Advanced (Concise):** render answered questions as a compact table (`question | answer | reasoning`); list required values as a single bulleted checklist with one-line asks; list insufficient-context items as a one-line bulleted checklist.

### Context Recovery Verbosity

The structural sections (current task name, current step, progress percentages, list of remaining steps) are identical at every level. The "What You Will Accomplish" prose, role/external requirement notes, and previously-completed-task summaries scale: full plain-language sentences at Beginner; raw `summary` strings at Intermediate; compact one-line variants at Advanced (e.g., "Resuming task 3/5 — [task title]; on step 7/12; remaining: …").

### Task Boundary Transitions Verbosity

The structural elements (task counts, "Up Next" task title, progress numbers) are identical at every level. The "Up Next" task summary and prerequisites scale: at Beginner, include a 2–3 sentence framing of why the next task matters and what new context it introduces; at Intermediate, show the next task's `summary` field as-is; at Advanced, condense the entire transition to a single line (e.g., `✓ Task 2/5 complete · Up next: Task 3/5 — [title]. Continue?`).

## Workflow

### Step 1: Select or Create Project

**Goal:** Identify which project the user wants to work with, or create a new one

**Actions:**

1. **List existing projects** in the repository:
   ```bash
   ls -la projects/
   ```

2. **Present project options to user:**
   ```
   Projects organize your blueprint configurations by customer, account, or use case.
   
   Existing projects:
   
   1. sample-project (example project with sample answers)
   [... any other existing projects ...]
   
   Would you like to:
   
   1. Work with an existing project
   2. Create a new project
   
   Enter your choice (1-2):
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user to select or create a project.

**If user selects existing project:**
- Note the project name for use in subsequent steps
- Proceed to Step 2 (Discover and Recommend Blueprint)

**If user wants to create a new project:**
1. **Prompt for project name:**
   ```
   Enter a name for your new project.
   
   Guidelines:
   - Use only alphanumeric characters, underscores, and hyphens
   - Example: customer_acme, prod-deployment, pilot-2024
   
   Project name:
   ```

2. **⚠️ MANDATORY STOPPING POINT**: Wait for user to provide project name.

3. **Validate project name** (alphanumeric, underscores, hyphens only)

4. **Create project directory structure:**
   ```bash
   mkdir -p projects/<project_name>/answers
   mkdir -p projects/<project_name>/output/iac/sql
   mkdir -p projects/<project_name>/output/documentation
   ```

5. **Confirm creation:**
   ```
   ✓ Created project: <project_name>
   
   Project directory: projects/<project_name>/
   ├── answers/           (for answer files)
   └── output/
       ├── iac/sql/       (for generated SQL)
       └── documentation/ (for generated docs)
   ```

6. **Proceed to Step 2** (Discover and Recommend Blueprint)

**Output:** Selected or created project name

### Step 2: Discover and Recommend Blueprint

**Goal:** Identify which blueprint best matches the user's intent, recommend it, and confirm selection.

**Actions:**

1. **Load all blueprint metadata:**
   ```bash
   find blueprints -name "meta.yaml" -type f
   ```
   For each blueprint, load `blueprints/<blueprint_slug>/meta.yaml` and extract: `name`, `summary`, `tasks` (titles), `steps`, `is_repeatable`.

2. **Match intent to blueprint.** If the user's initial prompt or earlier conversation provides context about what they want to do (e.g., "set up my Snowflake account", "create a data product", "harden RBAC"), recommend the best-matching blueprint directly:

   ```
   Based on what you've described, I'd recommend:

   → [Blueprint Name]
     [Brief summary]

     Tasks:
     - [Task 1 Title]
     - [Task 2 Title]
     - [Task 3 Title]
     - [Task 4 Title]

   There are also [N] other blueprints available.
   Would you like to proceed with this one, or see the full list?
   ```

   **If no clear intent** (user just said "set up a blueprint" or "what's available"), skip the recommendation and go directly to the full list (action 3).

3. **Full list (fallback or on request).** Present a compact table, then expand on request:

   ```
   Available blueprints:

   | # | Blueprint                         | Tasks |
   |---|-----------------------------------|-------|
   | 1 | [Name]                            | [N]   |
   | 2 | [Name]                            | [N]   |
   | ...                                           |

   Say a number to see details, or type a name to select.
   ```

   When the user picks a number or asks for details, show the full summary + task list for that blueprint before confirming selection.

**⚠️ MANDATORY STOPPING POINT**: Wait for user to confirm blueprint selection.

**Output:** Selected blueprint slug (directory name) and metadata

> **Note:** The blueprint slug is the directory name under `blueprints/` (e.g., `platform-foundation-setup`). This is **different** from the `blueprint_id` field inside `meta.yaml` (e.g., `blueprint_4d563df2`). All file path operations in subsequent steps use the slug.

### Step 2.5: Capture Experience Level

**Goal:** Determine the user's familiarity with Snowflake and data platforms so every subsequent overview, summary, and explanation can be rendered at the right depth.

This step runs immediately after blueprint selection and BEFORE the blueprint overview (Step 2.6) so that overview can already be scaled appropriately.

**Actions:**

1. **Check cortex memory for an existing preference.**
   Search the user's memory for a "Blueprint experience level" entry. If found, acknowledge it and offer to change:
   ```
   Your experience level is set to [level]. I'll tailor my explanations accordingly.
   (Say "switch to beginner/intermediate/advanced" anytime to change this.)
   ```
   Then proceed directly to Step 2.6.

2. **If no level found in memory, ask the intro question:**
   ```
   Before we go further, one quick question so I can pitch this at the right level.

   How would you describe your familiarity with Snowflake and data platforms?

   1. Beginner — New to Snowflake or data platforms. I'd like concepts
      explained and "why this matters" framing along the way.
   2. Intermediate — I'm comfortable with the basics (accounts, roles,
      warehouses, RBAC). Give me enough context to make good decisions.
   3. Advanced — I know Snowflake well. Keep it concise and
      action-oriented.

   Enter your choice (1-3):
   ```

3. **⚠️ MANDATORY STOPPING POINT:** Wait for the user's choice.

4. **Persist to cortex memory:**
   ```bash
   cortex ctx remember "Blueprint experience level: [chosen level]"
   ```

5. **Confirm to the user (one line, scaled to chosen level):**
   - Beginner: "Got it — I'll explain Snowflake concepts as we go and walk you through the reasoning at each step. You can say 'switch to advanced' anytime to dial it back."
   - Intermediate: "Got it — I'll keep context tight but include the key reasoning. Say 'be more concise' or 'explain more' anytime."
   - Advanced: "Got it — concise and action-oriented. Say 'explain more' anytime to expand."

**Changing the level mid-session:** If the user says "switch to advanced", "be more concise", "explain more", or similar at any point, update cortex memory immediately:
```bash
cortex ctx remember "Blueprint experience level: [new level]"
```
Then apply the new profile to all subsequent output. (See "Experience-Level Rendering Profiles" near the top of this skill for the per-tier templates.)

**Output:** Experience level known and stored in cortex memory.

### Step 2.6: Present Blueprint Overview

**Goal:** Give the user a CoCo-summarized, conversational sense of what this blueprint will accomplish — derived from `overview.md` and `meta.yaml`, scaled to the experience level captured in Step 2.5.

**Inputs:**
- `blueprints/<blueprint_slug>/overview.md` — full overview text
- `blueprints/<blueprint_slug>/meta.yaml` — `name`, `summary`, `tasks` (count + per-task `summary`, `personas`, `role_requirements`, `external_requirements`), `steps` (count)
- Optional `blueprints/<blueprint_slug>/tasks/<task_slug>.md` files — used only for "show full overview" expansion

**Actions:**

1. **Load all inputs.**

2. **Aggregate prerequisites across tasks:**
   - Union of `role_requirements` across all tasks
   - Union of `external_requirements` across all tasks
   - Union of `personas` across all tasks (so the user knows up-front who needs to be involved)

3. **Render the overview** using the level-specific Blueprint Overview template from the "Experience-Level Rendering Profiles" section above.

4. **Honor the "show full overview" affordance.** If the user says "show full overview", "show the raw overview", "expand", or similar, dump `overview.md` verbatim and then redisplay the level-appropriate "Ready to begin?" prompt.

5. **⚠️ MANDATORY STOPPING POINT:** Wait for the user to confirm they're ready to proceed (or to expand).

**Output:** User has read the blueprint overview and is ready to proceed to Step 3.

### Step 3: Initialize or Select Answer File

**Goal:** Let user choose to create a new answer file or work with an existing one

**Actions:**

1. **Check for existing answer files in the project:**
   ```bash
   find projects/<project_name>/answers/<blueprint_slug> -name "*.yaml" -type f 2>/dev/null | sort -r
   ```

2. **Present options to user:**
   ```
   Would you like to:
   
   1. Create a new answer file
   2. Work with an existing answer file
   
   Enter your choice (1-2):
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

**If user selects "Create a new answer file":**

1. **Generate timestamp:**
   ```bash
   date +%Y%m%d%H%M%S
   ```

2. **Create answer file directory:**
   ```bash
   mkdir -p projects/<project_name>/answers/<blueprint_slug>
   ```

3. **Create initial answer file:**
   - Path: `projects/<project_name>/answers/<blueprint_slug>/answers_<timestamp>.yaml`
   - Initialize with header comments (project name, blueprint name, date, blueprint ID)

4. **Proceed to Step 4** (Collect User Context)

**If user selects "Work with an existing answer file":**

1. **List available answer files:**
   ```
   Existing answer files for this project and blueprint:
   
   1. projects/<project_name>/answers/<blueprint_slug>/answers_20251221214657.yaml
      Created: 2025-12-21 21:46:57
      
   2. projects/<project_name>/answers/<blueprint_slug>/answers_20251221222441.yaml
      Created: 2025-12-21 22:24:41
   
   Which file would you like to work with? (1-N):
   ```

2. **⚠️ MANDATORY STOPPING POINT**: Wait for user to select a file.

3. **Run the migration script** to ensure the file is compatible with the current schema before loading:
   ```bash
   python3 scripts/migration/migrate_answers.py [selected_file_path] --dry-run
   ```
   - If the dry-run reports changes, apply them:
     ```bash
     python3 scripts/migration/migrate_answers.py [selected_file_path]
     ```
   - If the script reports errors or the file cannot be parsed, direct the user to `scripts/TROUBLESHOOTING.md` for resolution before continuing.
   - If no changes are needed, proceed immediately.

4. **Load selected answer file:**
    - Read the YAML file
    - Parse existing answers
    - Validate structure

5. **Present current state:**
   ```
   Loaded answer file: [file path]
   
   Current configuration:
   - Total questions in workflow: [N]
   - ✅ Questions answered: [M]
   - ❓ Requires user input: [P]
   - ⚠️ Needs more context: [Q]
   ```

5. **Offer next actions:**
   ```
   What would you like to do?
   
   1. Review/update configuration step-by-step
   2. Fill in required values (account names, emails, etc.)
   3. View current configuration summary
   4. Generate infrastructure code (SQL)
   5. Start over with new context (will prompt for description)
   
   Enter your choice (1-5):
   ```

6. **⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

7. **Route based on selection:**
   - Option 1 → Skip to Step 7 (Interactive Walkthrough)
   - Option 2 → Skip to Step 8 (Fill in required values)
   - Option 3 → Skip to Step 6 (Present Summary)
   - Option 4 → Skip to Step 9 (Generate IaC)
   - Option 5 → Proceed to Step 4 (will regenerate all answers based on new context)

**Output:** Path to answer file (new or existing) and current state

### Step 4: Collect User Context (Open-Ended Description)

**Goal:** Request a description of the user's organization and their plans for how they will use snowflake to understand their needs well enough to intelligently fill out all workflow answers.

**Actions:**

1. **Load all question definitions:**
   ```bash
   read definitions/questions.yaml
   ```

2. **Parse questions** to understand what information is needed across the entire blueprint

3. **Generate topic suggestions from the blueprint's questions.** Scan the loaded questions and group them by theme (e.g., by their parent task or by semantic similarity). Produce 3–5 topic categories that are specific to *this* blueprint, with 2–3 example questions per category. Do NOT use a hardcoded topic list — derive it from the actual questions.

   **How to derive topic categories:** Group the blueprint's questions by their parent task title. For each task, summarize what kind of information the questions in that task are asking for. Use the task title as the topic header and the question `guidance` fields to identify 2–3 representative information needs. Skip tasks where questions are purely procedural (e.g., "confirm you've completed X").

4. **Present open-ended request with the dynamically generated topics AND step-by-step option:**

   ```
   I can help you configure [Blueprint Name] in one of two ways:
   
   ---
   
   **Option A: Provide a Description (Recommended)**
   
   Share an open-ended description of your situation, and I'll intelligently 
   configure as many settings as possible based on what you tell me.
   
   To help me answer the most questions, consider including information about:
   
   [Dynamically generated topic categories based on this blueprint's questions.
    Each category is a bold header with 2-3 bullet points showing the kind of
    information that would be helpful.]
   
   **[Topic 1 derived from task/question themes]**
   - [Relevant consideration from this blueprint's questions]
   - [Another relevant consideration]
   
   **[Topic 2]**
   - [...]
   - [...]
   
   **[Topic 3]**
   - [...]
   
   [3-5 topic groups total. Keep each concise.]
   
   Share as much or as little as feels relevant.
   
   ---
   
   **Option B: Step-by-Step Walkthrough**
   
   If you prefer, I can walk you through each question one at a time, 
   explaining each option as we go. This takes longer but gives you 
   full control over every decision.
   
   ---
   
   **How would you like to proceed?**
   
   - Type your description to use Option A
   - Or type "step-by-step" to go through questions one at a time
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user response.

**If user provides a description:**
- Proceed to Step 5 (Generate All Workflow Answers based on context)

**If user types "step-by-step" (or similar):**
- Skip Step 5 entirely
- Create answer file with all questions as `null`
- Proceed directly to Step 7 (Interactive Step-by-Step Walkthrough)
- Present each question with full guidance, one at a time

**Output:** Either user context for auto-generation, or indication to use step-by-step mode

### Step 5: Generate All Blueprint Answers

**Goal:** Intelligently fill out blueprint answers based on user's context, being honest about what can and cannot be determined

**Actions:**

1. **Load blueprint steps:**
   - Read `blueprints/<blueprint_slug>/meta.yaml` for step order
   - Load each step's `overview.md` to understand questions

2. **For each step, extract questions:**
   - Parse overview.md for question IDs (format: `` `answer_title` ``)
   - Look up question definitions from `questions.yaml`

3. **Categorize each question into one of three types:**

   **Category A: Auto-Answerable** - Questions where user context provides enough information to make a confident decision
   
   **Category B: User-Specific Required** - Questions that ALWAYS require user input (account names, emails, org names, etc.) - these are NOT auto-answerable
   
   **Category C: Insufficient Context** - Questions where the user's description doesn't provide enough information to make a reasonable choice

4. **⚠️ STRICT RULES FOR ANSWER GENERATION:**

   **DO NOT generate fake TODO answers.** Specifically:
   - ❌ Do NOT use placeholder values like `YOUR_ACCOUNT_NAME`, `user@example.com`, `YOUR_COMPANY_NAME`
   - ❌ Do NOT invent domain names, team names, or organizational structures not mentioned by user
   - ❌ Do NOT guess specific values (IP ranges, user counts, budget amounts) unless explicitly stated
   - ❌ Do NOT create list items (domains, warehouses, users) that weren't mentioned or clearly implied
   
   **INSTEAD:**
   - ✅ Leave Category B questions unanswered (null/empty in YAML)
   - ✅ Leave Category C questions unanswered with a comment explaining what information is needed
   - ✅ Only answer Category A questions where you have genuine confidence

5. **Apply intelligent defaults ONLY when context supports it:**

   **Decision Logic Examples (use only when user provided relevant context):**
   
   **Organization Size (if explicitly mentioned):**
   - Small startup → Single account, simple RBAC, minimal admins
   - Mid-size → Consider multi-account, moderate RBAC complexity
   - Enterprise → Multi-account strategy, complex RBAC, multiple admins
   
   **Use Case (if explicitly mentioned):**
   - Analytics/BI → Focus on warehouses for queries, reader roles
   - Data Engineering → ETL warehouses, writer/owner roles, pipelines
   - ML/Data Science → Compute-optimized warehouses, data science roles
   
   **Security Posture (if explicitly mentioned):**
   - Has SSO → Configure SSO/SAML, use IdP for MFA
   - No SSO → Username/password with MFA, strong password policy
   - Strict network → Specific IP ranges, service account restrictions
   - Flexible → Broader access (0.0.0.0/0 with caution notes)
   
   **Compliance (if explicitly mentioned):**
   - GDPR/HIPAA/SOC2 → Enable audit schemas, change tracking, data retention policies
   - None → Balanced policies, monitoring recommended but optional
   
   **Cost Control (if explicitly mentioned):**
   - Strict → Resource monitors with suspend, hourly budget refresh, required tags
   - Moderate → Budgets with alerts, daily refresh, recommended tags
   - Flexible → Budget tracking, no hard limits
   
   **Budget Range (if explicitly mentioned):**
   - Under $1K → 250 credits/month budget, small warehouses
   - $1-10K → 2,500 credits/month, moderate resources
   - $10-50K → 7,500 credits/month, production scale
   - $50K+ → Custom based on needs

6. **Write answers to YAML file:**
   - Use `answer_title` as keys
   - Set values ONLY for Category A questions (auto-answerable with confidence)
   - Add inline comments explaining reasoning for each answered question
   - Leave Category B and C questions as `null` or omit entirely
   - Add comment for each unanswered question explaining why it wasn't answered

7. **Track and report answer status:**
   - Count questions in each category
   - Prepare detailed list of unanswered questions with reasons

**Output:** Answer file with honest answers and clear tracking of what was/wasn't answered

### Step 6: Present Summary and Offer Walkthrough

**Goal:** Show user exactly what was configured, what wasn't, and why

**Verbosity:** Apply the rendering profile based on the user's experience level — see "Step 6 Summary Verbosity" in the "Experience-Level Rendering Profiles" section above. The full prose template below is the Beginner (Verbose) form; compress per the profile guidance for Intermediate and Advanced.

**Actions:**

1. **Present detailed configuration summary with transparency:**
   ```
   ======================================================================
    Configuration Summary
   ======================================================================
   
   ## ✅ Questions Successfully Answered ([M] of [Total])
   
   Based on your description, I was able to confidently answer these questions:
   
   ### Account Strategy
   - [Question name]: [Answer] — Reasoning: [why]
   
   ### Security & Compliance
   - [Question name]: [Answer] — Reasoning: [why]
   
   ### Cost Controls
   - [Question name]: [Answer] — Reasoning: [why]
   
   [Continue for all answered questions...]
   
   ---
   
   ## ❓ Questions Requiring Your Input ([P] of [Total])
   
   These questions require information only you can provide:
   
   1. **[question_name]** (`answer_title`)
      - What's needed: [specific information required, e.g., "Your Snowflake account name"]
      - How to find it: [help text, e.g., "Run SELECT CURRENT_ACCOUNT_NAME(); in Snowflake"]
   
   2. **[question_name]** (`answer_title`)
      - What's needed: [specific information required]
      - How to find it: [help text]
   
   [Continue for all user-specific questions...]
   
   ---
   
   ## ⚠️ Questions Not Answered - Insufficient Context ([Q] of [Total])
   
   I didn't have enough information from your description to answer these:
   
   1. **[question_name]** (`answer_title`)
      - Missing context: [what information would help, e.g., "Number of data domains/teams"]
      - Please provide: [specific ask]
   
   2. **[question_name]** (`answer_title`)
      - Missing context: [what information would help]
      - Please provide: [specific ask]
   
   [Continue for all insufficient-context questions...]
   
   ---
   
   Answer file saved: [file path]
   
   **Summary:**
   - ✅ Auto-answered: [M] questions
   - ❓ Needs your input: [P] questions  
   - ⚠️ Needs more context: [Q] questions
   - Total: [Total] questions
   ```

2. **Offer walkthrough options:**
   ```
   What would you like to do next?
   
   1. Provide more context (I'll ask about unanswered questions)
   2. Fill in required values now (account names, emails, etc.)
   3. Review all configuration step-by-step
   4. Generate infrastructure code (SQL) with current answers
   5. Save and exit
   
   Enter your choice (1-5):
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

**Route based on selection:**
- Option 1 → Ask follow-up questions for Category C items, then regenerate
- Option 2 → Proceed to Step 8 (Update user-specific values)
- Option 3 → Proceed to Step 7 (Walkthrough)
- Option 4 → Proceed to Step 9 (Generate IaC) — warn if many questions unanswered
- Option 5 → End workflow

### Step 7: Interactive Step-by-Step Walkthrough

**Goal:** Walk through each blueprint step, showing questions, answers, reasoning, and allowing updates

**For each step in blueprint.steps:**

#### Step 7.0: Display Task Overview at Task Boundaries

Before presenting a step's details, check whether this step is the **first step in a new task**. If so, display a task overview before proceeding. This gives users immediate context about what they are about to work on, what roles/access they need, and who should be involved.

**Actions:**

1. **Determine if this is a task boundary:**
   - Find which task in `meta.yaml` contains the current step slug
   - Check if the current step is the first step in that task (i.e., index 0 in the task's steps list)

2. **If this is the first step in a new task, display the task overview:**

   First, load the task overview markdown file if available:
   ```bash
   read blueprints/<blueprint_slug>/tasks/<task_slug>.md
   ```

   Render the task overview using the rendering profile that matches the user's experience level. The structural sections (Prerequisites, Who Should Be Involved) are identical at every level — only the prose density and inclusion of supplementary content varies.

   See "Task Overview Templates" in the "Experience-Level Rendering Profiles" section above for the per-tier templates.

   **Rules common to all levels:**
   - **Summary** comes from the task's `summary` field in meta.yaml
   - **Role Requirements** comes from the task's `role_requirements` field. If empty, omit this section.
   - **External Requirements** comes from the task's `external_requirements` field. If empty, omit this section.
   - **Personas** comes from the task's `personas` field. If empty, omit this section.
   - Honor the "show full overview" affordance: at any tier, if the user says "show full task overview" / "expand", read and dump `tasks/<task_slug>.md` verbatim, then resume the same flow.
   - If this is the first task in the blueprint, do NOT re-display the blueprint-level overview here — Step 2.6 has already shown it. Proceed directly to the task overview.

3. **If this is NOT the first step in a task**, skip the task overview and proceed directly to Step 7.1.

#### Step 7.1: Display Step Overview and Questions

**Actions:**

1. **Read step overview:**
   ```bash
   read blueprints/<blueprint_slug>/<step_id>/overview.md
   ```

2. **Extract questions for this step** (parse overview.md for question IDs)

3. **Load question details** from definitions/questions.yaml for all questions in this step

4. **Resolve options for single-select and multi-select questions** using the three-stage resolution below before presenting any question.

   > **Maintainer note — Three-Stage Option Resolution:**
   > For every single-select or multi-select question, options are resolved in this priority order:
   > - **Stage 1a (Dynamic, in-memory):** If the question has a `dynamic_options_source` field, look up the current in-memory answer for the `answer_title` referenced by that field. If the answer is non-empty (the source question has been answered in this session and contains list values), use those list values as the options. Proceed to render normally.
   > - **Stage 1b (Dynamic, project files):** If Stage 1a finds nothing (source not yet answered in this session), search all `*.yaml` answer files saved under `projects/<project_name>/answers/` for a key matching `source_title`. If a non-empty list value is found, use it as the options. Record the file it came from (`resolved_source`) to show the user where the options originated. Proceed to render normally.
   > - **Stage 2 (Static fallback):** If neither Stage 1a nor 1b yields options (either `dynamic_options_source` is absent, or the source key was not found anywhere), check whether the question has a static `options` list. If present, use it. Proceed to render normally.
   > - **Stage 3 (Block):** Only if none of the above stages yield options, block the question. Display a notice that varies by sub-case: if the source question was answered in-memory but produced no usable values (empty or non-list result), tell the user that no options are available from that answer; if the source question has not been answered yet in any project file, tell the user to complete the blueprint that defines it first; if there is no `dynamic_options_source` at all (and no static `options` list), tell the user that no options are available and the question definition should be checked.
   >
   > A question with both `dynamic_options_source` and a static `options` list is valid: Stage 1a/1b take priority when the source is answered; Stage 2 provides a graceful fallback when it is not. Never treat `dynamic_options_source` and `options` as mutually exclusive.

   **Resolution algorithm (apply per question before display):**

   ```
   For each single-select / multi-select question:

     resolved_options = []
     resolved_source = null                            # tracks where options came from
     source_title = question.dynamic_options_source    # may be null/absent
     source_was_answered = false

     # Stage 1a — Dynamic, in-memory (current session)
     if source_title is present:
       if source_title in in_memory_answers:           # key exists → source was answered this session
         source_answer = in_memory_answers[source_title]
         if source_answer is non-empty list:
           resolved_options = source_answer
           resolved_source = "current answers"
         else:
           source_was_answered = true                  # answered but produced no usable options

     # Stage 1b — Dynamic, project files (cross-blueprint lookup)
     if resolved_options is empty and source_title is present and not source_was_answered:
       for each yaml_file in glob("projects/<project_name>/answers/**/*.yaml"):
         loaded = parse_yaml(yaml_file)
         if source_title in loaded and loaded[source_title] is non-empty list:
           resolved_options = loaded[source_title]
           resolved_source = relative path of yaml_file
           break

     # Stage 2 — Static fallback
     if resolved_options is empty:
       if question.options is present and non-empty:
         resolved_options = question.options
         resolved_source = "question definition"

     # Stage 3 — Block
     if resolved_options is empty:
       → Do NOT render the question for input
       → if source_was_answered:
           Display: "⚠️ This question has no available options. '[source_title]'
                     was answered but produced no selectable values."
         elif source_title is present:
           Display: "⚠️ This question cannot be answered yet. '[source_title]' was
                     not found in the current session or in any saved answer files
                     for project '<project_name>'. Complete the blueprint that
                     defines '[source_title]' first, then return to this question."
         else:
           Display: "⚠️ This question has no available options and no dynamic
                     source is configured. Check the question definition."
       → Skip to next question
     else:
       → Render question normally using resolved_options and resolved_source
   ```

5. **Present step information.** Render the "## Step Overview" block according to the user's experience level — see "Step Overview Templates" in the "Experience-Level Rendering Profiles" section above. The Configuration Questions block stays identical at every level (questions, options, guidance, reasoning are always shown in full).

   ```
   ======================================================================
    Step [N] of [Total]: [Step Name]
   ======================================================================
   
   ## Step Overview
   
   [Render this block per the level-specific template (Beginner / Intermediate / Advanced).
    Honor the "show full step overview" affordance: when the user requests it, dump the
    full contents of overview.md verbatim, then redisplay the step menu.]
   
   ---
   
   ## Configuration Questions and Answers
   
    ### Question 1: [question_text]
    
    **Answer:** [your answer]
    
    **Reasoning:** [why this answer was chosen based on user context]
    
    **Question Details:**
    - **Type:** [answer_type: single-select, multi-select, text, list, or object-list]
    - **Guidance:** 
      [Full guidance text from definitions - all paragraphs and formatting]
     [For single-select / multi-select questions — Stage 1a/1b or Stage 2 resolved options:]
     - **Available Options** (from `[resolved_source]`):
       1. [option 1 text]
       2. [option 2 text]
       ...
     [For single-select / multi-select questions — Stage 3 blocked (source not found anywhere):]
     ⚠️ This question cannot be answered yet. '[source_title]' was not found in the current session or in any saved answer files for project '<project_name>'. Complete the blueprint that defines '[source_title]' first, then return to this question.
     [For single-select / multi-select questions — Stage 3 blocked (source answered, no usable values):]
     ⚠️ This question has no available options. '[source_title]' was answered but produced no selectable values.
     [For single-select / multi-select questions — Stage 3 blocked (no dynamic source configured):]
     ⚠️ This question has no available options and no dynamic source is configured. Check the question definition.
     
      ---
      
      [Continue for additional questions in this step using the same Question 1 template above...]
    
    ---
   ```

6. **Present step menu:**
   ```
   What would you like to do?
   
   1. Update answer for Question [1-N]
   2. Continue to next step
   3. Go back to previous step
   4. Jump to specific step
   5. Generate infrastructure code (SQL) and exit
   6. Save and exit
   
   Enter your choice:
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

#### Step 7.2: Handle User Choice

**If user selects "Update answer":**

1. **Prompt for question number:**
   ```
   Which question would you like to update? (1-N):
   ```

2. **Get question details** from definitions/questions.yaml

3. **Show current answer and options:**
   ```
   Question: [question_text]
   Current Answer: [current value]
   
   [Display guidance from question definition]
   
   [For multi-select: show numbered options]
   [For list: show current items, prompt to add/remove]
   [For text: prompt for new value]
   
   Enter your new answer (or 'cancel' to keep current):
   ```

4. **Update answer file:**
   - Modify the YAML file with new value
   - Save immediately

5. **Confirm update:**
   ```
   ✓ Updated [answer_title] to: [new value]
   ```

6. **Return to step menu** (Step 7.1)

**If user selects "Continue to next step":**
- Increment step counter
- Return to Step 7.1 with next step

**If user selects "Go back to previous step":**
- Decrement step counter
- Return to Step 7.1 with previous step

**If user selects "Jump to specific step":**
- Show list of all steps
- Let user select step number
- Return to Step 7.1 with selected step

**If user selects "Generate infrastructure code and exit":**
- Proceed to Step 9 (Generate IaC)

**If user selects "Save and exit":**
- Confirm save
- End workflow

### Handling Navigation and Progress Questions During Walkthrough

During any point in the walkthrough (Step 7), users may ask navigation and progress questions. Answer these using the `meta.yaml` task structure already loaded in this phase.

**How to derive navigation info from `meta.yaml`:**

The `tasks` list in `meta.yaml` contains the full structure: each task has a `title`, `summary`, and `steps` list. The current step's position in this structure tells you everything:
- **Parent task:** find which task's `steps` list contains the current step slug
- **Remaining steps:** all steps after the current one in that task's list
- **Progress:** count completed steps (those with answers) vs. total steps across all tasks

#### Responding to "What's next?" queries

When a user asks "what's next?", "what comes after this?", or similar:

1. Find the current step in `meta.yaml`'s task structure
2. List remaining steps in the current task
3. Present the response:

```
**Current Task:** [Task Title]

**Next steps in this task:**
1. [Next step title]
2. [Following step title]
...

[If no remaining steps in current task, check if there are more tasks:]

You've completed all steps in "[Task Title]". 
The next task is "[Next Task Title]": [Next task summary]
```

#### Responding to "How much is left?" / Progress queries

When a user asks "how much is left?", "what's my progress?", "how far along am I?", or similar:

1. Count completed steps (those with non-null answers) vs. total steps
2. Present the response:

```
**Current Task:** [Task Title] — [completed_steps_in_task]/[total_steps_in_task] steps ([percentage]%)

**Overall Blueprint Progress:** [completed_steps]/[total_steps] steps ([percentage]%)
  - Completed tasks: [completed_tasks]/[total_tasks]
```

#### Context Recovery (Returning Users)

When a user returns to an in-progress blueprint (e.g., they resume a previous session or say "where was I?"):

**Verbosity:** Apply the rendering profile based on the user's experience level — see "Context Recovery Verbosity" in the "Experience-Level Rendering Profiles" section above.

1. Identify the current step from the answer file (the last step with answers provided, or the first step with null/missing answers)
2. Find the parent task in `meta.yaml`'s task structure
3. Calculate progress (completed steps vs. total)
4. Load the task overview for the current task: `read blueprints/<blueprint_slug>/tasks/<task_slug>.md`
5. Present a recovery summary that includes the current task's overview context:

```
**Welcome back! Here's where you left off:**

======================================================================
 Current Task [N] of [Total]: [Task Title]
======================================================================

## What You Will Accomplish
[Task summary from the task's `summary` field]

## Prerequisites

**Snowflake Role Requirements:**
- [role_requirement_1]
- [role_requirement_2]

**External Requirements:**
- [external_requirement_1]
- [external_requirement_2]

## Who Should Be Involved
- [persona_1]
- [persona_2]

---

**Current Step:** Step [N of M]: [Step Title]

**Task Progress:** [completed_steps_in_task]/[total_steps_in_task] steps complete ([percentage]%)

**Remaining steps in this task:**
1. [Remaining step title]
2. [Remaining step title]
...

---

**Previously Completed Tasks:**
- Task 1: [Task Title] — [summary] (all [N] steps complete)
- Task 2: [Task Title] — [summary] (all [N] steps complete)
[List all tasks before the current one that are fully completed]

**Overall Blueprint Progress:** [completed_steps]/[total_steps] steps ([percentage]%)

Would you like to continue from here, or jump to a different step?
```

**Rules for context recovery:**
- **Always show the current task's overview** (summary, prerequisites, personas) so the user understands the context of where they are
- **List previously completed tasks** with a brief summary of each, so the user can recall what was already done. Use the `summary` field from each completed task.
- **Show remaining steps** in the current task by listing all steps after the current one in that task's `steps` list in `meta.yaml`
- **Omit prerequisite sections** (role requirements, external requirements, personas) if they are empty for the current task
- If the user is on the very first step of the very first task, skip the "Previously Completed Tasks" section

#### Task Boundary Transitions

When the user completes the last step in a task (the current step is the final step in its task), proactively inform them about the transition:

**Verbosity:** Apply the rendering profile based on the user's experience level — see "Task Boundary Transitions Verbosity" in the "Experience-Level Rendering Profiles" section above.

1. In `meta.yaml`'s task structure, check if the current step is the last entry in its task's `steps` list
2. Calculate blueprint-level progress (completed tasks vs. total tasks)
3. Present the transition:

```
**Task Complete: [Current Task Title]**

You've finished all [N] steps in this task.

**Up Next — Task [M]: [Next Task Title]**
[Next task summary]

**Prerequisites:**
- Personas: [personas]
- Role Requirements: [role_requirements]
- External Requirements: [external_requirements]

**Overall Progress:** [completed_tasks]/[total_tasks] tasks complete

Ready to continue to the next task?
```

#### Question Grouping by Task for Persona/Role Routing

When presenting questions during a walkthrough (Step 7) or summary (Step 6), group questions by their parent task's `personas` field to enable organizational routing. This helps users identify which teams or individuals should review specific answers.

**How to apply persona-based grouping:**

1. **At the start of each task's questions**, announce the personas involved:

   ```
   ## Questions for Task [N]: [Task Title]

   **Reviewers:** The following questions are for your [Persona 1] and [Persona 2] to review.
   ```

   For example:
   ```
   ## Questions for Task 2: Account Security & Identity

   **Reviewers:** The following questions are for your Security Administrator and Network Team to review.
   ```

2. **When presenting the configuration summary (Step 6)**, group answers by task and annotate each group with the relevant personas:

   ```
   ### Task 1: Platform Foundation (Reviewers: Platform Administrator, Cloud/Infrastructure Team)

   - [Question name]: [Answer] — Reasoning: [why]
   - [Question name]: [Answer] — Reasoning: [why]

   ### Task 2: Platform Security & Identity (Reviewers: Security Administrator, Identity Team)

   - [Question name]: [Answer] — Reasoning: [why]
   - [Question name]: [Answer] — Reasoning: [why]

   ### Task 3: Platform Cost Management (Reviewers: FinOps Team, Finance Team)

   - [Question name]: [Answer] — Reasoning: [why]
   ```

3. **When multiple personas share a task**, list all of them. The user can then forward the relevant section to each team for review.

4. **When a task has no personas defined**, omit the reviewer annotation and present questions without grouping metadata.

5. **For step-by-step mode (Step 7)**, apply grouping at task boundaries:
   - When entering a new task, display the persona annotation (as part of the Step 7.0 task overview)
   - Questions within the same task inherit the task's persona context
   - When transitioning between tasks, clearly indicate the change in reviewer context

**Why this matters:** Different parts of a blueprint require input from different teams. A security task needs review by the Security Administrator, while a cost management task needs review by FinOps. Grouping by persona enables users to efficiently route configuration decisions to the right people, rather than requiring every reviewer to read the entire blueprint.

### Step 8: Fill In Required Values

**Goal:** Help user provide values that only they can supply (account names, emails, etc.)

**Actions:**

1. **Parse answer file** for questions marked as ❓ USER INPUT REQUIRED (null values that need user-specific information)

2. **Present required values list:**
   ```
   ======================================================================
    Values Only You Can Provide
   ======================================================================
   
   These questions require information specific to your organization:
   
   1. **primary_account_name** (currently: empty)
      What's needed: Your Snowflake account name
      How to find it: Run `SELECT CURRENT_ACCOUNT_NAME();` in Snowflake
   
   2. **org_name** (currently: empty)
      What's needed: Your company/organization name
   
   3. **accountadmin_users** (currently: empty)
      What's needed: Email addresses for Snowflake admin users
      Format: List of email addresses
   
   ...
   
   Which value would you like to provide? (1-N, 'all' for guided, 'skip' to continue):
   ```

3. **For each selected value:**
   - Show what information is needed
   - Provide guidance on how to find it
   - Prompt for the actual value
   - Validate format if applicable
   - Update answer file
   - Confirm update

4. **After updates, show progress:**
   ```
   ✅ Updated values:
   - primary_account_name: ACME_CORP_PROD
   - org_name: Acme Corporation
   
   Remaining required values: [N]
   
   Would you like to:
   1. Continue filling in required values
   2. Provide more context for unanswered questions
   3. Review configuration step-by-step
   4. Generate infrastructure code (SQL) and exit
   5. Save and exit
   
   Enter your choice:
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

**Route based on selection:**
- Option 1 → Continue in Step 8
- Option 2 → Ask follow-up questions for ⚠️ INSUFFICIENT CONTEXT items
- Option 3 → Return to Step 7 (Walkthrough)
- Option 4 → Proceed to Step 9 (Generate IaC)
- Option 5 → End workflow

### Step 9: Generate Infrastructure Code

**Goal:** Run the render_journey.py script to generate SQL infrastructure code

**⚠️ CRITICAL REMINDER: You MUST use `scripts/render_journey.py` for ALL code generation. NEVER generate SQL manually or use ad-hoc logic. This applies even if the user asks to "just show me" or "preview" the SQL.**

**Actions:**

1. **Present generation options:**
   ```
   ======================================================================
    Generate Infrastructure Code
   ======================================================================
   
   Your answer file: [answer_file_path]
   Workflow: [workflow_name]
   
   I can generate the SQL infrastructure code for you now.
   
   Options:
   1. Generate SQL now (I'll run the script)
   2. Show me the command to run manually
   3. Go back (don't generate yet)
   
   Enter your choice:
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

**If user selects "Generate SQL now":**

1. **Run the migration script** to ensure the answer file is compatible with the current schema before rendering:
   ```bash
   python3 scripts/migration/migrate_answers.py [answer_file_path] --dry-run
   ```
   - If the dry-run reports changes, apply them:
     ```bash
     python3 scripts/migration/migrate_answers.py [answer_file_path]
     ```
   - If the script reports errors or the file cannot be parsed, direct the user to `scripts/TROUBLESHOOTING.md` for resolution before continuing.
   - If no changes are needed, proceed immediately.

2. **Run render script with project flag:**
   ```bash
   python3 scripts/render_journey.py \
     [answer_file_path] \
     --blueprint [blueprint_slug] \
     --lang sql \
     --project [project_name]
   ```

3. **Check for output file:**
   ```bash
   ls -lt projects/[project_name]/output/iac/sql/ | head -5
   ```

4. **Present results:**
   ```
   ✓ SQL infrastructure code generated successfully!
   
   Output file: projects/[project_name]/output/iac/sql/[workflow_id]_[timestamp].sql
   
   Next Steps:
   1. Review the generated SQL file
   2. Connect to your Snowflake account
   3. Execute the SQL in your Snowflake worksheet
   4. Verify the infrastructure was created correctly
   
   Note: The SQL is idempotent - you can run it multiple times safely.
   ```

**If user selects "Show me the command":**

1. **Display command:**
   ```
   Before rendering, ensure your answer file is compatible with the current schema:

   ```bash
   python3 scripts/migration/migrate_answers.py [answer_file_path] --dry-run
   # If changes are reported, apply them:
   python3 scripts/migration/migrate_answers.py [answer_file_path]
   ```

   Then run this command to generate your infrastructure code:
   
   ```bash
   python3 scripts/render_journey.py \
     [answer_file_path] \
     --blueprint [blueprint_slug] \
     --lang sql \
     --project [project_name]
   ```
   
   Output will be saved to: projects/[project_name]/output/iac/sql/[blueprint_slug]_[timestamp].sql
   ```

**If user selects "Go back":**
- Return to Step 6 (Summary and offer walkthrough)

**Output:** Generated SQL file or command instructions

### Step 10: Final Summary

**Goal:** Provide final summary and close the workflow

**Actions:**

1. **Present final summary:**
   ```
   ======================================================================
    Landing Zone Configuration Complete
   ======================================================================
   
   Answer File: [answer_file_path]
   SQL Output: [sql_file_path] (if generated)
   
   Summary:
   - Workflow: [workflow_name]
   - Questions answered: [N]
   - Configuration approach: [summary based on user context]
   
   What was configured:
   - Account strategy: [summary]
   - Security & compliance: [summary]
   - Cost controls: [summary]
   - Data structure: [summary]
   
   Next Steps:
   1. Execute the SQL file in your Snowflake account
   2. Verify all objects were created successfully
   3. Test access with your admin users
   4. Configure any additional settings as needed
   
   For additional data products, run the "New Data Product" workflow.
   ```

**Output:** Workflow complete

## Answer File Format

The generated answer file follows this structure:

```yaml
# Platform Foundation Setup - Answer File
# Created: YYYY-MM-DD
# Blueprint ID: blueprint_id
# Organization: [user context summary]

# ============================================================================
# STEP N: Step Name
# ============================================================================

# ✅ AUTO-ANSWERED: Question Text
answer_title_1: Answer value 1  # Reasoning: why this was chosen based on user context

# ✅ AUTO-ANSWERED: Question Text  
account_strategy: Single Account  # Reasoning: user mentioned "small startup with 5 users"

# ❓ USER INPUT REQUIRED: Question Text
# What's needed: Your Snowflake account name
# How to find: Run SELECT CURRENT_ACCOUNT_NAME(); in Snowflake
primary_account_name: null

# ❓ USER INPUT REQUIRED: Question Text
# What's needed: Email addresses for admin users
accountadmin_users: null

# ⚠️ INSUFFICIENT CONTEXT: Question Text
# Missing: User didn't specify number of data domains or team structure
# Please provide: List of data domains/business units that will have separate databases
domain_list: null

# ✅ AUTO-ANSWERED: Question Text
enable_feature: 'Yes'  # Reasoning: user mentioned SOC2 compliance requirement
```

**Key points:**
- Use `answer_title` as the key (not question_text)
- Group by workflow step with section headers
- **Mark answer status clearly** with prefixes: ✅ AUTO-ANSWERED, ❓ USER INPUT REQUIRED, ⚠️ INSUFFICIENT CONTEXT
- Add inline comments explaining reasoning for answered questions
- Store multi-select as the selected option text (string)
- Store list as YAML list with `-` items
- Store text as string (quote if contains special characters)
- **Leave unanswered questions as `null`** — do NOT use placeholder values
- **Explain what's needed** for each unanswered question

## Best Practices

**When collecting user context (Step 3):**

1. ✅ **Request open-ended description** that allows users to share in their own words
2. ✅ **Provide topic suggestions** not prescriptive questions
3. ✅ **Include examples** in topic suggestions to guide users
4. ✅ **Accept flexible descriptions** and interpret intelligently
5. ✅ **Confirm understanding** before generating answers

**When generating answers (Step 4):**

1. ✅ **Be honest about uncertainty** — only answer questions where user context provides clear guidance
2. ✅ **Never fabricate values** — do NOT generate fake placeholders like `YOUR_ACCOUNT_NAME` or `user@example.com`
3. ✅ **Leave unknowns empty** — if you can't answer confidently, leave the answer as `null` rather than guessing
4. ✅ **Distinguish answer categories clearly:**
   - Auto-answered: You have enough context to decide
   - User-specific: Always requires user input (account names, emails)
   - Insufficient context: User didn't provide enough information
5. ✅ **Add reasoning comments** for every answered question explaining why
6. ✅ **Be conservative with security** — err on the side of caution
7. ✅ **Scale appropriately** — small startup ≠ enterprise needs (but only if size was mentioned)

**What NOT to do when generating answers:**

1. ❌ **Don't invent organization-specific details** — domains, team names, user lists
2. ❌ **Don't guess quantities** — user counts, budget amounts, warehouse sizes (unless explicitly stated)
3. ❌ **Don't create placeholder lists** — like `[domain1, domain2]` or `[user1@company.com]`
4. ❌ **Don't assume technical details** — IP ranges, cloud regions, compliance requirements
5. ❌ **Don't fill in just to have something** — an empty answer is better than a fake one

**During walkthrough (Step 6):**

1. ✅ **Show reasoning** explain why each answer was chosen
2. ✅ **Keep explanations concise** 1-2 sentences per answer
3. ✅ **Allow easy navigation** forward, back, jump, exit anytime
4. ✅ **Save immediately** when user updates an answer
5. ✅ **Provide context** from step overview but keep it brief
6. ✅ **Highlight unanswered questions** — make it clear what still needs input

**When presenting summary (Step 5):**

1. ✅ **Separate answered from unanswered** — don't mix them together
2. ✅ **Explain why each question wasn't answered** — missing context vs requires user input
3. ✅ **Be specific about what's needed** — "your Snowflake account name" not "fill in TODO"
4. ✅ **Give users a clear path forward** — how to provide missing information

**When generating IaC (Step 9):**

1. ✅ **ALWAYS use `render_journey.py`** — NEVER generate SQL manually or via ad-hoc logic
2. ✅ **Handle errors gracefully** provide manual command if script fails
3. ✅ **Confirm output** show where SQL file was created
4. ✅ **Give clear next steps** what to do with the SQL
5. ✅ **Warn about incomplete answers** — if many questions are unanswered, the generated code may be incomplete
6. ✅ **For previews/display requests** — run the script first, then read the output file

**What NOT to do when generating output:**

1. ❌ **NEVER write SQL directly** — even for "quick previews" or "showing what it would look like"
2. ❌ **NEVER construct SQL from answer file values** — the templates handle this correctly
3. ❌ **NEVER bypass render_journey.py** — it ensures proper template rendering and validation
4. ❌ **NEVER attempt to "explain" what the SQL would be** by writing it yourself

## Decision Logic Reference

Dynamically produce this at the initiation of the workflow based on the current state of the contents in the repository.

## Troubleshooting

**Outdated answer file — invalid option values or type mismatches:**
- This occurs when an answer file was created before the latest schema update, which changed 41 questions from `multi-select` to `single-select` and renamed options for `mfa_method`, `additional_tag_dimensions`, and `service_auth_methods`.
- **Always run the migration script before loading an existing answer file** (see Step 3 above).
- For a full explanation of what changed and manual fix instructions, refer the user to `scripts/TROUBLESHOOTING.md`.
- To migrate all answer files in the project at once:
  ```bash
  python3 scripts/migration/migrate_answers.py --all --dry-run
  python3 scripts/migration/migrate_answers.py --all
  ```

**User gives vague answers:**
- Ask clarifying follow-up questions
- Provide examples to help them choose
- Suggest defaults and ask if they seem right

**Missing question definitions:**
- Check if `definitions/questions.yaml` is up to date
- Look for typos in question IDs
- Verify workflow step references match question definitions

**Render script fails:**
- Check Python environment availability
- Verify answer file is valid YAML
- Provide manual command for user to debug
- Check for missing required answers

**User wants to change blueprint:**
- Save current progress
- Return to Step 1 to select different blueprint
- Offer to carry over relevant answers if blueprints overlap

## Output

Upon completion, this skill produces:
- An answer file at `projects/<project_name>/answers/<blueprint_slug>/answers_<timestamp>.yaml` with:
  - ✅ Auto-answered questions (where user context was sufficient)
  - ❓ User-specific questions marked as `null` with guidance on what's needed
  - ⚠️ Insufficient context questions marked as `null` with explanation of missing information
- Clear inline comments explaining reasoning for each answered question
- Explicit tracking of which questions were answered vs not answered (and why)
- Optional: Generated SQL infrastructure code at `projects/<project_name>/output/iac/sql/<blueprint_slug>_<timestamp>.sql`
- Summary showing exact breakdown: auto-answered, needs user input, needs more context
