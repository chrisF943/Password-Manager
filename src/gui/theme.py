"""
Custom color theme for fern password manager.
Replaces Flet dark theme defaults with custom palette.
"""
import flet as ft

# Background colors - user's exact hex values
DARK_BG = "#011826"  # darkest background
SURFACE = "#113340"  # card/panel background

# Accent colors
ACCENT = "#4AA63C"  # green accent
ACCENT_LIGHT = "#A4D955"  # light lime accent

# Text colors
TEXT_PRIMARY = ft.Colors.WHITE
TEXT_SECONDARY = ft.Colors.WHITE70
TEXT_HINT = ft.Colors.WHITE54

# Semantic colors (keep standard Flet for these)
ERROR = ft.Colors.RED_400
WARNING = ft.Colors.ORANGE_400
SUCCESS = ft.Colors.GREEN_400
INFO = ft.Colors.BLUE_400
