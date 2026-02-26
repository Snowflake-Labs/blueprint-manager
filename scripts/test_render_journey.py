#!/usr/bin/env python3

# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License. See LICENSE file.

"""
Unit tests for render_journey.py

Tests focus on the conditional variable handling fix (CXE-13814):
Templates should only be skipped when a null/missing variable would actually
be needed during rendering, taking into account conditional logic.
"""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from render_journey import check_template_renderable


class TestConditionalVariableHandling(TestCase):
    """Test that conditional variable patterns are handled correctly."""

    def setUp(self):
        """Create a temporary directory structure for test templates."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.base_dir),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_template(self, name, content):
        """Create a test template file."""
        template_path = self.base_dir / name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)
        return template_path

    def test_conditional_scim_not_required_for_manual_idp(self):
        """scim_admin_users should not be required when identity_provider is Manual."""
        template = self.create_template(
            "test_template.jinja",
            """
{% if identity_provider != "None - Manual User Management" %}
  SCIM Users: {{ scim_admin_users }}
{% else %}
  Manual Users: {{ manual_admin_users }}
{% endif %}
""",
        )
        answers = {
            "identity_provider": "None - Manual User Management",
            "scim_admin_users": None,  # Should NOT cause skip (inactive branch)
            "manual_admin_users": ["ADMIN"],
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertTrue(
            can_render,
            f"Template should render when null var is in inactive branch. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )

    def test_conditional_scim_required_for_okta_idp(self):
        """scim_admin_users should be required when identity_provider is Okta."""
        template = self.create_template(
            "test_template2.jinja",
            """
{% if identity_provider != "None - Manual User Management" %}
  SCIM Users: {{ scim_admin_users }}
{% else %}
  Manual Users: {{ manual_admin_users }}
{% endif %}
""",
        )
        answers = {
            "identity_provider": "Okta",
            "scim_admin_users": None,  # SHOULD cause skip (active branch)
            "manual_admin_users": ["ADMIN"],
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(
            can_render, "Template should NOT render when null var is in active branch"
        )
        self.assertIn("scim_admin_users", null_vars)

    def test_conditional_manual_required_for_manual_idp(self):
        """manual_admin_users should be required when identity_provider is Manual."""
        template = self.create_template(
            "test_template3.jinja",
            """
{% if identity_provider != "None - Manual User Management" %}
  SCIM Users: {{ scim_admin_users }}
{% else %}
  Manual Users: {{ manual_admin_users }}
{% endif %}
""",
        )
        answers = {
            "identity_provider": "None - Manual User Management",
            "scim_admin_users": ["ADMIN"],  # Not needed
            "manual_admin_users": None,  # SHOULD cause skip (active branch)
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(
            can_render, "Template should NOT render when null var is in active branch"
        )
        self.assertIn("manual_admin_users", null_vars)

    def test_nested_conditionals(self):
        """Nested conditionals should be handled correctly."""
        template = self.create_template(
            "nested_template.jinja",
            """
{% if enable_feature %}
  {% if feature_type == "basic" %}
    Basic: {{ basic_config }}
  {% else %}
    Advanced: {{ advanced_config }}
  {% endif %}
{% else %}
  Feature disabled
{% endif %}
""",
        )
        # Feature disabled - neither basic_config nor advanced_config should be needed
        answers = {
            "enable_feature": False,
            "feature_type": "basic",
            "basic_config": None,
            "advanced_config": None,
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertTrue(
            can_render,
            f"Template should render when null vars are in disabled feature block. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )

    def test_nested_conditionals_active_inner_branch(self):
        """Active inner branch should require its variables."""
        template = self.create_template(
            "nested_template2.jinja",
            """
{% if enable_feature %}
  {% if feature_type == "basic" %}
    Basic: {{ basic_config }}
  {% else %}
    Advanced: {{ advanced_config }}
  {% endif %}
{% else %}
  Feature disabled
{% endif %}
""",
        )
        # Feature enabled, basic type - basic_config is needed
        answers = {
            "enable_feature": True,
            "feature_type": "basic",
            "basic_config": None,  # SHOULD cause skip
            "advanced_config": None,  # Not needed
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when null var in active inner branch")
        self.assertIn("basic_config", null_vars)

    def test_missing_variable_detection(self):
        """Missing (not just null) variables should be detected."""
        template = self.create_template(
            "missing_var_template.jinja",
            """Hello {{ user_name }}!""",
        )
        answers = {}  # user_name not in answers at all
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when required var is missing")
        self.assertIn("user_name", missing_vars)

    def test_all_variables_present_and_valid(self):
        """Template with all required variables present should render."""
        template = self.create_template(
            "valid_template.jinja",
            """Hello {{ user_name }}! Welcome to {{ location }}.""",
        )
        answers = {"user_name": "Alice", "location": "Snowflake"}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertTrue(
            can_render,
            f"Template should render when all vars present. Missing: {missing_vars}, Null: {null_vars}",
        )

    def test_for_loop_with_null_list(self):
        """For loop over null list should be detected."""
        template = self.create_template(
            "loop_template.jinja",
            """
{% for item in items %}
  - {{ item }}
{% endfor %}
""",
        )
        answers = {"items": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when iterating over null")
        self.assertIn("items", null_vars)

    def test_conditional_equality_with_null_tracker(self):
        """Equality comparisons with NullTracker should work for conditions."""
        template = self.create_template(
            "equality_template.jinja",
            """
{% if var == "expected_value" %}
  Got expected
{% else %}
  Got something else: {{ other_var }}
{% endif %}
""",
        )
        # var is null, but we're only comparing it, not using its value
        answers = {
            "var": None,
            "other_var": "available",
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        # Should render because:
        # - var == "expected_value" evaluates to False (null != "expected_value")
        # - We go to else branch which uses other_var (which is available)
        self.assertTrue(
            can_render,
            f"Template should render when null var is only used in condition. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )


class TestMultipleConditionalPatterns(TestCase):
    """Test multiple conditional patterns in the same template."""

    def setUp(self):
        """Create a temporary directory structure for test templates."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.base_dir),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_template(self, name, content):
        """Create a test template file."""
        template_path = self.base_dir / name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)
        return template_path

    def test_multiple_independent_conditionals(self):
        """Multiple independent conditionals should all be respected."""
        template = self.create_template(
            "multi_cond.jinja",
            """
{% if enable_feature_a %}
  Feature A: {{ feature_a_config }}
{% endif %}

{% if enable_feature_b %}
  Feature B: {{ feature_b_config }}
{% endif %}

Always shown: {{ required_var }}
""",
        )
        # Both features disabled - their configs shouldn't be needed
        answers = {
            "enable_feature_a": False,
            "enable_feature_b": False,
            "feature_a_config": None,
            "feature_b_config": None,
            "required_var": "present",
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertTrue(
            can_render,
            f"Template should render when all null vars are in disabled blocks. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )

    def test_one_active_one_inactive_conditional(self):
        """One active and one inactive conditional - only active needs vars."""
        template = self.create_template(
            "mixed_cond.jinja",
            """
{% if enable_feature_a %}
  Feature A: {{ feature_a_config }}
{% endif %}

{% if enable_feature_b %}
  Feature B: {{ feature_b_config }}
{% endif %}
""",
        )
        # Feature A enabled (needs config), Feature B disabled (doesn't need config)
        answers = {
            "enable_feature_a": True,
            "enable_feature_b": False,
            "feature_a_config": "configured",  # Needed and present
            "feature_b_config": None,  # Not needed (disabled)
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertTrue(
            can_render,
            f"Template should render. Missing: {missing_vars}, Null: {null_vars}",
        )


class TestNullTrackerEdgeCases(TestCase):
    """Test edge cases for NullTracker behavior.
    
    These tests document known behavior patterns for:
    - {% if var is none %} pattern (known limitation)
    - {% if not var %} pattern (intentionally strict)
    - Reversed comparisons {% if 'value' == var %}
    """

    def setUp(self):
        """Create a temporary directory structure for test templates."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.base_dir),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_template(self, name, content):
        """Create a test template file."""
        template_path = self.base_dir / name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)
        return template_path

    def test_is_none_pattern_known_limitation(self):
        """{% if var is none %} - KNOWN LIMITATION: NullTracker is not actually None.
        
        Jinja2's 'is none' test uses identity comparison (x is None), which will
        return False for NullTracker objects. Templates should use 
        {% if var == None %} instead for null-checking that works with NullTracker.
        
        This test documents the current behavior, not the ideal behavior.
        """
        template = self.create_template(
            "is_none_template.jinja",
            """
{% if var is none %}
  var is none
{% else %}
  var is not none, value: {{ other_var }}
{% endif %}
""",
        )
        # var is null but 'is none' won't recognize NullTracker as None
        answers = {
            "var": None,
            "other_var": "fallback",
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        # This should render because 'var is none' returns False for NullTracker
        # (NullTracker is not actually None), so we go to the else branch
        self.assertTrue(
            can_render,
            f"Template should render (known limitation - 'is none' returns False for NullTracker). "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )

    def test_not_var_pattern_raises_error(self):
        """{% if not var %} - Intentionally raises error for null variables.
        
        Using a null variable in boolean context (e.g., {% if not var %}) raises
        an error because the intent is usually to check the variable's truthiness,
        which requires knowing its actual value. This is intentional strict behavior.
        """
        template = self.create_template(
            "not_var_template.jinja",
            """
{% if not var %}
  var is falsy
{% else %}
  var is truthy
{% endif %}
""",
        )
        answers = {"var": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        # Should NOT render - accessing boolean value of null var is intentionally strict
        self.assertFalse(
            can_render,
            "Template should NOT render when using null var in boolean context ({% if not var %})",
        )
        self.assertIn("var", null_vars)

    def test_reversed_equality_comparison(self):
        """{% if 'value' == var %} - Reversed comparison should work."""
        template = self.create_template(
            "reversed_eq_template.jinja",
            """
{% if "expected_value" == var %}
  Got expected
{% else %}
  Got something else: {{ other_var }}
{% endif %}
""",
        )
        # var is null, comparison reversed but should still work
        answers = {
            "var": None,
            "other_var": "available",
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        # Should render - "expected_value" == NullTracker will call NullTracker.__eq__
        # via Python's comparison fallback mechanism
        self.assertTrue(
            can_render,
            f"Template should render with reversed comparison. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )

    def test_equality_with_none_literal(self):
        """{% if var == None %} - Should work as alternative to 'is none'."""
        template = self.create_template(
            "eq_none_template.jinja",
            """
{% if var == None %}
  var is null - use fallback
{% else %}
  var has value: {{ var }}
{% endif %}
""",
        )
        answers = {"var": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        # Should render - NullTracker.__eq__(None) returns True
        self.assertTrue(
            can_render,
            f"Template should render using '== None' pattern. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )


class TestNullTrackerComparisonOperators(TestCase):
    """Test that comparison operators raise UndefinedError for null variables.
    
    These tests ensure that using comparison operators (<, >, <=, >=) with null
    variables raises UndefinedError instead of TypeError, allowing the exception
    to be properly caught and handled by check_template_renderable().
    """

    def setUp(self):
        """Create a temporary directory structure for test templates."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.base_dir),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_template(self, name, content):
        """Create a test template file."""
        template_path = self.base_dir / name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)
        return template_path

    def test_greater_than_comparison_with_null(self):
        """{% if var > 0 %} with null var should report as null, not crash."""
        template = self.create_template(
            "gt_template.jinja",
            """
{% if count > 0 %}
  Count is positive: {{ count }}
{% else %}
  Count is zero or negative
{% endif %}
""",
        )
        answers = {"count": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when comparing null var with >")
        self.assertIn("count", null_vars)

    def test_less_than_comparison_with_null(self):
        """{% if var < 100 %} with null var should report as null, not crash."""
        template = self.create_template(
            "lt_template.jinja",
            """
{% if limit < 100 %}
  Under limit
{% else %}
  At or over limit
{% endif %}
""",
        )
        answers = {"limit": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when comparing null var with <")
        self.assertIn("limit", null_vars)

    def test_greater_equal_comparison_with_null(self):
        """{% if var >= 10 %} with null var should report as null, not crash."""
        template = self.create_template(
            "ge_template.jinja",
            """
{% if threshold >= 10 %}
  High threshold
{% else %}
  Low threshold
{% endif %}
""",
        )
        answers = {"threshold": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when comparing null var with >=")
        self.assertIn("threshold", null_vars)

    def test_less_equal_comparison_with_null(self):
        """{% if var <= 5 %} with null var should report as null, not crash."""
        template = self.create_template(
            "le_template.jinja",
            """
{% if max_retries <= 5 %}
  Few retries allowed
{% else %}
  Many retries allowed
{% endif %}
""",
        )
        answers = {"max_retries": None}
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render, "Template should NOT render when comparing null var with <=")
        self.assertIn("max_retries", null_vars)

    def test_comparison_in_inactive_branch_does_not_crash(self):
        """Comparison with null var in inactive branch should not cause issues."""
        template = self.create_template(
            "inactive_comparison_template.jinja",
            """
{% if enable_limits %}
  {% if limit > 100 %}
    High limit: {{ limit }}
  {% else %}
    Normal limit
  {% endif %}
{% else %}
  Limits disabled
{% endif %}
""",
        )
        answers = {
            "enable_limits": False,
            "limit": None,  # In inactive branch, should not cause problems
        }
        can_render, missing_vars, null_vars = check_template_renderable(
            template, answers, self.jinja_env, self.base_dir
        )
        self.assertTrue(
            can_render,
            f"Template should render when comparison with null is in inactive branch. "
            f"Missing: {missing_vars}, Null: {null_vars}",
        )


class TestTaskMetadataLoading(TestCase):
    """Test task metadata loading from meta.yaml (CXE-14251)."""

    def setUp(self):
        """Create a temporary directory structure for test blueprints."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_meta_yaml(self, content):
        """Create a test meta.yaml file."""
        meta_file = self.blueprint_dir / "meta.yaml"
        with open(meta_file, "w") as f:
            yaml.dump(content, f)
        return meta_file

    def test_load_task_metadata_with_valid_tasks(self):
        """Task metadata should be loaded correctly from meta.yaml."""
        from render_journey import load_task_metadata

        self.create_meta_yaml({
            "name": "Test Blueprint",
            "tasks": [
                {
                    "slug": "task-1",
                    "title": "First Task",
                    "summary": "This is the first task",
                    "external_requirements": ["Requirement 1"],
                    "personas": ["Admin"],
                    "role_requirements": ["ACCOUNTADMIN"],
                    "steps": [
                        {"slug": "step-1", "title": "Step One"},
                        {"slug": "step-2", "title": "Step Two"},
                    ],
                },
                {
                    "slug": "task-2",
                    "title": "Second Task",
                    "steps": [
                        {"slug": "step-3", "title": "Step Three"},
                    ],
                },
            ],
        })

        tasks = load_task_metadata(self.blueprint_dir)

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["slug"], "task-1")
        self.assertEqual(tasks[0]["title"], "First Task")
        self.assertEqual(tasks[0]["summary"], "This is the first task")
        self.assertEqual(tasks[0]["external_requirements"], ["Requirement 1"])
        self.assertEqual(tasks[0]["personas"], ["Admin"])
        self.assertEqual(tasks[0]["role_requirements"], ["ACCOUNTADMIN"])
        self.assertEqual(len(tasks[0]["steps"]), 2)
        self.assertEqual(tasks[0]["steps"][0]["slug"], "step-1")

    def test_load_task_metadata_without_tasks(self):
        """Empty list should be returned when no tasks defined."""
        from render_journey import load_task_metadata

        self.create_meta_yaml({
            "name": "Test Blueprint",
            "steps": ["step-1", "step-2"],
        })

        tasks = load_task_metadata(self.blueprint_dir)

        self.assertEqual(tasks, [])

    def test_load_task_metadata_missing_file(self):
        """Empty list should be returned when meta.yaml doesn't exist."""
        from render_journey import load_task_metadata

        # Create a different directory without meta.yaml
        empty_dir = self.base_dir / "empty-blueprint"
        empty_dir.mkdir(parents=True)

        tasks = load_task_metadata(empty_dir)

        self.assertEqual(tasks, [])

    def test_load_task_metadata_with_string_steps(self):
        """Steps defined as strings should be normalized to dicts."""
        from render_journey import load_task_metadata

        self.create_meta_yaml({
            "name": "Test Blueprint",
            "tasks": [
                {
                    "slug": "task-1",
                    "title": "First Task",
                    "steps": ["step-1", "step-2"],  # String format
                },
            ],
        })

        tasks = load_task_metadata(self.blueprint_dir)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(tasks[0]["steps"]), 2)
        self.assertEqual(tasks[0]["steps"][0]["slug"], "step-1")
        self.assertEqual(tasks[0]["steps"][0]["title"], "")

    def test_load_task_metadata_with_defaults(self):
        """Missing optional fields should have default values."""
        from render_journey import load_task_metadata

        self.create_meta_yaml({
            "name": "Test Blueprint",
            "tasks": [
                {
                    "slug": "minimal-task",
                    "title": "Minimal Task",
                },
            ],
        })

        tasks = load_task_metadata(self.blueprint_dir)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["summary"], "")
        self.assertEqual(tasks[0]["external_requirements"], [])
        self.assertEqual(tasks[0]["personas"], [])
        self.assertEqual(tasks[0]["role_requirements"], [])
        self.assertEqual(tasks[0]["steps"], [])


class TestTaskOverviewLoading(TestCase):
    """Test task overview content loading from markdown files (CXE-14251)."""

    def setUp(self):
        """Create a temporary directory structure for test blueprints."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.tasks_dir = self.blueprint_dir / "tasks"
        self.tasks_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_task_overview(self, task_slug, content):
        """Create a test task overview markdown file."""
        task_file = self.tasks_dir / f"{task_slug}.md"
        task_file.write_text(content)
        return task_file

    def test_load_task_overview_existing_file(self):
        """Task overview content should be loaded from markdown file."""
        from render_journey import load_task_overview

        expected_content = "# Task Overview\n\nThis is the task description."
        self.create_task_overview("my-task", expected_content)

        content = load_task_overview(self.blueprint_dir, "my-task")

        self.assertEqual(content, expected_content)

    def test_load_task_overview_missing_file(self):
        """None should be returned when task file doesn't exist."""
        from render_journey import load_task_overview

        content = load_task_overview(self.blueprint_dir, "nonexistent-task")

        self.assertIsNone(content)

    def test_load_task_overview_missing_tasks_dir(self):
        """None should be returned when tasks directory doesn't exist."""
        from render_journey import load_task_overview

        # Create blueprint dir without tasks subdirectory
        empty_blueprint = self.base_dir / "empty-blueprint"
        empty_blueprint.mkdir(parents=True)

        content = load_task_overview(empty_blueprint, "any-task")

        self.assertIsNone(content)


class TestTaskStepMapping(TestCase):
    """Test task-to-step mapping functionality (CXE-14251)."""

    def test_build_task_step_mapping_basic(self):
        """Step mapping should correctly associate steps with tasks."""
        from render_journey import build_task_step_mapping

        tasks = [
            {
                "slug": "task-1",
                "title": "First Task",
                "steps": [
                    {"slug": "step-1", "title": "Step One"},
                    {"slug": "step-2", "title": "Step Two"},
                ],
            },
            {
                "slug": "task-2",
                "title": "Second Task",
                "steps": [
                    {"slug": "step-3", "title": "Step Three"},
                ],
            },
        ]

        mapping = build_task_step_mapping(tasks)

        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping["step-1"]["task_slug"], "task-1")
        self.assertEqual(mapping["step-1"]["task_title"], "First Task")
        self.assertEqual(mapping["step-1"]["task_index"], 0)
        self.assertEqual(mapping["step-1"]["step_index"], 0)
        self.assertEqual(mapping["step-1"]["total_steps_in_task"], 2)

        self.assertEqual(mapping["step-2"]["step_index"], 1)

        self.assertEqual(mapping["step-3"]["task_slug"], "task-2")
        self.assertEqual(mapping["step-3"]["task_index"], 1)
        self.assertEqual(mapping["step-3"]["step_index"], 0)
        self.assertEqual(mapping["step-3"]["total_steps_in_task"], 1)

    def test_build_task_step_mapping_empty(self):
        """Empty mapping should be returned for empty tasks list."""
        from render_journey import build_task_step_mapping

        mapping = build_task_step_mapping([])

        self.assertEqual(mapping, {})

    def test_get_progress_info_basic(self):
        """Progress info should provide accurate position information."""
        from render_journey import build_task_step_mapping, get_progress_info

        tasks = [
            {
                "slug": "task-1",
                "title": "First Task",
                "steps": [
                    {"slug": "step-1", "title": "Step One"},
                    {"slug": "step-2", "title": "Step Two"},
                ],
            },
            {
                "slug": "task-2",
                "title": "Second Task",
                "steps": [
                    {"slug": "step-3", "title": "Step Three"},
                ],
            },
        ]

        mapping = build_task_step_mapping(tasks)
        total_tasks = len(tasks)

        # Check first step
        progress = get_progress_info("step-1", mapping, total_tasks)
        self.assertEqual(progress["task_number"], 1)
        self.assertEqual(progress["total_tasks"], 2)
        self.assertEqual(progress["step_number"], 1)
        self.assertEqual(progress["total_steps_in_task"], 2)
        self.assertFalse(progress["is_last_step_in_task"])
        self.assertFalse(progress["is_last_task"])

        # Check last step in first task
        progress = get_progress_info("step-2", mapping, total_tasks)
        self.assertTrue(progress["is_last_step_in_task"])
        self.assertFalse(progress["is_last_task"])

        # Check last step in last task
        progress = get_progress_info("step-3", mapping, total_tasks)
        self.assertTrue(progress["is_last_step_in_task"])
        self.assertTrue(progress["is_last_task"])

    def test_get_progress_info_unknown_step(self):
        """None should be returned for unknown step slugs."""
        from render_journey import get_progress_info

        progress = get_progress_info("unknown-step", {}, 0)

        self.assertIsNone(progress)


class TestBackwardCompatibility(TestCase):
    """Test that blueprints without task definitions render normally (CXE-14251)."""

    def setUp(self):
        """Create a temporary directory structure for test blueprints."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)
        
        # Create a step directory with minimal content
        self.step_dir = self.blueprint_dir / "test-step"
        self.step_dir.mkdir()

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_meta_yaml(self, content):
        """Create a test meta.yaml file."""
        meta_file = self.blueprint_dir / "meta.yaml"
        with open(meta_file, "w") as f:
            yaml.dump(content, f)
        return meta_file

    def create_step_template(self, content):
        """Create a test code template."""
        template_file = self.step_dir / "code.sql.jinja"
        template_file.write_text(content)
        return template_file

    def test_render_without_task_context(self):
        """Rendering should work without task context (backward compatibility)."""
        from render_journey import render_blueprint_code

        self.create_meta_yaml({
            "name": "Legacy Blueprint",
            "steps": ["test-step"],
        })
        self.create_step_template("-- Simple SQL\nSELECT 1;")

        rendered, rendered_count, skipped_count = render_blueprint_code(
            self.blueprint_dir, "sql", {}, self.base_dir
        )

        self.assertIn("Legacy Blueprint", rendered)
        self.assertIn("SELECT 1", rendered)
        self.assertEqual(rendered_count, 1)

    def test_render_with_empty_task_context(self):
        """Rendering should work with empty task context."""
        from render_journey import render_blueprint_code

        self.create_meta_yaml({
            "name": "Blueprint Without Tasks",
            "steps": ["test-step"],
        })
        self.create_step_template("-- SQL code\nSELECT 2;")

        task_context = {"tasks": [], "step_mapping": {}}
        rendered, rendered_count, skipped_count = render_blueprint_code(
            self.blueprint_dir, "sql", {}, self.base_dir, task_context=task_context
        )

        self.assertIn("SELECT 2", rendered)
        self.assertEqual(rendered_count, 1)


class TestGenerateAnchor(TestCase):
    """Test anchor generation for TOC links (CXE-14253)."""

    def test_generate_anchor_basic(self):
        """Basic heading should convert to lowercase with hyphens."""
        from render_journey import generate_anchor

        anchor = generate_anchor("Task 1: Platform Foundation")
        self.assertEqual(anchor, "task-1-platform-foundation")

    def test_generate_anchor_with_special_characters(self):
        """Special characters should be removed."""
        from render_journey import generate_anchor

        anchor = generate_anchor("Step 1.1: Configure Account & Settings")
        self.assertEqual(anchor, "step-11-configure-account-settings")

    def test_generate_anchor_with_multiple_spaces(self):
        """Multiple spaces should collapse to single hyphen."""
        from render_journey import generate_anchor

        anchor = generate_anchor("Task  1:   Multiple   Spaces")
        self.assertEqual(anchor, "task-1-multiple-spaces")

    def test_generate_anchor_with_underscores(self):
        """Underscores should be converted to hyphens."""
        from render_journey import generate_anchor

        anchor = generate_anchor("my_task_name")
        self.assertEqual(anchor, "my-task-name")

    def test_generate_anchor_preserves_numbers(self):
        """Numbers should be preserved in anchors."""
        from render_journey import generate_anchor

        anchor = generate_anchor("Step 2.3: Configure 10 Settings")
        self.assertEqual(anchor, "step-23-configure-10-settings")

    def test_generate_anchor_removes_parentheses(self):
        """Parentheses and their contents should be handled."""
        from render_journey import generate_anchor

        anchor = generate_anchor("Task (Optional): Setup")
        self.assertEqual(anchor, "task-optional-setup")

    def test_generate_anchor_empty_string(self):
        """Empty string should return empty anchor."""
        from render_journey import generate_anchor

        anchor = generate_anchor("")
        self.assertEqual(anchor, "")


class TestGenerateTableOfContents(TestCase):
    """Test hierarchical TOC generation (CXE-14253)."""

    def test_generate_toc_basic(self):
        """Basic TOC should show tasks and steps with proper anchors."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                    {"slug": "step-2", "title": "Set Up Roles"},
                ],
            },
        ]
        rendered_steps = {"step-1", "step-2"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("## Table of Contents", toc)
        self.assertIn("- [Task 1: Platform Foundation](#task-1-platform-foundation)", toc)
        self.assertIn("  - [Step 1.1: Configure Account](#step-11-configure-account)", toc)
        self.assertIn("  - [Step 1.2: Set Up Roles](#step-12-set-up-roles)", toc)

    def test_generate_toc_respects_skipped_steps(self):
        """Skipped steps should not appear in TOC."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                    {"slug": "step-2", "title": "Skipped Step"},
                    {"slug": "step-3", "title": "Set Up Roles"},
                ],
            },
        ]
        # Only step-1 and step-3 were rendered
        rendered_steps = {"step-1", "step-3"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("Step 1.1: Configure Account", toc)
        self.assertIn("Step 1.2: Set Up Roles", toc)  # Note: numbered 1.2, not 1.3
        self.assertNotIn("Skipped Step", toc)

    def test_generate_toc_skips_empty_tasks(self):
        """Tasks with no rendered steps should be skipped entirely."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                ],
            },
            {
                "slug": "task-2",
                "title": "Empty Task",
                "steps": [
                    {"slug": "step-2", "title": "Skipped Step"},
                ],
            },
            {
                "slug": "task-3",
                "title": "Security Setup",
                "steps": [
                    {"slug": "step-3", "title": "Configure Auth"},
                ],
            },
        ]
        # Only steps from task-1 and task-3 were rendered
        rendered_steps = {"step-1", "step-3"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("Task 1: Platform Foundation", toc)
        self.assertIn("Task 3: Security Setup", toc)
        self.assertNotIn("Task 2", toc)
        self.assertNotIn("Empty Task", toc)

    def test_generate_toc_depth_1(self):
        """Depth 1 should only show tasks, not steps."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                    {"slug": "step-2", "title": "Set Up Roles"},
                ],
            },
        ]
        rendered_steps = {"step-1", "step-2"}

        toc = generate_table_of_contents(tasks, rendered_steps, depth=1)

        self.assertIn("- [Task 1: Platform Foundation](#task-1-platform-foundation)", toc)
        self.assertNotIn("Step 1.1", toc)
        self.assertNotIn("Step 1.2", toc)

    def test_generate_toc_depth_2_default(self):
        """Default depth 2 should show tasks and steps."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                ],
            },
        ]
        rendered_steps = {"step-1"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("Task 1: Platform Foundation", toc)
        self.assertIn("Step 1.1: Configure Account", toc)

    def test_generate_toc_empty_tasks(self):
        """Empty tasks list should return empty string."""
        from render_journey import generate_table_of_contents

        toc = generate_table_of_contents([], set())

        self.assertEqual(toc, "")

    def test_generate_toc_no_rendered_steps(self):
        """No rendered steps should result in empty TOC content."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                ],
            },
        ]
        rendered_steps = set()  # No steps rendered

        toc = generate_table_of_contents(tasks, rendered_steps)

        # TOC header is present but no tasks/steps
        self.assertIn("## Table of Contents", toc)
        self.assertNotIn("Task 1", toc)

    def test_generate_toc_multiple_tasks(self):
        """Multiple tasks should all appear with correct numbering."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "step-1", "title": "Configure Account"},
                ],
            },
            {
                "slug": "task-2",
                "title": "Security Setup",
                "steps": [
                    {"slug": "step-2", "title": "Configure Auth"},
                    {"slug": "step-3", "title": "Enable MFA"},
                ],
            },
            {
                "slug": "task-3",
                "title": "Cost Management",
                "steps": [
                    {"slug": "step-4", "title": "Set Budgets"},
                ],
            },
        ]
        rendered_steps = {"step-1", "step-2", "step-3", "step-4"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("- [Task 1: Platform Foundation](#task-1-platform-foundation)", toc)
        self.assertIn("- [Task 2: Security Setup](#task-2-security-setup)", toc)
        self.assertIn("- [Task 3: Cost Management](#task-3-cost-management)", toc)
        self.assertIn("  - [Step 1.1: Configure Account](#step-11-configure-account)", toc)
        self.assertIn("  - [Step 2.1: Configure Auth](#step-21-configure-auth)", toc)
        self.assertIn("  - [Step 2.2: Enable MFA](#step-22-enable-mfa)", toc)
        self.assertIn("  - [Step 3.1: Set Budgets](#step-31-set-budgets)", toc)

    def test_generate_toc_step_slug_fallback(self):
        """Steps without titles should use slug as display name."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": [
                    {"slug": "configure-account", "title": ""},  # Empty title
                    {"slug": "set-up-roles"},  # No title key at all
                ],
            },
        ]
        rendered_steps = {"configure-account", "set-up-roles"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("Step 1.1: configure-account", toc)
        self.assertIn("Step 1.2: set-up-roles", toc)

    def test_generate_toc_string_steps(self):
        """Steps defined as strings should work correctly."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "Platform Foundation",
                "steps": ["step-1", "step-2"],  # String format
            },
        ]
        rendered_steps = {"step-1", "step-2"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        self.assertIn("Step 1.1: step-1", toc)
        self.assertIn("Step 1.2: step-2", toc)

    def test_generate_toc_format_matches_markdown_conventions(self):
        """TOC format should match standard markdown conventions."""
        from render_journey import generate_table_of_contents

        tasks = [
            {
                "slug": "task-1",
                "title": "My Task",
                "steps": [
                    {"slug": "step-1", "title": "My Step"},
                ],
            },
        ]
        rendered_steps = {"step-1"}

        toc = generate_table_of_contents(tasks, rendered_steps)

        # Check format: unordered list with nested items
        lines = toc.strip().split("\n")
        self.assertEqual(lines[0], "## Table of Contents")
        self.assertEqual(lines[1], "")
        self.assertTrue(lines[2].startswith("- ["))  # Task line
        self.assertTrue(lines[3].startswith("  - ["))  # Step line (2-space indent)


class TestGetCurrentTask(TestCase):
    """Test get_current_task() navigation function (CXE-14254)."""

    def _make_tasks(self):
        return [
            {
                "slug": "platform-foundation",
                "title": "Platform Foundation",
                "summary": "Set up foundational infrastructure",
                "external_requirements": ["Snowflake account"],
                "personas": ["Platform Administrator"],
                "role_requirements": ["ORGADMIN"],
                "steps": [
                    {"slug": "determine-account-strategy", "title": "Determine Account Strategy"},
                    {"slug": "configure-org-name", "title": "Configure Org Name"},
                ],
            },
            {
                "slug": "platform-security",
                "title": "Platform Security",
                "summary": "Configure security and identity",
                "external_requirements": ["Identity Provider"],
                "personas": ["Security Administrator"],
                "role_requirements": ["ACCOUNTADMIN"],
                "steps": [
                    {"slug": "select-idp", "title": "Select Identity Provider"},
                    {"slug": "configure-scim", "title": "Configure SCIM"},
                    {"slug": "configure-sso", "title": "Configure SSO"},
                ],
            },
        ]

    def test_returns_correct_task_for_first_step(self):
        """Should return the first task when querying its first step."""
        from render_journey import get_current_task

        tasks = self._make_tasks()
        result = get_current_task("determine-account-strategy", tasks)

        self.assertIsNotNone(result)
        self.assertEqual(result["slug"], "platform-foundation")
        self.assertEqual(result["title"], "Platform Foundation")
        self.assertEqual(result["summary"], "Set up foundational infrastructure")
        self.assertEqual(result["task_index"], 0)
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["personas"], ["Platform Administrator"])
        self.assertEqual(result["role_requirements"], ["ORGADMIN"])
        self.assertEqual(result["external_requirements"], ["Snowflake account"])

    def test_returns_correct_task_for_second_task_step(self):
        """Should return the second task when querying one of its steps."""
        from render_journey import get_current_task

        tasks = self._make_tasks()
        result = get_current_task("configure-scim", tasks)

        self.assertIsNotNone(result)
        self.assertEqual(result["slug"], "platform-security")
        self.assertEqual(result["task_index"], 1)
        self.assertEqual(len(result["steps"]), 3)

    def test_returns_none_for_unknown_step(self):
        """Should return None for a step that doesn't exist."""
        from render_journey import get_current_task

        tasks = self._make_tasks()
        result = get_current_task("nonexistent-step", tasks)

        self.assertIsNone(result)

    def test_returns_none_for_empty_tasks(self):
        """Should return None when tasks list is empty."""
        from render_journey import get_current_task

        result = get_current_task("any-step", [])

        self.assertIsNone(result)

    def test_handles_string_steps(self):
        """Should handle tasks where steps are plain strings instead of dicts."""
        from render_journey import get_current_task

        tasks = [
            {
                "slug": "task-1",
                "title": "Task One",
                "summary": "",
                "steps": ["step-a", "step-b"],
            },
        ]
        result = get_current_task("step-b", tasks)

        self.assertIsNotNone(result)
        self.assertEqual(result["slug"], "task-1")


