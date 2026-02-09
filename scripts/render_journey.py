#!/usr/bin/env python3
"""
render_journey.py

Generates consolidated IaC and guidance files based on a blueprint and an answers file.
This script renders all code templates and overview documents from steps within a blueprint,
concatenating them in order into output files.

Only steps where ALL required variables are provided in the answers file will be rendered.
Steps with missing variables are skipped entirely.

Supports both slug-based and legacy UID-based directory structures with automatic fallback.
"""

import argparse
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
        meta,
        nodes,
    )
except ImportError as e:
    sys.stderr.write(f"Error: Required library not found: {e}\n")
    sys.stderr.write("Please install dependencies: pip install pyyaml jinja2\n")
    sys.exit(1)


def load_yaml(file_path):
    """Load and parse a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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
        "--output-dir",
        default="output/iac",
        help="Output directory for rendered IaC files (default: output/iac)",
    )
    parser.add_argument(
        "--guidance-dir",
        default="output/documentation",
        help="Output directory for rendered guidance files (default: output/documentation)",
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
    except Exception:
        pass
    return None


def get_blueprint_slug(blueprint_dir, meta_data=None):
    """
    Get the slug for a blueprint.
    
    The slug is determined in the following order:
    1. Explicit 'slug' field in meta.yaml
    2. Directory name (assumed to be slug-based)
    
    Args:
        blueprint_dir: Path to the blueprint directory
        meta_data: Optional pre-loaded meta.yaml data
        
    Returns:
        The blueprint slug string
    """
    if meta_data and "slug" in meta_data:
        return meta_data["slug"]
    # Use directory name as slug (already slug-based in the new structure)
    return blueprint_dir.name


def resolve_step_path(blueprint_dir, step_identifier, step_slug_map=None):
    """
    Resolve a step identifier to its actual directory path.
    
    Supports both slug-based and legacy UID-based directory structures.
    First attempts to find the step by slug, then falls back to UID-based lookup.
    
    Args:
        blueprint_dir: Path to the blueprint directory
        step_identifier: Step identifier from meta.yaml (slug or UID)
        step_slug_map: Optional mapping of step slugs to directory paths
        
    Returns:
        Tuple of (step_path, step_slug, used_fallback)
        - step_path: Path to the step directory
        - step_slug: The human-readable slug for the step
        - used_fallback: True if UID-based fallback was used
    """
    # First, try direct path resolution (slug-based naming)
    step_path = blueprint_dir / step_identifier
    if step_path.exists() and step_path.is_dir():
        return step_path, step_identifier, False
    
    # Check if step_slug_map has a mapping for this identifier
    if step_slug_map and step_identifier in step_slug_map:
        mapped_path = step_slug_map[step_identifier]
        if mapped_path.exists() and mapped_path.is_dir():
            slug = mapped_path.name
            return mapped_path, slug, False
    
    # Fallback: search for legacy UID-based directories
    # Look for directories that might have a step.yaml or meta.yaml with matching ID
    for child_dir in blueprint_dir.iterdir():
        if not child_dir.is_dir():
            continue
        # Check if this could be a legacy UID directory matching the identifier
        if child_dir.name.startswith("step_") or child_dir.name == step_identifier:
            step_meta_file = child_dir / "step.yaml"
            if step_meta_file.exists():
                step_meta = load_yaml(step_meta_file)
                if step_meta.get("step_id") == step_identifier or step_meta.get("slug") == step_identifier:
                    slug = step_meta.get("slug", child_dir.name)
                    sys.stderr.write(
                        f"  Note: Using legacy UID path for step '{step_identifier}' -> '{child_dir.name}'\n"
                    )
                    return child_dir, slug, True
    
    # If no match found, return the original path (will fail gracefully later)
    return step_path, step_identifier, False


def build_step_slug_map(blueprint_dir):
    """
    Build a mapping of step identifiers to their directory paths.
    
    Scans the blueprint directory to create a lookup map for resolving
    both slug-based and UID-based step references.
    
    Args:
        blueprint_dir: Path to the blueprint directory
        
    Returns:
        Dictionary mapping step identifiers (slugs and UIDs) to directory paths
    """
    slug_map = {}
    
    for child_dir in blueprint_dir.iterdir():
        if not child_dir.is_dir():
            continue
        
        # Skip non-step directories (like the meta.yaml file location)
        if child_dir.name.startswith("."):
            continue
            
        # Add directory name as a key (slug-based lookup)
        slug_map[child_dir.name] = child_dir
        
        # Check for step metadata with additional identifiers
        step_meta_file = child_dir / "step.yaml"
        if step_meta_file.exists():
            try:
                step_meta = load_yaml(step_meta_file)
                # Map step_id to directory path (for UID-based references)
                if "step_id" in step_meta:
                    slug_map[step_meta["step_id"]] = child_dir
                # Map explicit slug if different from directory name
                if "slug" in step_meta and step_meta["slug"] != child_dir.name:
                    slug_map[step_meta["slug"]] = child_dir
            except Exception:
                pass  # Ignore malformed step.yaml files
    
    return slug_map


def find_template_variables(template_source, jinja_env):
    """
    Use Jinja2's AST parser to find all undeclared variables in a template.

    Returns a set of variable names referenced in the template.
    """
    try:
        ast = jinja_env.parse(template_source)
        return meta.find_undeclared_variables(ast)
    except TemplateError:
        # If parsing fails, return empty set - the actual render will catch the error
        return set()


def find_template_set_variables(template_source, jinja_env):
    """
    Find variables that are set within the template using {% set %}.

    Returns a set of variable names defined internally in the template.
    """
    try:
        ast = jinja_env.parse(template_source)
        set_vars = set()
        for node in ast.find_all(nodes.Assign):
            target = node.target
            # Handle tuple unpacking: {% set x, y = values %}
            if isinstance(target, nodes.Tuple):
                for item in target.items:
                    if isinstance(item, nodes.Name):
                        set_vars.add(item.name)
            # Handle simple assignments: {% set x = value %}
            elif isinstance(target, nodes.Name):
                set_vars.add(target.name)
        return set_vars
    except TemplateError:
        return set()


def check_template_renderable(template_path, answers, jinja_env):
    """
    Pre-check if a template can be rendered with the given answers.
    Uses Jinja2's AST parser to find all referenced variables, then checks
    if they exist in answers and have non-None values where needed.

    Returns tuple: (can_render, missing_vars, null_vars)
    - can_render: True if template can be safely rendered
    - missing_vars: list of variables not in answers
    - null_vars: list of variables that are None in answers
    """
    with open(template_path, "r", encoding="utf-8") as f:
        template_source = f.read()

    # Use Jinja2's AST to find all undeclared variables
    referenced_vars = find_template_variables(template_source, jinja_env)

    # Find variables set internally within the template ({% set %})
    set_vars = find_template_set_variables(template_source, jinja_env)

    # Only check external variables (exclude internally-set variables)
    external_vars = referenced_vars - set_vars

    # Separate into missing (not in answers) and null (in answers but None)
    missing_vars = []
    null_vars = []

    for var in external_vars:
        if var not in answers:
            missing_vars.append(var)
        elif answers[var] is None:
            null_vars.append(var)

    missing_vars = sorted(missing_vars)
    null_vars = sorted(null_vars)

    can_render = len(missing_vars) == 0 and len(null_vars) == 0
    return can_render, missing_vars, null_vars


def render_step_code(step_path, lang, answers, jinja_env, base_dir):
    """
    Render code template for a step.
    Returns tuple: (rendered_code, step_id, missing_vars)
    - rendered_code: the rendered content or None if file doesn't exist
    - step_id: the step identifier
    - missing_vars: list of missing/null variable names (empty if successful)
    """
    step_id = step_path.name
    code_file = step_path / f"code.{lang}.jinja"

    if not code_file.exists():
        return None, step_id, []

    # Pre-check if template can be rendered using Jinja2's AST parser
    can_render, missing_vars, null_vars = check_template_renderable(
        code_file, answers, jinja_env
    )
    if not can_render:
        all_issues = missing_vars + null_vars
        issue_details = []
        if missing_vars:
            issue_details.append(f"missing {missing_vars}")
        if null_vars:
            issue_details.append(f"null values {null_vars}")
        sys.stderr.write(
            f"  Skipping {step_id}/code.{lang}.jinja: {', '.join(issue_details)}\n"
        )
        return None, step_id, all_issues

    try:
        # Load template using the shared Jinja2 environment
        template = jinja_env.get_template(str(code_file.relative_to(base_dir)))

        # Render the template (pre-check should have caught issues)
        rendered = template.render(**answers)
        return rendered, step_id, []

    except TemplateError as e:
        sys.stderr.write(f"Warning: Template error in {code_file}: {e}\n")
        return None, step_id, []


def render_step_guidance(step_path, answers, jinja_env, base_dir):
    """
    Render dynamic guidance markdown for a step from dynamic.md.jinja.
    Returns tuple: (rendered_content, step_id, missing_vars)
    - rendered_content: the rendered content or None if file doesn't exist
    - step_id: the step identifier
    - missing_vars: list of missing variable names (empty if successful)
    """
    step_id = step_path.name
    dynamic_file = step_path / "dynamic.md.jinja"

    if not dynamic_file.exists():
        return None, step_id, []

    # Pre-check if template can be rendered using Jinja2's AST parser
    can_render, missing_vars, null_vars = check_template_renderable(
        dynamic_file, answers, jinja_env
    )
    if not can_render:
        all_issues = missing_vars + null_vars
        issue_details = []
        if missing_vars:
            issue_details.append(f"missing {missing_vars}")
        if null_vars:
            issue_details.append(f"null values {null_vars}")
        sys.stderr.write(
            f"  Skipping {step_id}/dynamic.md.jinja: {', '.join(issue_details)}\n"
        )
        return None, step_id, all_issues

    try:
        # Load template using the shared Jinja2 environment
        template = jinja_env.get_template(str(dynamic_file.relative_to(base_dir)))

        # Render the template (pre-check should have caught issues)
        rendered = template.render(**answers)
        return rendered, step_id, []

    except TemplateError as e:
        sys.stderr.write(f"Warning: Template error in {dynamic_file}: {e}\n")
        return None, step_id, []


def render_blueprint_code(blueprint_dir, lang, answers, base_dir):
    """
    Render all code templates in a workflow.
    Only renders steps where all required variables are available.
    Steps with missing variables include a skip note in the output.
    Returns the concatenated rendered code and count of rendered/skipped steps.
    
    Supports both slug-based and legacy UID-based directory structures.
    """
    # Load meta.yaml for workflow metadata and step ordering
    meta_file = blueprint_dir / "meta.yaml"
    if not meta_file.exists():
        sys.stderr.write(
            f"Error: meta.yaml not found in blueprint directory: {blueprint_dir}\n"
        )
        sys.exit(1)

    meta_data = load_yaml(meta_file)
    blueprint_name = meta_data.get("name", blueprint_dir.name)
    blueprint_slug = get_blueprint_slug(blueprint_dir, meta_data)
    step_order = meta_data.get("steps", [])

    # Build step slug map for resolving step identifiers
    step_slug_map = build_step_slug_map(blueprint_dir)

    # Create Jinja2 environment once for all steps
    jinja_env = Environment(
        loader=FileSystemLoader(base_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    comment_char = get_comment_syntax(lang)
    rendered_sections = []
    rendered_count = 0
    skipped_count = 0

    # Add header with slug for better readability
    header = [
        f"{comment_char} ============================================================",
        f"{comment_char} RENDERED JOURNEY: {blueprint_name}",
        f"{comment_char} Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{comment_char} Blueprint: {blueprint_slug}",
        f"{comment_char} Language: {lang}",
        f"{comment_char} ============================================================\n",
    ]
    rendered_sections.append("\n".join(header))

    # Process steps in the order defined in meta.yaml
    for step_identifier in step_order:
        # Resolve step path using slug-based lookup with UID fallback
        step_path, step_slug, used_fallback = resolve_step_path(
            blueprint_dir, step_identifier, step_slug_map
        )
        
        if not step_path.exists():
            sys.stderr.write(f"Warning: Step directory not found for '{step_slug}': {step_path}\n")
            continue

        rendered_code, _, missing_vars = render_step_code(
            step_path, lang, answers, jinja_env, base_dir
        )

        if rendered_code is None:
            # No code file or missing variables - add skip note if file existed
            code_file = step_path / f"code.{lang}.jinja"
            if code_file.exists() and missing_vars:
                # Determine if vars are missing or null
                null_vars = [
                    v for v in missing_vars if v in answers and answers[v] is None
                ]
                missing_only = [v for v in missing_vars if v not in answers]

                # Get step title for better readability
                step_title = get_step_title(step_path)
                if step_title:
                    skip_header = f"SKIPPED: {step_title} ({step_slug})"
                else:
                    skip_header = f"SKIPPED: {step_slug}"

                # Build skip note with slug reference
                skip_note = [
                    "",
                    f"{comment_char} ============================================================",
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
                        f"{comment_char} ============================================================",
                        "",
                    ]
                )
                rendered_sections.append("\n".join(skip_note))
                skipped_count += 1
            continue

        rendered_sections.append(rendered_code)
        rendered_count += 1

    return "\n".join(rendered_sections), rendered_count, skipped_count


def render_blueprint_guidance(blueprint_dir, answers, base_dir):
    """
    Render all guidance/overview documents in a workflow.
    Only renders steps where all required variables are available.
    Steps with missing variables include a skip note in the output.
    Returns the concatenated rendered guidance markdown and count of rendered/skipped steps.
    
    Supports both slug-based and legacy UID-based directory structures.
    """
    # Load meta.yaml for workflow metadata and step ordering
    meta_file = blueprint_dir / "meta.yaml"
    if not meta_file.exists():
        sys.stderr.write(
            f"Error: meta.yaml not found in blueprint directory: {blueprint_dir}\n"
        )
        sys.exit(1)

    meta_data = load_yaml(meta_file)
    blueprint_name = meta_data.get("name", blueprint_dir.name)
    blueprint_slug = get_blueprint_slug(blueprint_dir, meta_data)
    blueprint_overview = meta_data.get("overview", "")
    step_order = meta_data.get("steps", [])

    # Build step slug map for resolving step identifiers
    step_slug_map = build_step_slug_map(blueprint_dir)

    # Create Jinja2 environment with strict undefined checking
    jinja_env = Environment(
        loader=FileSystemLoader(base_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    rendered_sections = []
    rendered_count = 0
    skipped_count = 0

    # Add header with slug for better readability
    header = [
        f"# {blueprint_name}",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> Blueprint: {blueprint_slug}",
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

    # Process steps in the order defined in meta.yaml
    step_num = 1
    for step_identifier in step_order:
        # Resolve step path using slug-based lookup with UID fallback
        step_path, step_slug, used_fallback = resolve_step_path(
            blueprint_dir, step_identifier, step_slug_map
        )
        
        if not step_path.exists():
            sys.stderr.write(f"Warning: Step directory not found for '{step_slug}': {step_path}\n")
            continue

        rendered_guidance, _, missing_vars = render_step_guidance(
            step_path, answers, jinja_env, base_dir
        )

        if rendered_guidance is None:
            # No dynamic template or missing variables - add skip note if file existed
            dynamic_file = step_path / "dynamic.md.jinja"
            if dynamic_file.exists() and missing_vars:
                # Determine if vars are missing or null
                null_vars = [
                    v for v in missing_vars if v in answers and answers[v] is None
                ]
                missing_only = [v for v in missing_vars if v not in answers]

                # Get step title for better readability
                step_title = get_step_title(step_path)
                if step_title:
                    step_heading = f"{step_title} ({step_slug})"
                else:
                    step_heading = step_slug

                # Build skip note with slug reference
                skip_note = [
                    "",
                    f"## Step {step_num}: {step_heading}",
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
                step_num += 1
            continue

        # Add step header with slug for better readability
        step_header = [
            "",
            f"## Step {step_num}: {step_slug}",
            "",
        ]

        rendered_sections.append("\n".join(step_header))
        rendered_sections.append(rendered_guidance)
        rendered_sections.append("\n---\n")

        rendered_count += 1
        step_num += 1

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
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        sys.stderr.write(
            f"Error: Invalid {name_type} '{name}'. "
            f"{name_type.capitalize()}s can only contain alphanumeric characters, underscores, and hyphens.\n"
        )
        sys.exit(1)


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

    blueprints_dir = base_dir / "blueprints"

    # Find blueprint directory - support both slug-based and legacy UID-based lookups
    blueprint_dir = blueprints_dir / args.blueprint
    blueprint_slug = args.blueprint  # Default to the provided argument
    
    if not blueprint_dir.exists() or not blueprint_dir.is_dir():
        # Try to find a blueprint directory by searching for meta.yaml with matching blueprint_id
        found = False
        for child_dir in blueprints_dir.iterdir():
            if not child_dir.is_dir():
                continue
            meta_file = child_dir / "meta.yaml"
            if meta_file.exists():
                try:
                    meta_data = load_yaml(meta_file)
                    if meta_data.get("blueprint_id") == args.blueprint or meta_data.get("slug") == args.blueprint:
                        blueprint_dir = child_dir
                        blueprint_slug = get_blueprint_slug(child_dir, meta_data)
                        sys.stderr.write(
                            f"Note: Resolved blueprint '{args.blueprint}' to directory '{child_dir.name}'\n"
                        )
                        found = True
                        break
                except Exception:
                    pass
        
        if not found:
            sys.stderr.write(f"Error: Blueprint '{args.blueprint}' not found in {blueprints_dir}\n")
            sys.stderr.write("Available blueprints:\n")
            for child_dir in blueprints_dir.iterdir():
                if child_dir.is_dir():
                    meta_file = child_dir / "meta.yaml"
                    if meta_file.exists():
                        try:
                            meta_data = load_yaml(meta_file)
                            name = meta_data.get("name", child_dir.name)
                            sys.stderr.write(f"  - {child_dir.name}: {name}\n")
                        except Exception:
                            sys.stderr.write(f"  - {child_dir.name}\n")
            sys.exit(1)
    else:
        # Load meta.yaml to get the slug
        meta_file = blueprint_dir / "meta.yaml"
        if meta_file.exists():
            meta_data = load_yaml(meta_file)
            blueprint_slug = get_blueprint_slug(blueprint_dir, meta_data)

    project_name = args.project if args.project else "default-project"
    project_dir = setup_project_directories(base_dir, project_name, blueprint_slug)
    print(f"Using project: {project_name}")
    print(f"Project directory: {project_dir}")
    
    if args.output_dir != "output/iac":
        sys.stderr.write(
            f"Warning: --output-dir is ignored when using project structure. "
            f"Output will be written to: {project_dir / 'output' / 'iac'}\n"
        )
    if args.guidance_dir != "output/documentation":
        sys.stderr.write(
            f"Warning: --guidance-dir is ignored when using project structure. "
            f"Documentation will be written to: {project_dir / 'output' / 'documentation'}\n"
        )
    output_base_dir = project_dir / "output" / "iac"
    guidance_base_dir = project_dir / "output" / "documentation"

    # Load answers
    print(f"Loading answers from {answers_path}...")
    answers = load_yaml(answers_path) or {}

    # Render IaC code
    print(f"Rendering blueprint '{blueprint_slug}' for language '{args.lang}'...")
    rendered_code, code_rendered, code_skipped = render_blueprint_code(
        blueprint_dir, args.lang, answers, base_dir
    )

    # Generate IaC output filename with slug-based naming (e.g., account-creation_20260205.sql)
    output_dir = output_base_dir / args.lang
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    extension = get_language_extension(args.lang)
    output_file = output_dir / f"{blueprint_slug}_{date_str}.{extension}"

    # Write IaC output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_code)

    print(f"Successfully rendered IaC to: {output_file}")
    print(f"  Steps rendered: {code_rendered}, skipped (missing vars): {code_skipped}")
    print(f"  Total size: {len(rendered_code)} characters")

    # Render guidance documents (unless skipped)
    if not args.skip_guidance:
        print("\nRendering guidance documents...")
        rendered_guidance, guide_rendered, guide_skipped = render_blueprint_guidance(
            blueprint_dir, answers, base_dir
        )

        # Generate guidance output filename with slug-based naming
        guidance_dir = guidance_base_dir
        guidance_dir.mkdir(parents=True, exist_ok=True)

        guidance_file = guidance_dir / f"{blueprint_slug}_{date_str}.md"

        # Write guidance output
        with open(guidance_file, "w", encoding="utf-8") as f:
            f.write(rendered_guidance)

        print(f"Successfully rendered guidance to: {guidance_file}")
        print(
            f"  Steps rendered: {guide_rendered}, skipped (missing vars): {guide_skipped}"
        )
        print(f"  Total size: {len(rendered_guidance)} characters")


if __name__ == "__main__":
    main()
