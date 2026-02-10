#!/usr/bin/env python3
"""
Unit tests for render_journey.py

Tests focus on the conditional variable handling fix (CXE-13814):
Templates should only be skipped when a null/missing variable would actually
be needed during rendering, taking into account conditional logic.
"""

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


if __name__ == "__main__":
    main()