class TestGetRemainingSteps(TestCase):
    """Test get_remaining_steps() navigation function (CXE-14254)."""

    def _make_tasks(self):
        return [
            {
                "slug": "task-1",
                "title": "First Task",
                "steps": [
                    {"slug": "step-1", "title": "Step One"},
                    {"slug": "step-2", "title": "Step Two"},
                    {"slug": "step-3", "title": "Step Three"},
                ],
            },
            {
                "slug": "task-2",
                "title": "Second Task",
                "steps": [
                    {"slug": "step-4", "title": "Step Four"},
                    {"slug": "step-5", "title": "Step Five"},
                ],
            },
        ]

    def test_remaining_from_first_step(self):
        """Should return all subsequent steps in the task."""
        from render_journey import get_remaining_steps

        tasks = self._make_tasks()
        remaining = get_remaining_steps("step-1", tasks)

        self.assertEqual(len(remaining), 2)
        self.assertEqual(remaining[0]["slug"], "step-2")
        self.assertEqual(remaining[0]["title"], "Step Two")
        self.assertEqual(remaining[0]["step_index"], 1)
        self.assertEqual(remaining[1]["slug"], "step-3")
        self.assertEqual(remaining[1]["step_index"], 2)

    def test_remaining_from_middle_step(self):
        """Should return only steps after the current one."""
        from render_journey import get_remaining_steps

        tasks = self._make_tasks()
        remaining = get_remaining_steps("step-2", tasks)

        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["slug"], "step-3")

    def test_remaining_from_last_step_in_task(self):
        """Should return empty list when on the last step of a task."""
        from render_journey import get_remaining_steps

        tasks = self._make_tasks()
        remaining = get_remaining_steps("step-3", tasks)

        self.assertEqual(remaining, [])

    def test_respects_task_boundaries(self):
        """Should NOT include steps from the next task."""
        from render_journey import get_remaining_steps

        tasks = self._make_tasks()
        # step-3 is the last step in task-1; step-4 is in task-2
        remaining = get_remaining_steps("step-3", tasks)

        self.assertEqual(len(remaining), 0)
        slugs = [s["slug"] for s in remaining]
        self.assertNotIn("step-4", slugs)
        self.assertNotIn("step-5", slugs)

    def test_unknown_step_returns_empty(self):
        """Should return empty list for unknown step."""
        from render_journey import get_remaining_steps

        remaining = get_remaining_steps("nonexistent", self._make_tasks())

        self.assertEqual(remaining, [])

    def test_empty_tasks_returns_empty(self):
        """Should return empty list when tasks list is empty."""
        from render_journey import get_remaining_steps

        remaining = get_remaining_steps("any-step", [])

        self.assertEqual(remaining, [])

    def test_handles_string_steps(self):
        """Should handle tasks where steps are plain strings."""
        from render_journey import get_remaining_steps

        tasks = [
            {
                "slug": "task-1",
                "title": "Task",
                "steps": ["step-a", "step-b", "step-c"],
            },
        ]
        remaining = get_remaining_steps("step-a", tasks)

        self.assertEqual(len(remaining), 2)
        self.assertEqual(remaining[0]["slug"], "step-b")
        self.assertEqual(remaining[0]["title"], "")  # string steps have no title


