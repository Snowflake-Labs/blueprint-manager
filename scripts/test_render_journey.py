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

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from render_journey import check_template_renderable, create_jinja_env


class BlueprintTestCase(TestCase):
    """Base class with common temp-dir + Jinja2 environment setup."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        self.jinja_env = create_jinja_env(self.base_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_template(self, name, content):
        template_path = self.base_dir / name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)
        return template_path

    def create_step(self, step_id, code_content=None, guidance_content=None, lang="sql"):
        step_dir = self.base_dir / step_id
        step_dir.mkdir(parents=True, exist_ok=True)
        if code_content:
            (step_dir / f"code.{lang}.jinja").write_text(code_content)
        if guidance_content:
            (step_dir / "dynamic.md.jinja").write_text(guidance_content)
        return step_dir


class TestConditionalVariableHandling(BlueprintTestCase):
    """Test that conditional variable patterns are handled correctly."""

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


class TestMultipleConditionalPatterns(BlueprintTestCase):
    """Test multiple conditional patterns in the same template."""

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


class TestNullTrackerEdgeCases(BlueprintTestCase):
    """Test edge cases for NullTracker behavior.
    
    These tests document known behavior patterns for:
    - {% if var is none %} pattern (known limitation)
    - {% if not var %} pattern (intentionally strict)
    - Reversed comparisons {% if 'value' == var %}
    """

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


class TestNullTrackerComparisonOperators(BlueprintTestCase):
    """Test that comparison operators raise UndefinedError for null variables.
    
    These tests ensure that using comparison operators (<, >, <=, >=) with null
    variables raises UndefinedError instead of TypeError, allowing the exception
    to be properly caught and handled by check_template_renderable().
    """

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


class TestTaskMetadataLoading(BlueprintTestCase):
    """Test task metadata loading from meta.yaml (CXE-14251)."""

    def setUp(self):
        super().setUp()
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)

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


class TestTaskOverviewLoading(BlueprintTestCase):
    """Test task overview content loading from markdown files (CXE-14251)."""

    def setUp(self):
        super().setUp()
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.tasks_dir = self.blueprint_dir / "tasks"
        self.tasks_dir.mkdir(parents=True)

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


class TestBackwardCompatibility(BlueprintTestCase):
    """Test that blueprints without task definitions render normally (CXE-14251)."""

    def setUp(self):
        super().setUp()
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)
        
        # Create a step directory with minimal content
        self.step_dir = self.blueprint_dir / "test-step"
        self.step_dir.mkdir()

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

        meta = {
            "name": "Legacy Blueprint",
            "steps": ["test-step"],
        }
        self.create_meta_yaml(meta)
        self.create_step_template("-- Simple SQL\nSELECT 1;")

        rendered, rendered_count, skipped_count = render_blueprint_code(
            self.blueprint_dir, "sql", {}, self.base_dir, meta
        )

        self.assertIn("Legacy Blueprint", rendered)
        self.assertIn("SELECT 1", rendered)
        self.assertEqual(rendered_count, 1)

    def test_render_with_empty_task_context(self):
        """Rendering should work with empty task context."""
        from render_journey import render_blueprint_code

        meta = {
            "name": "Blueprint Without Tasks",
            "steps": ["test-step"],
        }
        self.create_meta_yaml(meta)
        self.create_step_template("-- SQL code\nSELECT 2;")

        task_context = {"tasks": [], "step_mapping": {}}
        rendered, rendered_count, skipped_count = render_blueprint_code(
            self.blueprint_dir, "sql", {}, self.base_dir, meta, task_context=task_context
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


class TestRenderStepTemplate(BlueprintTestCase):
    """Test render_step_template() unified step rendering (CXE-14504)."""

    def setUp(self):
        super().setUp()
        # Create a step directory
        self.step_path = self.base_dir / "test-step"
        self.step_path.mkdir(parents=True)

    def create_template(self, name, content):
        """Create a test template file inside the step directory."""
        template_path = self.step_path / name
        template_path.write_text(content)
        return template_path

    def test_template_not_exists_returns_none(self):
        """Non-existent template file should return (None, step_id, [])."""
        from render_journey import render_step_template

        rendered, step_id, missing = render_step_template(
            self.step_path, "code.sql.jinja", {}, self.jinja_env, self.base_dir
        )

        self.assertIsNone(rendered)
        self.assertEqual(step_id, "test-step")
        self.assertEqual(missing, [])

    def test_successful_render(self):
        """Template with all variables present should render successfully."""
        from render_journey import render_step_template

        self.create_template("code.sql.jinja", "SELECT '{{ name }}';")
        rendered, step_id, missing = render_step_template(
            self.step_path, "code.sql.jinja", {"name": "Alice"}, self.jinja_env, self.base_dir
        )

        self.assertEqual(rendered, "SELECT 'Alice';")
        self.assertEqual(step_id, "test-step")
        self.assertEqual(missing, [])

    def test_missing_variable_returns_none(self):
        """Template with missing variable should return (None, step_id, [var])."""
        from render_journey import render_step_template

        self.create_template("code.sql.jinja", "SELECT '{{ name }}';")
        rendered, step_id, missing = render_step_template(
            self.step_path, "code.sql.jinja", {}, self.jinja_env, self.base_dir
        )

        self.assertIsNone(rendered)
        self.assertEqual(step_id, "test-step")
        self.assertIn("name", missing)

    def test_null_variable_in_active_branch_returns_none(self):
        """Null variable used in active branch should return (None, step_id, [var])."""
        from render_journey import render_step_template

        self.create_template("dynamic.md.jinja", "Hello {{ user }}!")
        rendered, step_id, missing = render_step_template(
            self.step_path, "dynamic.md.jinja", {"user": None}, self.jinja_env, self.base_dir
        )

        self.assertIsNone(rendered)
        self.assertEqual(step_id, "test-step")
        self.assertIn("user", missing)

    def test_null_variable_in_inactive_branch_renders(self):
        """Null variable in inactive conditional branch should render successfully."""
        from render_journey import render_step_template

        self.create_template(
            "dynamic.md.jinja",
            """{% if use_feature %}Feature: {{ feature_config }}{% else %}No feature{% endif %}""",
        )
        rendered, step_id, missing = render_step_template(
            self.step_path,
            "dynamic.md.jinja",
            {"use_feature": False, "feature_config": None},
            self.jinja_env,
            self.base_dir,
        )

        self.assertIsNotNone(rendered)
        self.assertIn("No feature", rendered)
        self.assertEqual(step_id, "test-step")
        self.assertEqual(missing, [])


class TestValidateName(TestCase):
    """Test validate_name() raises ValueError for invalid inputs (CXE-14503)."""

    def test_valid_alphanumeric(self):
        """Valid names with alphanumeric chars, hyphens, underscores should not raise."""
        from render_journey import validate_name

        validate_name("my-project_123")  # should not raise

    def test_rejects_path_traversal(self):
        """Path traversal attempts should be rejected."""
        from render_journey import validate_name

        with self.assertRaises(ValueError):
            validate_name("../etc/passwd")

    def test_rejects_spaces(self):
        """Names with spaces should be rejected."""
        from render_journey import validate_name

        with self.assertRaises(ValueError):
            validate_name("my project")

    def test_rejects_slashes(self):
        """Names with slashes should be rejected."""
        from render_journey import validate_name

        with self.assertRaises(ValueError):
            validate_name("foo/bar")

    def test_rejects_empty_string(self):
        """Empty strings should be rejected."""
        from render_journey import validate_name

        with self.assertRaises(ValueError):
            validate_name("")


class TestRenderBlueprintGuidance(BlueprintTestCase):
    """Test render_blueprint_guidance() end-to-end guidance rendering (CXE-14508)."""

    def setUp(self):
        super().setUp()
        self.blueprint_dir = self.base_dir / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)

    def _create_blueprint(self, steps, meta_extra=None):
        """Helper to create a minimal blueprint with given steps."""
        meta = {
            "name": "Test Blueprint",
            "steps": list(steps.keys()),
        }
        if meta_extra:
            meta.update(meta_extra)
        meta_file = self.blueprint_dir / "meta.yaml"
        with open(meta_file, "w") as f:
            yaml.dump(meta, f)

        for step_id, templates in steps.items():
            step_dir = self.blueprint_dir / step_id
            step_dir.mkdir(parents=True, exist_ok=True)
            if "guidance" in templates:
                (step_dir / "dynamic.md.jinja").write_text(templates["guidance"])
        return meta

    def test_minimal_blueprint_with_two_steps(self):
        """Renders a minimal blueprint with 2 steps, verifies TOC and content."""
        from render_journey import render_blueprint_guidance, build_task_step_mapping, load_task_metadata

        meta = self._create_blueprint({
            "step-1": {"guidance": "# Configure Account\n\nSet up your account."},
            "step-2": {"guidance": "# Set Up Roles\n\nCreate roles."},
        }, meta_extra={
            "tasks": [
                {
                    "slug": "task-1",
                    "title": "Platform Foundation",
                    "steps": [
                        {"slug": "step-1", "title": "Configure Account"},
                        {"slug": "step-2", "title": "Set Up Roles"},
                    ],
                },
            ],
        })

        tasks = load_task_metadata(meta)
        step_mapping = build_task_step_mapping(tasks)
        task_context = {"tasks": tasks, "step_mapping": step_mapping}

        rendered, rendered_count, skipped_count = render_blueprint_guidance(
            self.blueprint_dir, {}, self.base_dir, meta,
            date_display="2026-02-27 10:00:00", task_context=task_context,
        )

        self.assertEqual(rendered_count, 2)
        self.assertEqual(skipped_count, 0)
        # TOC is generated
        self.assertIn("Table of Contents", rendered)
        # Step headers are present
        self.assertIn("Configure Account", rendered)
        self.assertIn("Set Up Roles", rendered)
        # Content is rendered
        self.assertIn("Set up your account.", rendered)
        self.assertIn("Create roles.", rendered)

    def test_with_task_context_headers(self):
        """Task headers should appear when task context is provided."""
        from render_journey import render_blueprint_guidance, build_task_step_mapping, load_task_metadata

        meta = self._create_blueprint({
            "step-1": {"guidance": "# Step One\n\nContent."},
        }, meta_extra={
            "tasks": [
                {
                    "slug": "task-1",
                    "title": "My Task",
                    "steps": [{"slug": "step-1", "title": "Step One"}],
                },
            ],
        })

        tasks = load_task_metadata(meta)
        step_mapping = build_task_step_mapping(tasks)
        task_context = {"tasks": tasks, "step_mapping": step_mapping}

        rendered, _, _ = render_blueprint_guidance(
            self.blueprint_dir, {}, self.base_dir, meta,
            date_display="2026-02-27 10:00:00", task_context=task_context,
        )

        self.assertIn("Task 1: My Task", rendered)

    def test_skip_note_for_missing_variables(self):
        """Steps with missing variables should show skip notes."""
        from render_journey import render_blueprint_guidance

        meta = self._create_blueprint({
            "step-1": {"guidance": "# Step One\n\nHello {{ missing_var }}!"},
        })

        rendered, rendered_count, skipped_count = render_blueprint_guidance(
            self.blueprint_dir, {}, self.base_dir, meta,
            date_display="2026-02-27 10:00:00",
        )

        self.assertEqual(rendered_count, 0)
        self.assertEqual(skipped_count, 1)
        self.assertIn("SKIPPED", rendered)
        self.assertIn("missing_var", rendered)

    def test_overview_section(self):
        """Overview content from meta.yaml should appear in rendered guidance."""
        from render_journey import render_blueprint_guidance

        meta = self._create_blueprint({
            "step-1": {"guidance": "# Step One\n\nContent."},
        }, meta_extra={
            "overview": "This blueprint sets up your Snowflake environment.",
        })

        rendered, _, _ = render_blueprint_guidance(
            self.blueprint_dir, {}, self.base_dir, meta,
            date_display="2026-02-27 10:00:00",
        )

        self.assertIn("This blueprint sets up your Snowflake environment.", rendered)


class TestGetStepTitle(BlueprintTestCase):
    """Test get_step_title() title extraction from dynamic.md.jinja (CXE-14508)."""

    def test_step_with_title(self):
        """Step with dynamic.md.jinja starting with '# My Title' returns 'My Title'."""
        from render_journey import get_step_title

        step_dir = self.create_step("test-step", guidance_content="# My Title\n\nSome content.")
        title = get_step_title(step_dir)
        self.assertEqual(title, "My Title")

    def test_step_without_dynamic_file(self):
        """Step with no dynamic.md.jinja returns None."""
        from render_journey import get_step_title

        step_dir = self.base_dir / "empty-step"
        step_dir.mkdir(parents=True, exist_ok=True)
        title = get_step_title(step_dir)
        self.assertIsNone(title)

    def test_step_with_no_heading(self):
        """Step with dynamic.md.jinja that has no '# ' line returns None."""
        from render_journey import get_step_title

        step_dir = self.create_step("test-step", guidance_content="No heading here\nJust text.")
        title = get_step_title(step_dir)
        self.assertIsNone(title)

    def test_step_with_leading_whitespace_heading(self):
        """Step with leading whitespace before '# ' returns the title."""
        from render_journey import get_step_title

        step_dir = self.create_step("test-step", guidance_content="  # Indented Title\n\nContent.")
        # get_step_title strips the line before checking startswith("# ")
        title = get_step_title(step_dir)
        self.assertEqual(title, "Indented Title")

    def test_step_with_heading_not_on_first_line(self):
        """The first '# ' heading should be returned even if not on line 1."""
        from render_journey import get_step_title

        step_dir = self.create_step(
            "test-step",
            guidance_content="Some preamble\n\n# Actual Title\n\nContent.",
        )
        title = get_step_title(step_dir)
        self.assertEqual(title, "Actual Title")


class TestSetupProjectDirectories(BlueprintTestCase):
    """Test setup_project_directories() directory creation (CXE-14508)."""

    def test_creates_expected_directory_structure(self):
        """Creates the expected directory structure under a temp dir."""
        from render_journey import setup_project_directories

        project_dir = setup_project_directories(self.base_dir, "my-project", "my-blueprint")

        self.assertTrue(project_dir.exists())
        self.assertTrue((project_dir / "answers" / "my-blueprint").is_dir())
        self.assertTrue((project_dir / "output" / "iac" / "sql").is_dir())
        self.assertTrue((project_dir / "output" / "documentation").is_dir())

    def test_idempotent_calls(self):
        """Repeated calls are idempotent (exist_ok=True) - no error on second call."""
        from render_journey import setup_project_directories

        setup_project_directories(self.base_dir, "my-project", "my-blueprint")
        # Should not raise
        project_dir = setup_project_directories(self.base_dir, "my-project", "my-blueprint")
        self.assertTrue(project_dir.exists())

    def test_invalid_project_name_raises_value_error(self):
        """Invalid project names should raise ValueError."""
        from render_journey import setup_project_directories

        with self.assertRaises(ValueError):
            setup_project_directories(self.base_dir, "../bad-name", "my-blueprint")

    def test_invalid_blueprint_id_raises_value_error(self):
        """Invalid blueprint IDs should raise ValueError."""
        from render_journey import setup_project_directories

        with self.assertRaises(ValueError):
            setup_project_directories(self.base_dir, "my-project", "bad/blueprint")

    def test_returns_correct_project_path(self):
        """Return value should be the project directory path."""
        from render_journey import setup_project_directories

        project_dir = setup_project_directories(self.base_dir, "test-proj", "bp-1")
        expected = self.base_dir / "projects" / "test-proj"
        self.assertEqual(project_dir, expected)


class TestUtilityFunctions(TestCase):
    """Test get_language_extension() and get_comment_syntax() utilities (CXE-14508)."""

    def test_get_language_extension_sql(self):
        from render_journey import get_language_extension
        self.assertEqual(get_language_extension("sql"), "sql")

    def test_get_language_extension_terraform(self):
        from render_journey import get_language_extension
        self.assertEqual(get_language_extension("terraform"), "tf")

    def test_get_language_extension_unknown_passthrough(self):
        from render_journey import get_language_extension
        self.assertEqual(get_language_extension("unknown"), "unknown")

    def test_get_comment_syntax_sql(self):
        from render_journey import get_comment_syntax
        self.assertEqual(get_comment_syntax("sql"), "--")

    def test_get_comment_syntax_terraform(self):
        from render_journey import get_comment_syntax
        self.assertEqual(get_comment_syntax("terraform"), "#")

    def test_get_comment_syntax_unknown_defaults_to_hash(self):
        from render_journey import get_comment_syntax
        self.assertEqual(get_comment_syntax("unknown"), "#")


class TestCheckTemplateRenderableSyntaxError(BlueprintTestCase):
    """Test check_template_renderable with syntax-error templates (CXE-14508)."""

    def test_syntax_error_template_returns_false(self):
        """Template with Jinja2 syntax error returns (False, ['Template error: ...'], [])."""
        template = self.create_template(
            "bad_syntax.jinja",
            "{% if %}This is broken{% endif %}",
        )
        can_render, missing_vars, null_vars = check_template_renderable(
            template, {}, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render)
        self.assertTrue(len(missing_vars) > 0)
        self.assertTrue(missing_vars[0].startswith("Template error:"))
        self.assertEqual(null_vars, [])

    def test_unclosed_block_returns_false(self):
        """Template with unclosed block returns failure."""
        template = self.create_template(
            "unclosed_block.jinja",
            "{% for item in items %}{{ item }}",
        )
        can_render, missing_vars, null_vars = check_template_renderable(
            template, {"items": ["a", "b"]}, self.jinja_env, self.base_dir
        )
        self.assertFalse(can_render)
        self.assertTrue(len(missing_vars) > 0)
        self.assertTrue(missing_vars[0].startswith("Template error:"))


class TestLoadTaskMetadataNonDictEntry(BlueprintTestCase):
    """Test load_task_metadata with non-dict entries in tasks list (CXE-14508)."""

    def setUp(self):
        super().setUp()
        self.blueprint_dir = self.base_dir / "blueprints" / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)

    def test_non_dict_entries_are_skipped(self):
        """Non-dict entries in tasks list should be skipped."""
        from render_journey import load_task_metadata

        meta = {
            "name": "Test Blueprint",
            "tasks": [
                "this-is-a-string",
                {
                    "slug": "valid-task",
                    "title": "Valid Task",
                    "steps": [{"slug": "step-1", "title": "Step One"}],
                },
                42,
                None,
            ],
        }

        tasks = load_task_metadata(meta)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["slug"], "valid-task")


class TestRenderBlueprintCodeTaskContext(BlueprintTestCase):
    """Test render_blueprint_code with task-context headers (CXE-14508)."""

    def setUp(self):
        super().setUp()
        self.blueprint_dir = self.base_dir / "test-blueprint"
        self.blueprint_dir.mkdir(parents=True)

    def test_task_context_headers_appear_in_output(self):
        """Rendered code with task context should include TASK headers."""
        from render_journey import (
            render_blueprint_code, build_task_step_mapping, load_task_metadata,
        )

        # Create step directories with code templates
        step_dir = self.blueprint_dir / "step-1"
        step_dir.mkdir(parents=True)
        (step_dir / "code.sql.jinja").write_text("-- Step 1 SQL\nSELECT 1;")

        meta = {
            "name": "Test Blueprint",
            "steps": ["step-1"],
            "tasks": [
                {
                    "slug": "task-1",
                    "title": "Platform Foundation",
                    "steps": [{"slug": "step-1", "title": "Configure Account"}],
                },
            ],
        }
        meta_file = self.blueprint_dir / "meta.yaml"
        with open(meta_file, "w") as f:
            yaml.dump(meta, f)

        tasks = load_task_metadata(meta)
        step_mapping = build_task_step_mapping(tasks)
        task_context = {"tasks": tasks, "step_mapping": step_mapping}

        rendered, rendered_count, skipped_count = render_blueprint_code(
            self.blueprint_dir, "sql", {}, self.base_dir, meta,
            date_display="2026-02-27 10:00:00", task_context=task_context,
        )

        self.assertEqual(rendered_count, 1)
        self.assertIn("TASK 1: Platform Foundation", rendered)
        self.assertIn("SELECT 1", rendered)


class TestRenderStepCodeAndGuidance(BlueprintTestCase):
    """Test render_step_code/render_step_guidance via render_step_template (CXE-14508)."""

    def setUp(self):
        super().setUp()
        self.step_path = self.base_dir / "test-step"
        self.step_path.mkdir(parents=True)

    def test_render_code_with_valid_template(self):
        """Valid code template with all variables renders successfully."""
        from render_journey import render_step_template

        (self.step_path / "code.sql.jinja").write_text(
            "CREATE DATABASE {{ db_name }};"
        )
        rendered, step_id, missing = render_step_template(
            self.step_path, "code.sql.jinja",
            {"db_name": "MY_DB"}, self.jinja_env, self.base_dir,
        )

        self.assertEqual(rendered, "CREATE DATABASE MY_DB;")
        self.assertEqual(step_id, "test-step")
        self.assertEqual(missing, [])

    def test_render_code_with_missing_variables(self):
        """Code template with missing variables returns info about missing vars."""
        from render_journey import render_step_template

        (self.step_path / "code.sql.jinja").write_text(
            "CREATE DATABASE {{ db_name }};"
        )
        rendered, step_id, missing = render_step_template(
            self.step_path, "code.sql.jinja", {}, self.jinja_env, self.base_dir,
        )

        self.assertIsNone(rendered)
        self.assertEqual(step_id, "test-step")
        self.assertIn("db_name", missing)

    def test_render_code_no_template_file(self):
        """Missing code template file returns gracefully."""
        from render_journey import render_step_template

        rendered, step_id, missing = render_step_template(
            self.step_path, "code.sql.jinja", {}, self.jinja_env, self.base_dir,
        )

        self.assertIsNone(rendered)
        self.assertEqual(step_id, "test-step")
        self.assertEqual(missing, [])

    def test_render_guidance_with_valid_template(self):
        """Valid guidance template renders successfully."""
        from render_journey import render_step_template

        (self.step_path / "dynamic.md.jinja").write_text(
            "# Welcome\n\nHello {{ user_name }}!"
        )
        rendered, step_id, missing = render_step_template(
            self.step_path, "dynamic.md.jinja",
            {"user_name": "Alice"}, self.jinja_env, self.base_dir,
        )

        self.assertIn("Hello Alice!", rendered)
        self.assertEqual(step_id, "test-step")
        self.assertEqual(missing, [])

    def test_render_guidance_with_missing_variables(self):
        """Guidance template with missing variables returns missing var info."""
        from render_journey import render_step_template

        (self.step_path / "dynamic.md.jinja").write_text(
            "# Welcome\n\nHello {{ user_name }}!"
        )
        rendered, step_id, missing = render_step_template(
            self.step_path, "dynamic.md.jinja", {}, self.jinja_env, self.base_dir,
        )

        self.assertIsNone(rendered)
        self.assertIn("user_name", missing)


if __name__ == "__main__":
    main()
