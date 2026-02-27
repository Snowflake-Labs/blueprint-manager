#!/usr/bin/env python3

# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License. See LICENSE file.

"""
render_journey.py

Generates consolidated IaC and guidance files based on a blueprint and an answers file.
This script renders all code templates and overview documents from steps within a blueprint,
concatenating them in order into output files.

Only steps where ALL required variables are provided in the answers file will be rendered.
Steps with missing variables are skipped entirely.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
    from jinja2 import (
        Environment,
        FileSystemLoader,
        StrictUndefined,
        TemplateError,
        UndefinedError,
    )
except ImportError as e:
    sys.stderr.write(f"Error: Required library not found: {e}\n")
    sys.stderr.write("Please install dependencies: pip install pyyaml jinja2\n")
    sys.exit(1)


class NullTracker:
    """
    Marker class to track null values that are actually accessed during template rendering.

    Wraps variables whose answer value is None so that Jinja2's StrictUndefined mode
    can distinguish between "missing" and "null" variables at render time.

    Note: {% if var is none %} won't work correctly because NullTracker is not
    actually None. Templates should use {% if var == None %} or other patterns.
    """

    def __init__(self, var_name):
        self.var_name = var_name

    def __str__(self):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __repr__(self):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __bool__(self):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __iter__(self):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __len__(self):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __getattr__(self, name):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __getitem__(self, key):
        raise UndefinedError(f"'{self.var_name}' is null")

    # Allow equality comparisons for conditional checks like {% if var == "value" %}
    def __eq__(self, other):
        # If comparing None/null with something, return appropriate result
        return other is None

    def __ne__(self, other):
        return other is not None

    def __lt__(self, other):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __gt__(self, other):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __le__(self, other):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __ge__(self, other):
        raise UndefinedError(f"'{self.var_name}' is null")

    def __hash__(self):
        # Explicitly make NullTracker unhashable (consistent with __eq__ override)
        raise TypeError(f"unhashable type: 'NullTracker'")


DEFAULT_PROJECT_NAME = "default-project"


def classify_missing_vars(missing_vars, answers):
    """
    Split a list of problematic variable names into those missing from answers
    entirely and those present but set to None.

    Returns:
        Tuple of (missing_only, null_only) lists.
    """
    null_only = [v for v in missing_vars if v in answers and answers[v] is None]
    missing_only = [v for v in missing_vars if v not in answers]
    return missing_only, null_only


def load_yaml(file_path):
    """Load and parse a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_step_slug(step):
    """Extract the slug from a step that may be a dict or a plain string."""
    return step.get("slug", "") if isinstance(step, dict) else step


def _find_step_location(step_slug, tasks):
    """
    Find the task and step indices for a given step slug.

    Returns:
        Tuple of (task_index, step_index) or (None, None) if not found.
    """
    for task_index, task in enumerate(tasks):
        for step_index, step in enumerate(task.get("steps", [])):
            if get_step_slug(step) == step_slug:
                return task_index, step_index
    return None, None


def load_task_metadata(blueprint_meta):
    """
    Extract and normalize task metadata from a parsed meta.yaml dict.
    
    Parses the 'tasks' array from the provided dict and returns structured task
    information including slug, title, summary, external_requirements, personas,
    role_requirements, and the list of steps associated with each task.
    
    Args:
        blueprint_meta: Parsed meta.yaml dictionary (or a Path for backward compatibility)
        
    Returns:
        List of task metadata dictionaries, or empty list if no tasks defined.
        Each task dict contains:
        - slug: Task identifier
        - title: Human-readable task title
        - summary: Brief description of what the task accomplishes
        - external_requirements: List of external dependencies
        - personas: List of personas/roles involved
        - role_requirements: List of required Snowflake roles
        - steps: List of step dicts with 'slug' and 'title'
    """
    # Backward compatibility: if a Path is passed, load meta.yaml from it
    if isinstance(blueprint_meta, Path):
        meta_file = blueprint_meta / "meta.yaml"
        if not meta_file.exists():
            return []
        try:
            blueprint_meta = load_yaml(meta_file)
        except (yaml.YAMLError, OSError) as e:
            sys.stderr.write(f"Warning: Error loading task metadata from {meta_file}: {e}\n")
            return []

    if blueprint_meta is None:
        return []
    if not isinstance(blueprint_meta, dict):
        return []
    
    try:
        tasks = blueprint_meta.get("tasks", [])
        if not tasks:
            return []
        if not isinstance(tasks, list):
            return []
        
        # Normalize task structure with defaults for optional fields
        normalized_tasks = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            
            normalized_task = {
                "slug": task.get("slug", ""),
                "title": task.get("title", ""),
                "summary": task.get("summary", ""),
                "external_requirements": task.get("external_requirements", []),
                "personas": task.get("personas", []),
                "role_requirements": task.get("role_requirements", []),
                "steps": task.get("steps", []),
            }
            
            # Normalize steps within task
            normalized_steps = []
            for step in normalized_task["steps"]:
                if isinstance(step, dict):
                    normalized_steps.append({
                        "slug": step.get("slug", ""),
                        "title": step.get("title", ""),
                    })
                elif isinstance(step, str):
                    # Handle case where step is just a string slug
                    normalized_steps.append({
                        "slug": step,
                        "title": "",
                    })
            normalized_task["steps"] = normalized_steps
            
            if normalized_task["slug"]:  # Only add tasks with valid slugs
                normalized_tasks.append(normalized_task)
        
        return normalized_tasks
    except (yaml.YAMLError, OSError) as e:
        sys.stderr.write(f"Warning: Error processing task metadata: {e}\n")
        return []