class TestGetTaskProgress(TestCase):
    """Test get_task_progress() navigation function (CXE-14254)."""

    def _make_tasks(self):
        return [
            {
                "slug": "task-1",
                "title": "First Task",
                "steps": [
                    {"slug": "step-1", "title": "Step One"},
                    {"slug": "step-2", "title": "Step Two"},
                    {"slug": "step-3", "title": "Step Three"},
                    {"slug": "step-4", "title": "Step Four"},
                ],
            },
            {
                "slug": "task-2",
                "title": "Second Task",
                "steps": [
                    {"slug": "step-5", "title": "Step Five"},
                    {"slug": "step-6", "title": "Step Six"},
                ],
            },
        ]

    def test_first_step_progress(self):
        """First step should show 1/4 task progress and 1/6 blueprint progress."""
        from render_journey import get_task_progress

        tasks = self._make_tasks()
        progress = get_task_progress("step-1", tasks)

        self.assertIsNotNone(progress)
        # Task-level
        self.assertEqual(progress["current_task"]["slug"], "task-1")
        self.assertEqual(progress["current_task"]["title"], "First Task")
        self.assertEqual(progress["current_task"]["task_index"], 0)
        self.assertEqual(progress["current_task"]["completed_steps"], 1)
        self.assertEqual(progress["current_task"]["total_steps"], 4)
        self.assertEqual(progress["current_task"]["completion_percentage"], 25.0)
        # Blueprint-level
        self.assertEqual(progress["blueprint"]["completed_tasks"], 0)
        self.assertEqual(progress["blueprint"]["total_tasks"], 2)
        self.assertEqual(progress["blueprint"]["completed_steps"], 1)
        self.assertEqual(progress["blueprint"]["total_steps"], 6)
        self.assertAlmostEqual(progress["blueprint"]["completion_percentage"], 16.7, places=1)

    def test_last_step_in_first_task(self):
        """Last step in first task should show 100% task and 4/6 blueprint."""
        from render_journey import get_task_progress

        tasks = self._make_tasks()
        progress = get_task_progress("step-4", tasks)

        self.assertEqual(progress["current_task"]["completed_steps"], 4)
        self.assertEqual(progress["current_task"]["total_steps"], 4)
        self.assertEqual(progress["current_task"]["completion_percentage"], 100.0)
        self.assertEqual(progress["blueprint"]["completed_tasks"], 1)
        self.assertEqual(progress["blueprint"]["completed_steps"], 4)
        self.assertAlmostEqual(progress["blueprint"]["completion_percentage"], 66.7, places=1)

    def test_first_step_of_second_task(self):
        """First step of second task should show 1 completed task at blueprint level."""
        from render_journey import get_task_progress

        tasks = self._make_tasks()
        progress = get_task_progress("step-5", tasks)

        self.assertEqual(progress["current_task"]["slug"], "task-2")
        self.assertEqual(progress["current_task"]["completed_steps"], 1)
        self.assertEqual(progress["current_task"]["total_steps"], 2)
        self.assertEqual(progress["current_task"]["completion_percentage"], 50.0)
        self.assertEqual(progress["blueprint"]["completed_tasks"], 1)
        self.assertEqual(progress["blueprint"]["completed_steps"], 5)
        self.assertAlmostEqual(progress["blueprint"]["completion_percentage"], 83.3, places=1)

    def test_last_step_overall(self):
        """Last step of last task should show 100% blueprint completion."""
        from render_journey import get_task_progress

        tasks = self._make_tasks()
        progress = get_task_progress("step-6", tasks)

        self.assertEqual(progress["current_task"]["completion_percentage"], 100.0)
        self.assertEqual(progress["blueprint"]["completed_tasks"], 2)
        self.assertEqual(progress["blueprint"]["completed_steps"], 6)
        self.assertEqual(progress["blueprint"]["total_steps"], 6)
        self.assertEqual(progress["blueprint"]["completion_percentage"], 100.0)

    def test_unknown_step_returns_none(self):
        """Should return None for unknown step slug."""
        from render_journey import get_task_progress

        progress = get_task_progress("nonexistent", self._make_tasks())

        self.assertIsNone(progress)

    def test_empty_tasks_returns_none(self):
        """Should return None when tasks list is empty."""
        from render_journey import get_task_progress

        progress = get_task_progress("any-step", [])

        self.assertIsNone(progress)

    def test_single_step_task(self):
        """Single-step task should show 100% after that step."""
        from render_journey import get_task_progress

        tasks = [
            {
                "slug": "only-task",
                "title": "Only Task",
                "steps": [{"slug": "only-step", "title": "Only Step"}],
            },
        ]
        progress = get_task_progress("only-step", tasks)

        self.assertEqual(progress["current_task"]["completed_steps"], 1)
        self.assertEqual(progress["current_task"]["total_steps"], 1)
        self.assertEqual(progress["current_task"]["completion_percentage"], 100.0)
        self.assertEqual(progress["blueprint"]["completion_percentage"], 100.0)


if __name__ == "__main__":
    main()
