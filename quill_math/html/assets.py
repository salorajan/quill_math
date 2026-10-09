"""CSS and JavaScript assets for accessible HTML math equations with in-place tree navigation."""

from __future__ import annotations

import accessible_math_nav as amn

# Seamless asset integration: pure Python SOTA SRE-style drawer CSS and JS
NAV_CSS = amn.get_navigation_css()
NAV_JS = amn.get_navigation_script()
