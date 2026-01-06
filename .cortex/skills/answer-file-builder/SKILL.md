---
name: answer-file-builder
description: "Guide users through constructing answer files for Snowflake Landing Zone workflows. Use when: user wants to create or complete an answer file, configure a landing zone workflow, or understand configuration questions. Triggers: create answer file, build answers, configure workflow, landing zone setup, fill out questionnaire, set up landing zone."
---

# Answer File Builder

This skill guides users through constructing answer files for Snowflake Landing Zone workflows by first understanding their organization through an open-ended description, then intelligently generating all configuration answers, and finally offering an optional step-by-step review.

## When to Use

Invoke this skill when users:
- Want to set up a Snowflake landing zone
- Need to create or complete an answer file for a workflow
- Ask about workflow configuration
- Want to configure their Snowflake environment
- Mention setting up infrastructure or governance

## Prerequisites

1. **Repository structure exists:**
   - `workflows/` directory with workflow definitions
   - `definitions/questions.yaml` with question definitions
   - `answers/` directory for storing answer files

2. **Workflow components:**
   - Each workflow has a `meta.yaml` with workflow metadata
   - Steps have `overview.md` files with context and guidance
   - Questions are defined with types: `multi-select`, `list`, or `text`

## Workflow

### Step 1: Discover Available Workflows

**Goal:** Identify which workflows are available and which one the user wants to work with

**Actions:**

1. **List workflows** in the repository:
   ```bash
   find workflows -name "meta.yaml" -type f
   ```

2. **Read workflow metadata** for each workflow:
   - Load `workflows/<workflow_id>/meta.yaml`
   - Extract: `name`, `summary`, `overview`, `is_repeatable`, `steps`

3. **Present workflows** to user:
   ```
   Available workflows:
   
   1. [Workflow Name]
      Summary: [Brief description]
      Steps: [Number of steps]
   
   2. [Workflow Name 2]
      ...
   
   Which workflow would you like to work with?
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user to select a workflow.

**Output:** Selected workflow ID and metadata

### Step 2: Initialize or Select Answer File

**Goal:** Let user choose to create a new answer file or work with an existing one

**Actions:**

1. **Check for existing answer files:**
   ```bash
   find answers/<workflow_id> -name "*.yaml" -type f 2>/dev/null | sort -r
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
   mkdir -p answers/<workflow_id>
   ```

3. **Create initial answer file:**
   - Path: `answers/<workflow_id>/answers_<timestamp>.yaml`
   - Initialize with header comments (workflow name, date, workflow ID)

4. **Proceed to Step 3** (Collect User Context)

**If user selects "Work with an existing answer file":**

1. **List available answer files:**
   ```
   Existing answer files for this workflow:
   
   1. answers/<workflow_id>/answers_20251221214657.yaml
      Created: 2025-12-21 21:46:57
      
   2. answers/<workflow_id>/answers_20251221222441.yaml
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
   - Questions answered: [M]
   - Questions incomplete/TODO: [P]
   ```

5. **Offer next actions:**
   ```
   What would you like to do?
   
   1. Review/update configuration step-by-step
   2. Update specific TODO values
   3. View current configuration summary
   4. Generate infrastructure code (SQL)
   5. Start over with new context (will prompt for description)
   
   Enter your choice (1-5):
   ```

6. **⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

7. **Route based on selection:**
   - Option 1 → Skip to Step 6 (Interactive Walkthrough)
   - Option 2 → Skip to Step 7 (Update TODOs)
   - Option 3 → Skip to Step 5 (Present Summary)
   - Option 4 → Skip to Step 8 (Generate IaC)
   - Option 5 → Proceed to Step 3 (will regenerate all answers based on new context)

**Output:** Path to answer file (new or existing) and current state

### Step 3: Collect User Context (Open-Ended Description)

**Goal:** Request a description of the user's organization and their plans for how they will use snowflake to understand their needs well enough to intelligently fill out all workflow answers.

**Actions:**

1. **Load all question definitions:**
   ```bash
   read definitions/questions.yaml
   ```

2. **Parse questions** to understand what information is needed across the entire workflow

3. **Present open-ended request with suggested topics:**
   
   **Request Template - Adapt based on workflow:**
   
   ```
   Please provide an open-ended description of your organization to help me configure your Snowflake Landing Zone appropriately.
   
   Consider including information about the following topics in your response:
   
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
   
   Please share as much or as little detail as feels relevant. I'll use your description to make intelligent configuration decisions.
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user's open-ended response.

**Output:** User context gathered from their open-ended description

### Step 4: Generate All Workflow Answers

**Goal:** Intelligently fill out ALL workflow answers based on user's context

**Actions:**

1. **Load workflow steps:**
   - Read `workflows/<workflow_id>/meta.yaml` for step order
   - Load each step's `overview.md` to understand questions

2. **For each step, extract questions:**
   - Parse overview.md for question IDs (format: `` `answer_title` ``)
   - Look up question definitions from `questions.yaml`

