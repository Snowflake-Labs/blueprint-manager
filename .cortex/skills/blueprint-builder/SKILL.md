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
  --blueprint [blueprint_id] \
  --lang sql \
  --project [project_name]
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
   - Questions are defined with types: `multi-select`, `list`, or `text`

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
- Proceed to Step 2 (Discover Available Blueprints)

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

6. **Proceed to Step 2** (Discover Available Blueprints)

**Output:** Selected or created project name

### Step 2: Discover Available Blueprints

**Goal:** Identify which blueprints are available and which one the user wants to work with

**Actions:**

1. **List blueprints** in the repository:
   ```bash
   find blueprints -name "meta.yaml" -type f
   ```

2. **Read blueprint metadata** for each blueprint:
   - Load `blueprints/<blueprint_id>/meta.yaml`
   - Extract: `name`, `summary`, `overview`, `is_repeatable`, `steps`

3. **Present blueprints** to user:
   ```
   Available blueprints:
   
   1. [Blueprint Name]
      Summary: [Brief description]
      Steps: [Number of steps]
   
   2. [Blueprint Name 2]
      ...
   
   Which blueprint would you like to work with?
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user to select a blueprint.

**Output:** Selected blueprint ID and metadata

### Step 3: Initialize or Select Answer File

**Goal:** Let user choose to create a new answer file or work with an existing one

**Actions:**

1. **Check for existing answer files in the project:**
   ```bash
   find projects/<project_name>/answers/<blueprint_id> -name "*.yaml" -type f 2>/dev/null | sort -r
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
   mkdir -p projects/<project_name>/answers/<blueprint_id>
   ```

3. **Create initial answer file:**
   - Path: `projects/<project_name>/answers/<blueprint_id>/answers_<timestamp>.yaml`
   - Initialize with header comments (project name, blueprint name, date, blueprint ID)

4. **Proceed to Step 4** (Collect User Context)

**If user selects "Work with an existing answer file":**

1. **List available answer files:**
   ```
   Existing answer files for this project and blueprint:
   
   1. projects/<project_name>/answers/<blueprint_id>/answers_20251221214657.yaml
      Created: 2025-12-21 21:46:57
      
   2. projects/<project_name>/answers/<blueprint_id>/answers_20251221222441.yaml
      Created: 2025-12-21 22:24:41
   
   Which file would you like to work with? (1-N):
   ```

2. **⚠️ MANDATORY STOPPING POINT**: Wait for user to select a file.

3. **Load selected answer file:**
   - Read the YAML file
   - Parse existing answers
   - Validate structure

4. **Present current state:**
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

3. **Present open-ended request with suggested topics AND step-by-step option:**
   
   **Request Template - Adapt based on workflow:**
   
   ```
   I can help you configure your Snowflake Blueprint in one of two ways:
   
   ---
   
   **Option A: Provide a Description (Recommended)**
   
   Share an open-ended description of your organization, and I'll intelligently 
   configure as many settings as possible based on what you tell me.
   
   Consider including information about:
   
   **Organization Profile**
   - Organization size (small startup, mid-size, large enterprise)
   - Primary Snowflake use case (analytics, data engineering, ML, application, multiple)
   - Number of users/teams that will use Snowflake
   
   **Security & Compliance**
   - Existing SSO/identity provider (Okta, Azure AD, none, other)
   - Compliance requirements (SOC2, HIPAA, GDPR, PCI-DSS, none)
   - Network access controls (strict corporate only, VPN, cloud services, flexible)
   
   **Cost & Scale**
   - Expected monthly budget/usage (under $1K, $1-10K, $10-50K, $50K+, unknown)
   - Cost control level (strict - prevent overruns, moderate - alerts, flexible - track only)
   - Deployment approach (start small/dev, straight to production, phased rollout)
   
   **Technical Environment** (if applicable)
   - Cloud provider preference (AWS, Azure, GCP, multi-cloud)
   - Existing data sources (databases, cloud storage, APIs, streaming)
   - Data governance maturity (just starting, have some policies, mature governance)
   
   **Organizational Structure** (if applicable for complex workflows)
   - Team structure (centralized data team, distributed, hybrid)
   - Data product approach (single product, multiple domains, not sure yet)
   
   Share as much or as little as feels relevant.
   
   ---
   
   **Option B: Step-by-Step Walkthrough**
   
   If you prefer, I can walk you through each question one at a time, 
   explaining each option as we go. This takes longer but gives you 
   full control over every decision.
   
   ---
   
   **How would you like to proceed?**
   
   - Type your organization description to use Option A
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
   - Read `blueprints/<blueprint_id>/meta.yaml` for step order
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