def load_task_overview(blueprint_dir, task_slug):
    """
    Load task overview content from a markdown file.
    
    Reads the content from tasks/<task-slug>.md within the blueprint directory.
    Uses flat directory structure as per design requirements.
    
    Args:
        blueprint_dir: Path to the blueprint directory
        task_slug: The task slug/identifier (e.g., 'platform-foundation')
        
    Returns:
        String containing the markdown content, or None if file doesn't exist.
    """
    tasks_dir = blueprint_dir / "tasks"
    task_file = tasks_dir / f"{task_slug}.md"
    
    if not task_file.exists():
        return None
    
    try:
        with open(task_file, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write(f"Warning: Error reading task overview {task_file}: {e}\n")
        return None


def build_task_step_mapping(tasks):
    """
    Build a mapping from step slugs to their parent task information.
    
    Creates a dictionary that allows looking up which task a step belongs to,
    enabling progress tracking queries like "what's next?" and "how much is left?".
    
    Args:
        tasks: List of task metadata dictionaries (from load_task_metadata)
        
    Returns:
        Dictionary mapping step slugs to task context:
        {
            "step-slug": {
                "task_slug": "parent-task-slug",
                "task_title": "Parent Task Title",
                "task_index": 0,  # 0-based index of parent task
                "step_index": 0,  # 0-based index within the task
                "total_steps_in_task": 5,
            },
            ...
        }
    """
    step_mapping = {}
    
    for task_index, task in enumerate(tasks):
        task_slug = task.get("slug", "")
        task_title = task.get("title", "")
        task_steps = task.get("steps", [])
        total_steps = len(task_steps)
        
        for step_index, step in enumerate(task_steps):
            step_slug = get_step_slug(step)
            if step_slug:
                step_mapping[step_slug] = {
                    "task_slug": task_slug,
                    "task_title": task_title,
                    "task_index": task_index,
                    "step_index": step_index,
                    "total_steps_in_task": total_steps,
                }
    
    return step_mapping


def get_progress_info(step_slug, step_mapping, total_tasks):
    """
    Get progress information for a given step.
    
    Returns information about where the step is in the overall workflow,
    useful for answering "what's next?" and "how much is left?" queries.
    
    Args:
        step_slug: The step identifier
        step_mapping: Dictionary from build_task_step_mapping
        total_tasks: Total number of tasks in the blueprint
        
    Returns:
        Dictionary with progress info, or None if step not found:
        {
            "task_slug": "current-task",
            "task_title": "Current Task Title",
            "task_number": 1,  # 1-based task number
            "total_tasks": 3,
            "step_number": 2,  # 1-based step number within task
            "total_steps_in_task": 5,
            "is_last_step_in_task": False,
            "is_last_task": False,
        }
    """
    if step_slug not in step_mapping:
        return None
    
    info = step_mapping[step_slug]
    return {
        "task_slug": info["task_slug"],
        "task_title": info["task_title"],
        "task_number": info["task_index"] + 1,
        "total_tasks": total_tasks,
        "step_number": info["step_index"] + 1,
        "total_steps_in_task": info["total_steps_in_task"],
        "is_last_step_in_task": info["step_index"] == info["total_steps_in_task"] - 1,
        "is_last_task": info["task_index"] == total_tasks - 1,
    }


def get_current_task(step_slug, tasks):
    """
    Determine which task a given step belongs to.

    Maps a step identifier back to its parent task, returning the full task
    metadata including summary, personas, role requirements, and step list.

    Args:
        step_slug: The step identifier (e.g., 'configure-scim-integration')
        tasks: List of task metadata dictionaries (from load_task_metadata)

    Returns:
        Dictionary with parent task metadata, or None if step not found:
        {
            "slug": "parent-task-slug",
            "title": "Parent Task Title",
            "summary": "Brief description...",
            "task_index": 0,  # 0-based index
            "external_requirements": [...],
            "personas": [...],
            "role_requirements": [...],
            "steps": [{"slug": "...", "title": "..."}, ...],
        }
    """
    task_index, _ = _find_step_location(step_slug, tasks)
    if task_index is None:
        return None
    task = tasks[task_index]
    return {
        "slug": task.get("slug", ""),
        "title": task.get("title", ""),
        "summary": task.get("summary", ""),
        "task_index": task_index,
        "external_requirements": task.get("external_requirements", []),
        "personas": task.get("personas", []),
        "role_requirements": task.get("role_requirements", []),
        "steps": task.get("steps", []),
    }


def get_remaining_steps(step_slug, tasks):
    """
    List the remaining steps within the current task after the given step.

    Respects task boundaries — only returns steps within the same task,
    not steps from subsequent tasks.

    Args:
        step_slug: The current step identifier
        tasks: List of task metadata dictionaries (from load_task_metadata)

    Returns:
        List of remaining step dicts (after the current step, within the same task),
        or empty list if step not found or it is the last step in the task.
        Each dict contains:
        {
            "slug": "step-slug",
            "title": "Step Title",
            "step_index": 3,  # 0-based index within the task
        }
    """
    task_index, step_index = _find_step_location(step_slug, tasks)
    if task_index is None:
        return []
    task_steps = tasks[task_index].get("steps", [])
    remaining = []
    for j in range(step_index + 1, len(task_steps)):
        s = task_steps[j]
        remaining.append({
            "slug": get_step_slug(s),
            "title": s.get("title", "") if isinstance(s, dict) else "",
            "step_index": j,
        })
    return remaining


def get_task_progress(step_slug, tasks):
    """
    Report task-level and blueprint-level completion based on the current step.

    Computes how far through the current task and overall blueprint the user is,
    treating all steps up to and including the current step as completed.

    Args:
        step_slug: The current step identifier
        tasks: List of task metadata dictionaries (from load_task_metadata)

    Returns:
        Dictionary with progress information, or None if step not found:
        {
            "current_task": {
                "slug": "task-slug",
                "title": "Task Title",
                "task_index": 0,
                "completed_steps": 2,
                "total_steps": 5,
                "completion_percentage": 40.0,
            },
            "blueprint": {
                "completed_tasks": 1,  # tasks fully before the current one
                "total_tasks": 3,
                "completed_steps": 9,  # all steps up to and including current
                "total_steps": 21,
                "completion_percentage": 42.9,
            },
        }
    """
    # Find which task and step index the current step is in
    found_task_index, found_step_index = _find_step_location(step_slug, tasks)

    if found_task_index is None:
        return None

    current_task = tasks[found_task_index]
    current_task_steps = current_task.get("steps", [])
    total_steps_in_task = len(current_task_steps)
    completed_in_task = found_step_index + 1  # current step counts as completed

    # Blueprint-level progress
    total_tasks = len(tasks)
    total_steps_all = sum(len(t.get("steps", [])) for t in tasks)

    # Steps completed across all tasks: all steps in prior tasks + completed in current
    completed_steps_all = 0
    for i in range(found_task_index):
        completed_steps_all += len(tasks[i].get("steps", []))
    completed_steps_all += completed_in_task

    # Fully completed tasks = all tasks before the current one + current if all its steps are done
    completed_tasks = found_task_index
    if completed_in_task == total_steps_in_task:
        completed_tasks += 1

    task_pct = round((completed_in_task / total_steps_in_task) * 100, 1) if total_steps_in_task > 0 else 0.0
    blueprint_pct = round((completed_steps_all / total_steps_all) * 100, 1) if total_steps_all > 0 else 0.0

    return {
        "current_task": {
            "slug": current_task.get("slug", ""),
            "title": current_task.get("title", ""),
            "task_index": found_task_index,
            "completed_steps": completed_in_task,
            "total_steps": total_steps_in_task,
            "completion_percentage": task_pct,
        },
        "blueprint": {
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completed_steps": completed_steps_all,
            "total_steps": total_steps_all,
            "completion_percentage": blueprint_pct,
        },
    }


def resolve_step_title(step_id, step_path, task_context):
    """
    Resolve the display title for a step using a consistent priority order.

    Priority:
        1. meta.yaml step title (from task_context) — always preferred when available
        2. dynamic.md.jinja '# ' title (via get_step_title) — fallback
        3. step_id slug — last resort

    Using meta.yaml as the primary source ensures that both the TOC
    (generate_table_of_contents) and the document body headings
    (render_blueprint_guidance / render_blueprint_code) produce identical
    anchors, fixing broken TOC links.

    Args:
        step_id: The step slug identifier
        step_path: Path to the step directory (for get_step_title fallback)
        task_context: Optional dict with 'tasks' and 'step_mapping' keys

    Returns:
        The resolved human-readable title string.
    """
    # 1. Try meta.yaml title via task_context
    if task_context:
        tasks = task_context.get("tasks", [])
        for task in tasks:
            for step in task.get("steps", []):
                slug = step.get("slug", "") if isinstance(step, dict) else step
                if slug == step_id:
                    title = step.get("title", "") if isinstance(step, dict) else ""
                    if title:
                        return title
                    break

    # 2. Try dynamic.md.jinja title
    jinja_title = get_step_title(step_path)
    if jinja_title:
        return jinja_title

    # 3. Fall back to slug
    return step_id


def generate_anchor(text):
    """
    Generate a markdown-compatible anchor from heading text.
    
    Follows standard markdown anchor conventions:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters except hyphens
    - Collapse multiple hyphens into single hyphen
    
    Args:
        text: The heading text to convert to an anchor
        
    Returns:
        String suitable for use as a markdown anchor (without the # prefix)
    """
    # Convert to lowercase
    anchor = text.lower()
    # Replace spaces and underscores with hyphens
    anchor = re.sub(r'[\s_]+', '-', anchor)
    # Remove special characters except hyphens and alphanumerics
    anchor = re.sub(r'[^a-z0-9-]', '', anchor)
    # Collapse multiple hyphens into single hyphen
    anchor = re.sub(r'-+', '-', anchor)
    # Remove leading/trailing hyphens
    anchor = anchor.strip('-')
    return anchor


def generate_table_of_contents(tasks, rendered_steps, depth=2, blueprint_dir=None, task_context=None):
    """
    Generate a hierarchical Table of Contents for rendered blueprint documentation.
    
    Creates a markdown-formatted TOC from the task→step hierarchy with proper
    anchor links. Includes both rendered and skipped steps so that TOC numbering
    stays consistent with the document body (where skipped steps still appear
    with a "SKIPPED" note). Steps without template files are excluded entirely.
    
    Args:
        tasks: List of task metadata dictionaries from load_task_metadata().
               Each task should have 'slug', 'title', and 'steps' keys.
        rendered_steps: Set or list of step slugs that have template files.
                       Steps not in this collection are excluded from the TOC
                       (these are steps with no template that produce no body output).
        depth: Controls nesting levels in TOC (default: 2)
               - depth=1: Only tasks (no steps)
               - depth=2: Tasks and steps (default)
               - depth>2: Reserved for future sub-step support
        blueprint_dir: Optional path to blueprint directory, used to resolve
                      step titles via resolve_step_title() for consistency
                      with document body headings.
        task_context: Optional dict with 'tasks' and 'step_mapping' keys,
                     passed through to resolve_step_title().
               
    Returns:
        String containing markdown-formatted TOC, or empty string if no tasks.
        
    Example output:
        ## Table of Contents
        
        - [Task 1: Platform Foundation](#task-1-platform-foundation)
          - [Step 1.1: Configure Account](#step-11-configure-account)
          - [Step 1.2: Set Up Roles](#step-12-set-up-roles)
        - [Task 2: Data Integration](#task-2-data-integration)
          - [Step 2.1: Connect Sources](#step-21-connect-sources)
    """
    if not tasks:
        return ""
    
    # Convert rendered_steps to set for O(1) lookup
    rendered_set = set(rendered_steps) if rendered_steps else set()
    
    toc_lines = [
        "## Table of Contents",
        "",
    ]
    
    for task_index, task in enumerate(tasks):
        task_num = task_index + 1
        task_title = task.get("title", task.get("slug", f"Task {task_num}"))
        task_steps = task.get("steps", [])
        
        # Check if any steps in this task were rendered
        task_step_slugs = [get_step_slug(s) for s in task_steps]
        rendered_task_steps = [slug for slug in task_step_slugs if slug in rendered_set]
        
        # Skip task entirely if no steps were rendered
        if not rendered_task_steps:
            continue
        
        # Generate task entry with anchor link
        task_heading = f"Task {task_num}: {task_title}"
        task_anchor = generate_anchor(task_heading)
        toc_lines.append(f"- [{task_heading}](#{task_anchor})")
        
        # Add step entries if depth >= 2
        if depth >= 2:
            for step_index, step in enumerate(task_steps):
                slug = get_step_slug(step)
                
                # Skip steps that don't have templates (these produce
                # no output in the document body at all)
                if slug not in rendered_set:
                    continue
                
                # Use position-based numbering so TOC labels match
                # the body headings (which use step_mapping step_index)
                step_label = f"{task_num}.{step_index + 1}"
                
                # Use resolve_step_title for consistent fallback with body headings
                if blueprint_dir is not None:
                    step_path = blueprint_dir / slug
                    step_display = resolve_step_title(slug, step_path, task_context)
                else:
                    # Legacy fallback: meta.yaml title → slug
                    step_title = step.get("title", "") if isinstance(step, dict) else ""
                    step_display = step_title if step_title else slug
                step_heading = f"Step {step_label}: {step_display}"
                step_anchor = generate_anchor(step_heading)
                toc_lines.append(f"  - [{step_heading}](#{step_anchor})")
    
    # Add trailing empty line and separator
    toc_lines.append("")
    toc_lines.append("---")
    toc_lines.append("")
    
    return "\n".join(toc_lines)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Render a complete customer journey with user-provided answers."
    )
    parser.add_argument(
        "answers_file",
        help="Path to the answers YAML file (e.g., answers/sample_answers.yaml)",
    )
    parser.add_argument(
        "--blueprint",
        required=True,
        help="Blueprint name/id (e.g., base_blueprint)",
    )
    parser.add_argument(
        "--lang",
        required=True,
        choices=["sql", "terraform"],
        help="Code language to render (sql or terraform)",
    )
    parser.add_argument(
        "--skip-guidance",
        action="store_true",
        help="Skip rendering guidance documents",
    )
    parser.add_argument(
        "--project",
        help="Project/workspace name to organize artifacts by customer or use case",
    )
    return parser.parse_args()