3. **Apply intelligent defaults based on user context:**

   **Decision Logic Examples:**
   
   **Organization Size:**
   - Small startup → Single account, simple RBAC, minimal admins
   - Mid-size → Consider multi-account, moderate RBAC complexity
   - Enterprise → Multi-account strategy, complex RBAC, multiple admins
   
   **Use Case:**
   - Analytics/BI → Focus on warehouses for queries, reader roles
   - Data Engineering → ETL warehouses, writer/owner roles, pipelines
   - ML/Data Science → Compute-optimized warehouses, data science roles
   
   **Security Posture:**
   - Has SSO → Configure SSO/SAML, use IdP for MFA
   - No SSO → Username/password with MFA, strong password policy
   - Strict network → Specific IP ranges, service account restrictions
   - Flexible → Broader access (0.0.0.0/0 with caution notes)
   
   **Compliance:**
   - GDPR/HIPAA/SOC2 → Enable audit schemas, change tracking, data retention policies
   - None → Balanced policies, monitoring recommended but optional
   
   **Cost Control:**
   - Strict → Resource monitors with suspend, hourly budget refresh, required tags
   - Moderate → Budgets with alerts, daily refresh, recommended tags
   - Flexible → Budget tracking, no hard limits
   
   **Budget Range:**
   - Under $1K → 250 credits/month budget, small warehouses
   - $1-10K → 2,500 credits/month, moderate resources
   - $10-50K → 7,500 credits/month, production scale
   - $50K+ → Custom based on needs

4. **Write all answers to YAML file:**
   - Use `answer_title` as keys
   - Set intelligent defaults for every question
   - Add inline comments explaining reasoning
   - Mark any TODO items that require user-specific values (account names, emails, etc.)

5. **Generate answer summary:**
   ```
   Total questions: [N]
   Answered automatically: [M]
   Requires user input: [P] (marked as TODO)
   ```

**Output:** Completed answer file with intelligent defaults and TODO markers

### Step 5: Present Summary and Offer Walkthrough

**Goal:** Show user what was configured and offer detailed review

**Actions:**

1. **Present configuration summary:**
   ```
   ======================================================================
    ✓ Configuration Complete
   ======================================================================
   
   Your Snowflake Landing Zone Configuration:
   
   ### Account Strategy
   - [Summary of account decisions and reasoning]
   
   ### Users & Access
   - [Summary of admin users, authentication, security]
   
   ### Security & Compliance
   - [Summary of network policies, password policies, audit settings]
   
   ### Cost Controls
   - [Summary of budgets, resource monitors, tags]
   
   ### Data Structure
   - [Summary of domains, zones, data products, warehouses]
   
   ---
   
   ### TODO: Update These Values
   [List any values that need user input, e.g., account names, emails]
   
   ---
   
   Answer file saved: [file path]
   
   Questions answered: [N] of [Total]
   ```

2. **Offer walkthrough options:**
   ```
   What would you like to do next?
   
   1. Review configuration step-by-step (see each question, answer, and reasoning)
   2. Update specific TODO values now
   3. Generate infrastructure code (SQL) and exit
   4. Save and exit (update TODO values later)
   
   Enter your choice (1-4):
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

**Route based on selection:**
- Option 1 → Proceed to Step 6 (Walkthrough)
- Option 2 → Proceed to Step 7 (Update TODOs)
- Option 3 → Proceed to Step 8 (Generate IaC)
- Option 4 → End workflow

### Step 6: Interactive Step-by-Step Walkthrough

**Goal:** Walk through each workflow step, showing questions, answers, reasoning, and allowing updates

**For each step in workflow.steps:**

#### Step 6.1: Display Step Overview and Questions

**Actions:**

1. **Read step overview:**
   ```bash
   read workflows/<workflow_id>/<step_id>/overview.md
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

#### Step 6.2: Handle User Choice

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

6. **Return to step menu** (Step 6.1)

**If user selects "Continue to next step":**
- Increment step counter
- Return to Step 6.1 with next step

**If user selects "Go back to previous step":**
- Decrement step counter
- Return to Step 6.1 with previous step

**If user selects "Jump to specific step":**
- Show list of all steps
- Let user select step number
- Return to Step 6.1 with selected step

**If user selects "Generate infrastructure code and exit":**
- Proceed to Step 8 (Generate IaC)

**If user selects "Save and exit":**
- Confirm save
- End workflow

### Step 7: Update TODO Values

**Goal:** Help user fill in specific values that require their input

**Actions:**

1. **Parse answer file** for TODO comments and placeholder values