#### Step 7.1: Display Step Overview and Questions

**Actions:**

1. **Read step overview:**
   ```bash
   read blueprints/<blueprint_id>/<step_id>/overview.md
   ```

2. **Extract questions for this step** (parse overview.md for question IDs)

3. **Load question details** from definitions/questions.yaml for all questions in this step

4. **Present step information:**
   ```
   ======================================================================
    Step [N] of [Total]: [Step Name]
   ======================================================================
   
   ## Step Overview
   
   [Full content from overview.md - ALL paragraphs and details]
   
   ---
   
   ## Configuration Questions and Answers
   
   ### Question 1: [question_text]
   
   **Answer:** [your answer]
   
   **Reasoning:** [why this answer was chosen based on user context]
   
   **Question Details:**
   - **Type:** [answer_type: multi-select, list, or text]
   - **Guidance:** 
     [Full guidance text from definitions - all paragraphs and formatting]
   [For multi-select questions:]
   - **Available Options:**
     1. [option 1 text]
     2. [option 2 text]
     ...
   
   ---
   
   ### Question 2: [question_text]
   
   **Answer:** [your answer]
   
   **Reasoning:** [why this answer was chosen based on user context]
   
   **Question Details:**
   - **Type:** [answer_type]
   - **Guidance:**
     [Full guidance text from definitions - all paragraphs and formatting]
   [For multi-select questions:]
   - **Available Options:**
     1. [option 1 text]
     2. [option 2 text]
     ...
   
   ---
   
   [Continue for all questions in this step...]
   
   ---
   ```

5. **Present step menu:**
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

1. **Check if Python environment is available:**
   ```bash
   which python3
   ls -la venv/bin/python
   ```

2. **Present generation options:**
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

1. **Run render script with project flag:**
   ```bash
   python scripts/render_journey.py \
     [answer_file_path] \
     --blueprint [blueprint_id] \
     --lang sql \
     --project [project_name]
   ```
   
   OR if venv exists:
   ```bash
   ./venv/bin/python scripts/render_journey.py \
     [answer_file_path] \
     --blueprint [blueprint_id] \
     --lang sql \
     --project [project_name]
   ```

2. **Check for output file:**
   ```bash
   ls -lt projects/[project_name]/output/iac/sql/ | head -5
   ```

3. **Present results:**
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
   Run this command to generate your infrastructure code:
   
   ```bash
   python scripts/render_journey.py \
     [answer_file_path] \
     --blueprint [blueprint_id] \
     --lang sql \
     --project [project_name]
   ```
   
   Or if you have a virtual environment:
   
   ```bash
   ./venv/bin/python scripts/render_journey.py \
     [answer_file_path] \
     --blueprint [blueprint_id] \
     --lang sql \
     --project [project_name]
   ```
   
   Output will be saved to: projects/[project_name]/output/iac/sql/[blueprint_id]_[timestamp].sql
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
2. ✅ **Check environment** verify Python availability
3. ✅ **Handle errors gracefully** provide manual command if script fails
4. ✅ **Confirm output** show where SQL file was created
5. ✅ **Give clear next steps** what to do with the SQL
6. ✅ **Warn about incomplete answers** — if many questions are unanswered, the generated code may be incomplete
7. ✅ **For previews/display requests** — run the script first, then read the output file

**What NOT to do when generating output:**

1. ❌ **NEVER write SQL directly** — even for "quick previews" or "showing what it would look like"
2. ❌ **NEVER construct SQL from answer file values** — the templates handle this correctly
3. ❌ **NEVER bypass render_journey.py** — it ensures proper template rendering and validation
4. ❌ **NEVER attempt to "explain" what the SQL would be** by writing it yourself

## Decision Logic Reference

Dynamically produce this at the initiation of the workflow based on the current state of the contents in the repository.

## Troubleshooting

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
- An answer file at `projects/<project_name>/answers/<blueprint_id>/answers_<timestamp>.yaml` with:
  - ✅ Auto-answered questions (where user context was sufficient)
  - ❓ User-specific questions marked as `null` with guidance on what's needed
  - ⚠️ Insufficient context questions marked as `null` with explanation of missing information
- Clear inline comments explaining reasoning for each answered question
- Explicit tracking of which questions were answered vs not answered (and why)
- Optional: Generated SQL infrastructure code at `projects/<project_name>/output/iac/sql/<blueprint_id>_<timestamp>.sql`
- Summary showing exact breakdown: auto-answered, needs user input, needs more context
