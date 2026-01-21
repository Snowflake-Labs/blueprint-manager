#!/usr/bin/env python3
"""
render_journey.py

Generates consolidated IaC and guidance files based on a blueprint and an answers file.
This script renders all code templates and overview documents from steps within a blueprint,
concatenating them in order into output files.

Only steps where ALL required variables are provided in the answers file will be rendered.
Steps with missing variables are skipped entirely.
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
    """
    blueprint_id = blueprint_dir.name

    # Load meta.yaml for workflow metadata and step ordering
    meta_file = blueprint_dir / "meta.yaml"
    if not meta_file.exists():
        sys.stderr.write(
            f"Error: meta.yaml not found in blueprint directory: {blueprint_dir}\n"
        )
        sys.exit(1)

    meta = load_yaml(meta_file)
    blueprint_name = meta.get("name", blueprint_id)
    step_order = meta.get("steps", [])

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

    # Add header
    header = [
        f"{comment_char} ============================================================",
        f"{comment_char} RENDERED JOURNEY: {blueprint_name}",
        f"{comment_char} Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{comment_char} Blueprint: {blueprint_id}",
        f"{comment_char} Language: {lang}",
        f"{comment_char} ============================================================\n",
    ]
    rendered_sections.append("\n".join(header))

    # Process steps in the order defined in meta.yaml
    for step_id in step_order:
        step_path = blueprint_dir / step_id
        if not step_path.exists():
            sys.stderr.write(f"Warning: Step directory not found: {step_path}\n")
            continue

        rendered_code, step_id, missing_vars = render_step_code(
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
                    skip_header = f"SKIPPED: {step_title} ({step_id})"
                else:
                    skip_header = f"SKIPPED: {step_id}"

                # Build skip note
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
    """
    blueprint_id = blueprint_dir.name

    # Load meta.yaml for workflow metadata and step ordering
    meta_file = blueprint_dir / "meta.yaml"
    if not meta_file.exists():
        sys.stderr.write(
            f"Error: meta.yaml not found in blueprint directory: {blueprint_dir}\n"
        )
        sys.exit(1)

    meta = load_yaml(meta_file)
    blueprint_name = meta.get("name", blueprint_id)
    blueprint_overview = meta.get("overview", "")
    step_order = meta.get("steps", [])

    # Create Jinja2 environment with strict undefined checking
    jinja_env = Environment(
        loader=FileSystemLoader(base_dir),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    rendered_sections = []
    rendered_count = 0
    skipped_count = 0

    # Add header
    header = [
        f"# {blueprint_name}",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
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

    # Process steps in the order defined in meta.yaml
    step_num = 1
    for step_id in step_order:
        step_path = blueprint_dir / step_id
        if not step_path.exists():
            sys.stderr.write(f"Warning: Step directory not found: {step_path}\n")
            continue

        rendered_guidance, step_id, missing_vars = render_step_guidance(
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
                    step_heading = f"{step_title} ({step_id})"
                else:
                    step_heading = step_id

                # Build skip note
                skip_note = [
                    "",
                    f"## Step {step_num}: {step_heading}",
                    "",
                    "> ⚠️ **SKIPPED:** This step could not be rendered due to missing answers.",
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

        # Add step header
        step_header = [
            "",
            f"## Step {step_num}: {step_id}",
            "",
        ]

        rendered_sections.append("\n".join(step_header))
        rendered_sections.append(rendered_guidance)
        rendered_sections.append("\n---\n")

        rendered_count += 1
        step_num += 1

    return "\n".join(rendered_sections), rendered_count, skipped_count


def setup_project_directories(base_dir, project_name, blueprint_id):
    """
    Create project directory structure when --project is specified.
    
    Creates:
        projects/<project_name>/
        ├── answers/
        │   └── <blueprint_id>/
        └── output/
            ├── iac/
            │   └── sql/
            └── documentation/
    """
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

    project_dir = None
    if args.project:
        project_dir = setup_project_directories(base_dir, args.project, args.blueprint)
        print(f"Using project: {args.project}")
        print(f"Project directory: {project_dir}")

    blueprints_dir = base_dir / "blueprints"

    # Find workflow directory (external repo structure)
    blueprint_dir = blueprints_dir / args.blueprint
    if not blueprint_dir.exists() or not blueprint_dir.is_dir():
        sys.stderr.write(f"Error: Blueprint directory not found: {blueprint_dir}\n")
        sys.exit(1)

    # Load answers
    print(f"Loading answers from {answers_path}...")
    answers = load_yaml(answers_path) or {}

    # Render IaC code
    print(f"Rendering blueprint '{args.blueprint}' for language '{args.lang}'...")
    rendered_code, code_rendered, code_skipped = render_blueprint_code(
        blueprint_dir, args.lang, answers, base_dir
    )

    # Generate IaC output filename
    if project_dir:
        output_dir = project_dir / "output" / "iac" / args.lang
    else:
        output_dir = base_dir / args.output_dir / args.lang
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d")
    extension = get_language_extension(args.lang)
    output_file = output_dir / f"{args.blueprint}_{date_str}.{extension}"

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
            blueprint_dir, answers, base_dir
        )

        # Generate guidance output filename
        if project_dir:
            guidance_dir = project_dir / "output" / "documentation"
        else:
            guidance_dir = base_dir / args.guidance_dir
        guidance_dir.mkdir(parents=True, exist_ok=True)

        guidance_file = guidance_dir / f"{args.blueprint}_{date_str}.md"

        # Write guidance output
        with open(guidance_file, "w", encoding="utf-8") as f:
            f.write(rendered_guidance)

        print(f"✓ Successfully rendered guidance to: {guidance_file}")
        print(
            f"  Steps rendered: {guide_rendered}, skipped (missing vars): {guide_skipped}"
        )
        print(f"  Total size: {len(rendered_guidance)} characters")


if __name__ == "__main__":
    main()
