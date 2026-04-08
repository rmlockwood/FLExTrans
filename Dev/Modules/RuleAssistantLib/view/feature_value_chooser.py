"""Feature Value Chooser Dialog"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QDialogButtonBox
from PyQt6.QtCore import Qt
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..flexmodel.flex_feature import FLExFeature, FLExFeatureValue
    from ..model.feature import Feature


class FeatureValueChooserDialog(QDialog):
    """Modal dialog for choosing a feature value."""

    def __init__(self, features: list["FLExFeature"], current_feature: Optional["Feature"] = None,
                 show_unmarked_label: bool = False, parent=None):
        """Initialize the feature value chooser.

        Args:
            features: List of available FLExFeature objects
            current_feature: Currently selected feature (for pre-selection)
            show_unmarked_label: Whether to show "Unmarked Feature Notice" label
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Choose Feature Value")
        self.setModal(True)
        self.resize(350, 400)

        self.features = features
        self.current_feature = current_feature
        self.show_unmarked_label = show_unmarked_label
        self._chosen_value = None

        self._create_ui()
        self._populate_list()

    def _create_ui(self) -> None:
        """Create the UI layout."""
        layout = QVBoxLayout(self)

        # Unmarked label (optional)
        if self.show_unmarked_label:
            label = QLabel("Unmarked Feature Notice")
            label.setStyleSheet("font-weight: bold; color: red;")
            layout.addWidget(label)

        # List of feature values
        self.value_list = QListWidget()
        self.value_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.value_list.keyPressEvent = self._on_key_press
        layout.addWidget(self.value_list)

        # OK/Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _populate_list(self) -> None:
        """Populate the feature value list from features."""
        self.value_list.clear()

        current_label = None
        current_value = None

        if self.current_feature:
            current_label = self.current_feature.label
            current_value = self.current_feature.get_match_or_value()

        current_index = 0
        row = 0

        for feature in self.features:
            # Skip Greek variables in unmarked mode
            if self.show_unmarked_label:
                from ..flexmodel.flex_feature import FLExFeatureValue
                values = [v for v in feature.values if not FLExFeatureValue.is_greek(v.abbreviation)]
            else:
                values = feature.values

            for value in values:
                display_text = f"{feature.name}:{value.abbreviation}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, (feature, value))
                self.value_list.addItem(item)

                # Pre-select current value
                if current_label and feature.name == current_label and value.abbreviation == current_value:
                    current_index = row

                row += 1

        if self.value_list.count() > 0:
            self.value_list.setCurrentRow(current_index)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on value item."""
        feature, value = item.data(Qt.ItemDataRole.UserRole)
        self._chosen_value = (feature, value)
        self.accept()

    def _on_key_press(self, event) -> None:
        """Handle key press (Enter to confirm, Escape to cancel)."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.value_list.currentItem()
            if current_item:
                feature, value = current_item.data(Qt.ItemDataRole.UserRole)
                self._chosen_value = (feature, value)
                self.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super(QListWidgetItem, self.value_list).keyPressEvent(event)

    def get_chosen_value(self) -> Optional[tuple["FLExFeature", "FLExFeatureValue"]]:
        """Get the chosen feature value.

        Returns:
            Tuple of (FLExFeature, FLExFeatureValue) or None if cancelled
        """
        if self.result() == QDialog.DialogCode.Accepted:
            if not self._chosen_value:
                current_item = self.value_list.currentItem()
                if current_item:
                    self._chosen_value = current_item.data(Qt.ItemDataRole.UserRole)
            return self._chosen_value
        return None