2. **Present TODO list:**
   ```
   ======================================================================
    Values That Need Your Input
   ======================================================================
   
   1. primary_account_name: YOUR_ACCOUNT_NAME
      Help: Run `SELECT CURRENT_ACCOUNT_NAME();` in Snowflake
   
   2. org_name: YOUR_COMPANY_NAME
      Help: Your company/organization name
   
   3. accountadmin_users: [user1@yourcompany.com, user2@yourcompany.com]
      Help: Email addresses for admin users
   
   ...
   
   Which value would you like to update? (1-N, 'all' for guided, 'skip' to continue):
   ```

3. **For each selected TODO:**
   - Show current placeholder
   - Prompt for actual value
   - Update answer file
   - Confirm update

4. **After updates:**
   ```
   Would you like to:
   1. Review configuration step-by-step
   2. Generate infrastructure code (SQL) and exit
   3. Save and exit
   
   Enter your choice:
   ```

**⚠️ MANDATORY STOPPING POINT**: Wait for user choice.

**Route based on selection:**
- Option 1 → Return to Step 6 (Walkthrough)
- Option 2 → Proceed to Step 8 (Generate IaC)
- Option 3 → End workflow

### Step 8: Generate Infrastructure Code

**Goal:** Run the render_journey.py script to generate SQL infrastructure code

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

1. **Run render script:**
   ```bash
   python scripts/render_journey.py \
     [answer_file_path] \
     --workflow [workflow_id] \
     --lang sql
   ```
   
   OR if venv exists:
   ```bash
   ./venv/bin/python scripts/render_journey.py \
     [answer_file_path] \
     --workflow [workflow_id] \
     --lang sql
   ```

2. **Check for output file:**
   ```bash
   ls -lt iac/sql/ | head -5
   ```

3. **Present results:**
   ```
   ✓ SQL infrastructure code generated successfully!
   
   Output file: iac/sql/[workflow_id]_[timestamp].sql
   
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
     --workflow [workflow_id] \
     --lang sql
   ```
   
   Or if you have a virtual environment:
   
   ```bash
   ./venv/bin/python scripts/render_journey.py \
     [answer_file_path] \
     --workflow [workflow_id] \
     --lang sql
   ```
   
   Output will be saved to: iac/sql/[workflow_id]_[timestamp].sql
   ```

**If user selects "Go back":**
- Return to Step 5 (Summary and offer walkthrough)

**Output:** Generated SQL file or command instructions

### Step 9: Final Summary

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
# Workflow ID: workflow_id
# Organization: [user context summary]

# ============================================================================
# STEP N: Step Name
# ============================================================================
# Question Text
answer_title_1: Answer value 1  # Reasoning: why this was chosen
# Question Text
answer_title_2:
- List item 1
- List item 2
# Question Text
enable_feature: 'Yes'  # Reasoning: based on user requirements
# Question Text
account_strategy: Single Account  # Reasoning: small startup, 5 users
# Question Text
domain_list:
- DOMAIN1
- DOMAIN2
```

**Key points:**
- Use `answer_title` as the key (not question_text)
- Group by workflow step with section headers
- Add inline comments explaining reasoning
- Store multi-select as the selected option text (string)
- Store list as YAML list with `-` items
- Store text as string (quote if contains special characters)
- Mark TODOs clearly for user-specific values

## Best Practices

**When collecting user context (Step 3):**

1. ✅ **Request open-ended description** that allows users to share in their own words
2. ✅ **Provide topic suggestions** not prescriptive questions
3. ✅ **Include examples** in topic suggestions to guide users
4. ✅ **Accept flexible descriptions** and interpret intelligently
5. ✅ **Confirm understanding** before generating answers

**When generating answers (Step 4):**

1. ✅ **Apply sensible defaults** based on organization size and use case
2. ✅ **Add reasoning comments** for every non-obvious choice
3. ✅ **Mark TODOs clearly** for values that need user input
4. ✅ **Be conservative with security** err on the side of caution
5. ✅ **Scale appropriately** small startup ≠ enterprise needs

**During walkthrough (Step 6):**

1. ✅ **Show reasoning** explain why each answer was chosen
2. ✅ **Keep explanations concise** 1-2 sentences per answer
3. ✅ **Allow easy navigation** forward, back, jump, exit anytime
4. ✅ **Save immediately** when user updates an answer
5. ✅ **Provide context** from step overview but keep it brief

**When generating IaC (Step 8):**

1. ✅ **Check environment** verify Python availability
2. ✅ **Handle errors gracefully** provide manual command if script fails
3. ✅ **Confirm output** show where SQL file was created
4. ✅ **Give clear next steps** what to do with the SQL

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

**User wants to change workflow:**
- Save current progress
- Return to Step 1 to select different workflow
- Offer to carry over relevant answers if workflows overlap

## Output

Upon completion, this skill produces:
- A complete answer file at `answers/<workflow_id>/answers_<timestamp>.yaml` with intelligent defaults
- Clear inline comments explaining reasoning for each answer
- TODO markers for user-specific values
- Optional: Generated SQL infrastructure code at `iac/sql/<workflow_id>_<timestamp>.sql`
- Summary of configuration decisions and next steps
