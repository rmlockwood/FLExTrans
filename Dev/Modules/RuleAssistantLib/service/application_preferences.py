"""Application Preferences - QSettings wrapper"""

from PyQt6.QtCore import QSettings


class ApplicationPreferences:
    """Manages application preferences using Qt QSettings.

    Preference keys are named to match Java Preferences API names for
    backwards compatibility.
    """

    # Key constants
    LAST_LOCALE_LANGUAGE = "lastLocaleLanguage"
    LAST_SELECTED_RULE = "lastSelectedRule"
    LAST_SELECTED_DISJOINT_FEATURE_SET = "lastSelectedDisjointFeatureSet"
    LAST_WINDOW = "lastWindow"
    POSITION_X = "PositionX"
    POSITION_Y = "PositionY"
    WIDTH = "Width"
    HEIGHT = "Height"
    MAXIMIZED = "Maximized"
    LAST_SPLIT_PANE_POSITION = "lastSplitPanePosition"
    LAST_CATEGORY_CHOOSER = "lastCategoryChooser"
    LAST_FEATURE_CHOOSER = "lastFeatureChooser"
    DISJOINT_FEATURE_EDITOR = "DISJOINT_FEATURE_EDITOR_"

    def __init__(self):
        """Initialize QSettings with SIL organization and FLExTransRuleGenerator app."""
        self._settings = QSettings("SIL", "FLExTransRuleGenerator")

    def get_last_locale_language(self, default: str = "en") -> str:
        """Get the last selected UI language.

        Args:
            default: Default language code if not set

        Returns:
            Language code (e.g., "en", "fr", "es")
        """
        return self._settings.value(self.LAST_LOCALE_LANGUAGE, default)

    def set_last_locale_language(self, lang_code: str) -> None:
        """Set the last selected UI language.

        Args:
            lang_code: Language code to save
        """
        self._settings.setValue(self.LAST_LOCALE_LANGUAGE, lang_code)

    def get_last_selected_rule(self, default: int = 0) -> int:
        """Get the last selected rule index.

        Args:
            default: Default index if not set

        Returns:
            Rule index
        """
        return int(self._settings.value(self.LAST_SELECTED_RULE, default))

    def set_last_selected_rule(self, index: int) -> None:
        """Set the last selected rule index.

        Args:
            index: Rule index to save
        """
        self._settings.setValue(self.LAST_SELECTED_RULE, index)

    def get_last_selected_disjoint_feature_set(self, default: int = 0) -> int:
        """Get the last selected disjoint feature set index.

        Args:
            default: Default index if not set

        Returns:
            Feature set index
        """
        return int(self._settings.value(self.LAST_SELECTED_DISJOINT_FEATURE_SET, default))

    def set_last_selected_disjoint_feature_set(self, index: int) -> None:
        """Set the last selected disjoint feature set index.

        Args:
            index: Feature set index to save
        """
        self._settings.setValue(self.LAST_SELECTED_DISJOINT_FEATURE_SET, index)

    def get_window_position_x(self, default: int = 100) -> int:
        """Get saved window X position."""
        return int(self._settings.value(
            f"{self.LAST_WINDOW}{self.POSITION_X}", default
        ))

    def set_window_position_x(self, x: int) -> None:
        """Save window X position."""
        self._settings.setValue(f"{self.LAST_WINDOW}{self.POSITION_X}", x)

    def get_window_position_y(self, default: int = 100) -> int:
        """Get saved window Y position."""
        return int(self._settings.value(
            f"{self.LAST_WINDOW}{self.POSITION_Y}", default
        ))

    def set_window_position_y(self, y: int) -> None:
        """Save window Y position."""
        self._settings.setValue(f"{self.LAST_WINDOW}{self.POSITION_Y}", y)

    def get_window_width(self, default: int = 660) -> int:
        """Get saved window width."""
        return int(self._settings.value(f"{self.LAST_WINDOW}{self.WIDTH}", default))

    def set_window_width(self, width: int) -> None:
        """Save window width."""
        self._settings.setValue(f"{self.LAST_WINDOW}{self.WIDTH}", width)

    def get_window_height(self, default: int = 1000) -> int:
        """Get saved window height."""
        return int(self._settings.value(f"{self.LAST_WINDOW}{self.HEIGHT}", default))

    def set_window_height(self, height: int) -> None:
        """Save window height."""
        self._settings.setValue(f"{self.LAST_WINDOW}{self.HEIGHT}", height)

    def get_window_maximized(self, default: bool = False) -> bool:
        """Get saved window maximized state."""
        return self._settings.value(
            f"{self.LAST_WINDOW}{self.MAXIMIZED}", default, type=bool
        )

    def set_window_maximized(self, maximized: bool) -> None:
        """Save window maximized state."""
        self._settings.setValue(f"{self.LAST_WINDOW}{self.MAXIMIZED}", maximized)

    def get_split_pane_position(self, default: float = 0.3) -> float:
        """Get saved split pane divider position."""
        return float(self._settings.value(self.LAST_SPLIT_PANE_POSITION, default))

    def set_split_pane_position(self, position: float) -> None:
        """Save split pane divider position."""
        self._settings.setValue(self.LAST_SPLIT_PANE_POSITION, position)

    def sync(self) -> None:
        """Sync settings to storage."""
        self._settings.sync()