def get_language_extension(lang):
    """Get file extension for the specified language."""
    extensions = {
        "sql": "sql",
        "terraform": "tf",
    }
    return extensions.get(lang, lang)


def get_comment_syntax(lang):
    """Get comment syntax for the specified language."""
    comment_styles = {
        "sql": "--",
        "terraform": "#",
    }
    return comment_styles.get(lang, "#")


def get_step_title(step_path):
    """
    Extract the step title from the dynamic.md.jinja file.
    The title is expected to be the first line starting with '# '.
    Returns the title or None if not found.
    """
    dynamic_file = step_path / "dynamic.md.jinja"
    if not dynamic_file.exists():
        return None

    try:
        with open(dynamic_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None


def create_jinja_env(base_dir):
    """Create a Jinja2 environment configured for blueprint template rendering."""
    return Environment(
        loader=FileSystemLoader(base_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )


def try_render_template(template_path, answers, jinja_env, base_dir):
    """
    Attempt to render a Jinja2 template with the given answers.

    This approach correctly handles conditional logic - variables that are only
    used inside conditional blocks that won't execute (based on current answer
    values) won't cause the template to be skipped.

    Note: Due to the runtime rendering approach, only the first missing/null
    variable encountered will be reported. If multiple variables are missing
    in the active code path, users may need to fix them one at a time.
    This is a tradeoff for correctly handling conditional logic.

    Returns tuple: (rendered_output, missing_vars, null_vars)
    - rendered_output: the rendered string on success, or None on failure
    - missing_vars: list of variables that are actually needed but not in answers
    - null_vars: list of variables that are actually needed but are None in answers
    """
    try:
        # Load and attempt to render the template
        template = jinja_env.get_template(str(template_path.relative_to(base_dir)))

        # Build render context: wrap null values with NullTracker
        render_context = {}
        for key, value in answers.items():
            if value is None:
                render_context[key] = NullTracker(key)
            else:
                render_context[key] = value

        # Attempt to render
        rendered_output = template.render(**render_context)

        # If we get here, template rendered successfully
        return rendered_output, [], []

    except UndefinedError as e:
        # Extract variable name from error message
        error_msg = str(e)
        missing_vars = []
        null_vars = []

        # Parse the error message to identify the variable
        # Jinja2 UndefinedError messages typically look like:
        # "'variable_name' is undefined" or "'variable_name' is null" (our custom)
        match = re.search(r"'([^']+)'", error_msg)
        if match:
            var_name = match.group(1)
            if "is null" in error_msg:
                null_vars.append(var_name)
            else:
                missing_vars.append(var_name)
        else:
            # Fallback: couldn't parse, include raw error
            missing_vars.append(error_msg)

        return None, sorted(missing_vars), sorted(null_vars)

    except TemplateError as e:
        # Other template errors (syntax, etc.) - can't render
        # Return the error message so users can diagnose issues
        return None, [f"Template error: {str(e)}"], []


def check_template_renderable(template_path, answers, jinja_env, base_dir):
    """
    Check if a template can be rendered with the given answers.

    Thin wrapper around try_render_template that returns a boolean instead of
    the rendered output. Used in render_blueprint_guidance's pre-scan phase
    where only the renderability check is needed.

    Returns tuple: (can_render, missing_vars, null_vars)
    - can_render: True if template can be safely rendered
    - missing_vars: list of variables that are actually needed but not in answers
    - null_vars: list of variables that are actually needed but are None in answers
    """
    output, missing, null = try_render_template(template_path, answers, jinja_env, base_dir)
    return (output is not None), missing, null


def render_step_template(step_path, template_name, answers, jinja_env, base_dir):
    """
    Render a single template file within a step directory.

    Args:
        step_path: Path to the step directory
        template_name: Name of the template file (e.g., "code.sql.jinja", "dynamic.md.jinja")
        answers: Dictionary of user-provided answers
        jinja_env: Configured Jinja2 Environment
        base_dir: Base directory for template loading

    Returns tuple: (rendered_content, step_id, missing_vars)
    - rendered_content: the rendered string, or None if file doesn't exist or can't render
    - step_id: the step identifier (step_path.name)
    - missing_vars: list of missing/null variable names (empty if successful)
    """
    step_id = step_path.name
    template_file = step_path / template_name

    if not template_file.exists():
        return None, step_id, []

    rendered, missing_vars, null_vars = try_render_template(
        template_file, answers, jinja_env, base_dir
    )

    if rendered is None:
        all_issues = missing_vars + null_vars
        issue_details = []
        if missing_vars:
            issue_details.append(f"missing {missing_vars}")
        if null_vars:
            issue_details.append(f"null values {null_vars}")
        sys.stderr.write(
            f"  Skipping {step_id}/{template_name}: {', '.join(issue_details)}\n"
        )
        return None, step_id, all_issues

    return rendered, step_id, []


def render_blueprint_code(blueprint_dir, lang, answers, base_dir, blueprint_meta, date_display=None, task_context=None):
    """
    Render all code templates in a workflow.
    Only renders steps where all required variables are available.
    Steps with missing variables include a skip note in the output.
    Returns the concatenated rendered code and count of rendered/skipped steps.
    
    Args:
        blueprint_dir: Path to the blueprint directory
        lang: Language to render (sql, terraform)
        answers: Dictionary of user-provided answers
        base_dir: Base directory for template loading
        blueprint_meta: Parsed meta.yaml dictionary
        date_display: Pre-formatted timestamp string for headers (e.g., "2026-02-27 10:30:00").
            If None, generates one from datetime.now().
        task_context: Optional dict with task metadata for enhanced rendering:
            - tasks: List of task metadata from load_task_metadata()
            - step_mapping: Dict from build_task_step_mapping()
            When provided, adds task context headers to rendered output.
    
    Returns:
        Tuple of (rendered_code, rendered_count, skipped_count)
    """
    blueprint_id = blueprint_dir.name

    if not isinstance(blueprint_meta, dict):
        raise ValueError(f"blueprint_meta must be a dict, got {type(blueprint_meta).__name__}")
    blueprint_name = blueprint_meta.get("name", blueprint_id)
    step_order = blueprint_meta.get("steps", [])

    # Create Jinja2 environment once for all steps
    jinja_env = create_jinja_env(base_dir)

    comment_char = get_comment_syntax(lang)
    rendered_sections = []
    rendered_count = 0
    skipped_count = 0

    # Extract task context if provided
    step_mapping = task_context.get("step_mapping", {}) if task_context else {}
    tasks = task_context.get("tasks", []) if task_context else []
    current_task_slug = None
    current_task_num = 0

    # Add header
    if date_display is None:
        date_display = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = [
        f"{comment_char} ============================================================",
        f"{comment_char} RENDERED JOURNEY: {blueprint_name}",
        f"{comment_char} Generated: {date_display}",
        f"{comment_char} Blueprint: {blueprint_id}",
        f"{comment_char} Language: {lang}",
        f"{comment_char} ============================================================\n",
    ]
    rendered_sections.append("\n".join(header))

    # Process steps in the order defined in meta.yaml
    for step_id in step_order:
        # Add task header when entering a new task (if task context provided)
        if step_mapping and step_id in step_mapping:
            task_info = step_mapping[step_id]
            if task_info["task_slug"] != current_task_slug:
                current_task_slug = task_info["task_slug"]
                task_title = task_info["task_title"]
                current_task_num = task_info["task_index"] + 1
                total_tasks = len(tasks)
                
                # Find task metadata for additional info
                task_meta = next(
                    (t for t in tasks if t.get("slug") == current_task_slug), 
                    {}
                )
                
                task_header = [
                    "",
                    f"{comment_char} ============================================================================",
                    f"{comment_char} TASK {current_task_num}: {task_title}",
                ]
                
                # Add summary if available
                if task_meta.get("summary"):
                    summary = task_meta["summary"].strip().replace("\n", " ")
                    task_header.append(f"{comment_char} Summary: {summary}")
                
                # Add personas if available
                if task_meta.get("personas"):
                    personas_str = ", ".join(task_meta["personas"])
                    task_header.append(f"{comment_char} Personas: {personas_str}")
                
                # Add role requirements if available
                if task_meta.get("role_requirements"):
                    roles_str = ", ".join(task_meta["role_requirements"])
                    task_header.append(f"{comment_char} Role Requirements: {roles_str}")
                
                # Add external requirements if available
                if task_meta.get("external_requirements"):
                    ext_reqs_str = ", ".join(task_meta["external_requirements"])
                    task_header.append(f"{comment_char} External Requirements: {ext_reqs_str}")
                
                task_header.extend([
                    f"{comment_char} ============================================================================",
                    "",
                ])
                rendered_sections.append("\n".join(task_header))
        step_path = blueprint_dir / step_id
        if not step_path.exists():
            sys.stderr.write(f"Warning: Step directory not found: {step_path}\n")
            continue

        rendered_code, _, missing_vars = render_step_template(
            step_path, f"code.{lang}.jinja", answers, jinja_env, base_dir
        )

        # Determine step numbering (hierarchical if task context available, flat otherwise)
        if step_mapping and step_id in step_mapping:
            task_info = step_mapping[step_id]
            step_num_in_task = task_info["step_index"] + 1
            step_label = f"{current_task_num}.{step_num_in_task}"
        else:
            # Fallback to flat numbering for backward compatibility
            step_label = str(rendered_count + skipped_count + 1)

        if rendered_code is None:
            # No code file or missing variables - add skip note if file existed
            code_file = step_path / f"code.{lang}.jinja"
            if code_file.exists() and missing_vars:
                # Classify vars as missing vs null
                missing_only, null_vars = classify_missing_vars(missing_vars, answers)

                # Get step title using canonical resolution (meta.yaml first)
                step_heading = resolve_step_title(step_id, step_path, task_context)
                skip_header = f"SKIPPED Step {step_label}: {step_heading}"

                # Build skip note
                skip_note = [
                    "",
                    f"{comment_char} ------------------------------------------------------------",
                    f"{comment_char} {skip_header}",
                ]
                if missing_only:
                    skip_note.append(
                        f"{comment_char} Missing answers: {', '.join(missing_only)}"
                    )
                if null_vars:
                    skip_note.append(
                        f"{comment_char} Null/empty answers: {', '.join(null_vars)}"
                    )
                skip_note.extend(
                    [
                        f"{comment_char} Provide values for the above variables to render this step.",
                        f"{comment_char} ------------------------------------------------------------",
                        "",
                    ]
                )
                rendered_sections.append("\n".join(skip_note))
                skipped_count += 1
            continue

        # Add step header with hierarchical numbering using canonical title resolution
        step_heading = resolve_step_title(step_id, step_path, task_context)
        step_header_text = f"Step {step_label}: {step_heading}"
        
        step_header = [
            "",
            f"{comment_char} ------------------------------------------------------------",
            f"{comment_char} {step_header_text}",
            f"{comment_char} ------------------------------------------------------------",
            "",
        ]
        rendered_sections.append("\n".join(step_header))
        rendered_sections.append(rendered_code)
        rendered_count += 1

    return "\n".join(rendered_sections), rendered_count, skipped_count


def render_blueprint_guidance(blueprint_dir, answers, base_dir, blueprint_meta, date_display=None, task_context=None, toc_depth=2):
    """
    Render all guidance/overview documents in a workflow.
    Only renders steps where all required variables are available.
    Steps with missing variables include a skip note in the output.
    Returns the concatenated rendered guidance markdown and count of rendered/skipped steps.
    
    Args:
        blueprint_dir: Path to the blueprint directory
        answers: Dictionary of user-provided answers
        base_dir: Base directory for template loading
        blueprint_meta: Parsed meta.yaml dictionary
        date_display: Pre-formatted timestamp string for headers (e.g., "2026-02-27 10:30:00").
            If None, generates one from datetime.now().
        task_context: Optional dict with task metadata for enhanced rendering:
            - tasks: List of task metadata from load_task_metadata()
            - step_mapping: Dict from build_task_step_mapping()
            When provided, adds task sections with overview content to rendered output.
        toc_depth: Controls Table of Contents nesting levels (default: 2)
            - depth=1: Only tasks (no steps)
            - depth=2: Tasks and steps (default)
    
    Returns:
        Tuple of (rendered_guidance, rendered_count, skipped_count)
    """
    blueprint_id = blueprint_dir.name

    if not isinstance(blueprint_meta, dict):
        raise ValueError(f"blueprint_meta must be a dict, got {type(blueprint_meta).__name__}")
    blueprint_name = blueprint_meta.get("name", blueprint_id)
    blueprint_overview = blueprint_meta.get("overview", "")
    step_order = blueprint_meta.get("steps", [])

    # Create Jinja2 environment with strict undefined checking
    jinja_env = create_jinja_env(base_dir)

    # Extract task context if provided
    step_mapping = task_context.get("step_mapping", {}) if task_context else {}
    tasks = task_context.get("tasks", []) if task_context else []

    # PHASE 1: Pre-scan to determine which steps have templates
    # The TOC includes ALL steps that have a template file (both renderable
    # and skipped), so that numbering stays consistent with the document body
    # where skipped steps still appear with a "SKIPPED" note.
    toc_steps = set()
    for step_id in step_order:
        step_path = blueprint_dir / step_id
        if not step_path.exists():
            continue
        
        dynamic_file = step_path / "dynamic.md.jinja"
        if not dynamic_file.exists():
            continue
        
        toc_steps.add(step_id)

    # PHASE 2: Build header with task-aware TOC
    rendered_sections = []
    rendered_count = 0
    skipped_count = 0
    current_task_slug = None
    current_task_num = 0

    # Add header
    if date_display is None:
        date_display = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = [
        f"# {blueprint_name}",
        "",
        f"> Generated: {date_display}",
        f"> Blueprint: {blueprint_id}",
        "",
        "---",
        "",
    ]

    if blueprint_overview:
        header.append(blueprint_overview)
        header.append("")
        header.append("---")
        header.append("")

    rendered_sections.append("\n".join(header))

    # Generate and add hierarchical table of contents (includes all steps with templates)
    if tasks:
        toc = generate_table_of_contents(tasks, toc_steps, depth=toc_depth, blueprint_dir=blueprint_dir, task_context=task_context)
        if toc:
            rendered_sections.append(toc)

    # Process steps in the order defined in meta.yaml
    flat_step_num = 1  # Fallback for backward compatibility
    for step_id in step_order:
        # Add task header when entering a new task (if task context provided)
        if step_mapping and step_id in step_mapping:
            task_info = step_mapping[step_id]
            if task_info["task_slug"] != current_task_slug:
                current_task_slug = task_info["task_slug"]
                task_title = task_info["task_title"]
                current_task_num = task_info["task_index"] + 1
                
                # Find task metadata for additional info
                task_meta = next(
                    (t for t in tasks if t.get("slug") == current_task_slug), 
                    {}
                )
                
                task_section = [
                    "",
                    f"# Task {current_task_num}: {task_title}",
                    "",
                ]
                
                # Add task summary if available
                if task_meta.get("summary"):
                    summary = task_meta["summary"].strip().replace("\n", " ")
                    task_section.append(f"**Summary:** {summary}")
                    task_section.append("")
                
                # Add prerequisites section if available
                prereqs = []
                if task_meta.get("personas"):
                    personas_str = ", ".join(task_meta["personas"])
                    prereqs.append(f"- **Personas:** {personas_str}")
                
                if task_meta.get("role_requirements"):
                    roles_str = ", ".join(task_meta["role_requirements"])
                    prereqs.append(f"- **Role Requirements:** {roles_str}")
                
                if task_meta.get("external_requirements"):
                    ext_reqs_str = ", ".join(task_meta["external_requirements"])
                    prereqs.append(f"- **External Requirements:** {ext_reqs_str}")
                
                if prereqs:
                    task_section.append("**Prerequisites:**")
                    task_section.extend(prereqs)
                    task_section.append("")
                
                # Load and add task overview content if available
                task_overview = load_task_overview(blueprint_dir, current_task_slug)
                if task_overview:
                    task_section.append("<details>")
                    task_section.append("<summary>Task Overview (click to expand)</summary>")
                    task_section.append("")
                    task_section.append(task_overview)
                    task_section.append("")
                    task_section.append("</details>")
                    task_section.append("")
                
                task_section.append("---")
                task_section.append("")
                
                rendered_sections.append("\n".join(task_section))

        step_path = blueprint_dir / step_id
        if not step_path.exists():
            sys.stderr.write(f"Warning: Step directory not found: {step_path}\n")
            continue

        rendered_guidance, _, missing_vars = render_step_template(
            step_path, "dynamic.md.jinja", answers, jinja_env, base_dir
        )

        # Determine step numbering (hierarchical if task context available, flat otherwise)
        if step_mapping and step_id in step_mapping:
            task_info = step_mapping[step_id]
            step_num_in_task = task_info["step_index"] + 1
            step_label = f"{current_task_num}.{step_num_in_task}"
        else:
            # Fallback to flat numbering for backward compatibility
            step_label = str(flat_step_num)
            flat_step_num += 1

        if rendered_guidance is None:
            # No dynamic template or missing variables - add skip note if file existed
            dynamic_file = step_path / "dynamic.md.jinja"
            if dynamic_file.exists() and missing_vars:
                # Classify vars as missing vs null
                missing_only, null_vars = classify_missing_vars(missing_vars, answers)

                # Get step title using canonical resolution (meta.yaml first)
                step_heading = resolve_step_title(step_id, step_path, task_context)

                # Build skip note
                skip_note = [
                    "",
                    f"## Step {step_label}: {step_heading}",
                    "",
                    "> **SKIPPED:** This step could not be rendered due to missing answers.",
                    ">",
                ]
                if missing_only:
                    skip_note.append(
                        f"> **Missing answers:** `{', '.join(missing_only)}`"
                    )
                    skip_note.append(">")
                if null_vars:
                    skip_note.append(
                        f"> **Null/empty answers:** `{', '.join(null_vars)}`"
                    )
                    skip_note.append(">")
                skip_note.extend(
                    [
                        "> Provide values for the above variables to render this step.",
                        "",
                        "---",
                        "",
                    ]
                )
                rendered_sections.append("\n".join(skip_note))
                skipped_count += 1
            continue

        # Add step header with hierarchical numbering using canonical title resolution
        step_heading = resolve_step_title(step_id, step_path, task_context)
        
        step_header = [
            "",
            f"## Step {step_label}: {step_heading}",
            "",
        ]

        rendered_sections.append("\n".join(step_header))
        rendered_sections.append(rendered_guidance)
        rendered_sections.append("\n---\n")

        rendered_count += 1

    return "\n".join(rendered_sections), rendered_count, skipped_count


def validate_name(name, name_type="name"):
    """
    Validate that a name contains only safe characters.
    Prevents path traversal attacks by rejecting special characters.
    
    Args:
        name: The name to validate
        name_type: Description of what's being validated (e.g., "project name", "blueprint ID")
    
    Allowed: alphanumeric characters, underscores, and hyphens.
    """
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError(
            f"Invalid {name_type} '{name}'. "
            f"{name_type.capitalize()}s can only contain alphanumeric characters, underscores, and hyphens."
        )


def setup_project_directories(base_dir, project_name, blueprint_id):
    """
    Ensure project directory structure exists for the given project name and blueprint.
    
    This function is always called to organize artifacts by project. When --project
    is not specified, the default project name 'default-project' is used.
    
    Creates:
        projects/<project_name>/
        ├── answers/
        │   └── <blueprint_id>/
        └── output/
            ├── iac/
            │   └── sql/
            └── documentation/
    
    Args:
        base_dir: Base directory of the repository
        project_name: Name of the project (user-specified or 'default-project')
        blueprint_id: ID of the blueprint being rendered
    
    Returns:
        Path to the project directory
    """
    validate_name(project_name, "project name")
    validate_name(blueprint_id, "blueprint ID")
    project_dir = base_dir / "projects" / project_name
    
    (project_dir / "answers" / blueprint_id).mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "iac" / "sql").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "documentation").mkdir(parents=True, exist_ok=True)
    
    return project_dir


def main():
    """Main entry point."""
    args = parse_args()

    # Resolve paths
    answers_path = Path(args.answers_file)
    if not answers_path.exists():
        sys.stderr.write(f"Error: Answers file not found: {answers_path}\n")
        sys.exit(1)

    # Determine base directory (assume script is in scripts/)
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    try:
        project_name = args.project if args.project else DEFAULT_PROJECT_NAME
        project_dir = setup_project_directories(base_dir, project_name, args.blueprint)
        print(f"Using project: {project_name}")
        print(f"Project directory: {project_dir}")
        
        output_base_dir = project_dir / "output" / "iac"
        guidance_base_dir = project_dir / "output" / "documentation"

        blueprints_dir = base_dir / "blueprints"

        # Find workflow directory (external repo structure)
        blueprint_dir = blueprints_dir / args.blueprint
        if not blueprint_dir.exists() or not blueprint_dir.is_dir():
            sys.stderr.write(f"Error: Blueprint directory not found: {blueprint_dir}\n")
            sys.exit(1)

        # Load answers
        print(f"Loading answers from {answers_path}...")
        answers = load_yaml(answers_path)

        if answers is None:
            answers = {}
        elif not isinstance(answers, dict):
            sys.stderr.write(
                f"Error: Answers file must contain a YAML mapping, got {type(answers).__name__}\n"
            )
            sys.exit(1)

        # Load meta.yaml once for all consumers
        meta_file = blueprint_dir / "meta.yaml"
        if not meta_file.exists():
            sys.stderr.write(f"Error: meta.yaml not found: {meta_file}\n")
            sys.exit(1)
        blueprint_meta = load_yaml(meta_file)
        if not isinstance(blueprint_meta, dict):
            sys.stderr.write(
                f"Error: meta.yaml in {blueprint_dir} must contain a YAML mapping\n"
            )
            sys.exit(1)

        # Generate timestamp once for consistent headers and filenames
        timestamp = datetime.now()
        date_display = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        date_file = timestamp.strftime("%Y%m%d%H%M%S")

        # Load task context for hierarchical rendering
        tasks = load_task_metadata(blueprint_meta)
        task_context = None
        if tasks:
            step_mapping = build_task_step_mapping(tasks)
            task_context = {
                "tasks": tasks,
                "step_mapping": step_mapping,
            }

        # Render IaC code
        print(f"Rendering blueprint '{args.blueprint}' for language '{args.lang}'...")
        rendered_code, code_rendered, code_skipped = render_blueprint_code(
            blueprint_dir, args.lang, answers, base_dir, blueprint_meta,
            date_display=date_display, task_context=task_context
        )

        # Generate IaC output filename
        output_dir = output_base_dir / args.lang
        output_dir.mkdir(parents=True, exist_ok=True)

        extension = get_language_extension(args.lang)
        output_file = output_dir / f"{args.blueprint}_{date_file}.{extension}"

        # Write IaC output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rendered_code)

        print(f"✓ Successfully rendered IaC to: {output_file}")
        print(f"  Steps rendered: {code_rendered}, skipped (missing vars): {code_skipped}")
        print(f"  Total size: {len(rendered_code)} characters")

        # Render guidance documents (unless skipped)
        if not args.skip_guidance:
            print("\nRendering guidance documents...")
            rendered_guidance, guide_rendered, guide_skipped = render_blueprint_guidance(
                blueprint_dir, answers, base_dir, blueprint_meta,
                date_display=date_display, task_context=task_context
            )

            # Generate guidance output filename
            guidance_dir = guidance_base_dir
            guidance_dir.mkdir(parents=True, exist_ok=True)

            guidance_file = guidance_dir / f"{args.blueprint}_{date_file}.md"

            # Write guidance output
            with open(guidance_file, "w", encoding="utf-8") as f:
                f.write(rendered_guidance)

            print(f"✓ Successfully rendered guidance to: {guidance_file}")
            print(
                f"  Steps rendered: {guide_rendered}, skipped (missing vars): {guide_skipped}"
            )
            print(f"  Total size: {len(rendered_guidance)} characters")

    except (ValueError, OSError, yaml.YAMLError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
