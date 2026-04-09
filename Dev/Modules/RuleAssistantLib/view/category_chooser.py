"""Category Chooser Dialog"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flex_category import FLExCategory
    from category import Category


class CategoryChooserDialog(QDialog):
    """Modal dialog for choosing a FLEx category."""

    def __init__(self, categories: list["FLExCategory"], current_category: Optional["Category"] = None, parent=None):
        """Initialize the category chooser.

        Args:
            categories: List of available FLExCategory objects
            current_category: The currently selected category (for pre-selection)
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Choose Category")
        self.setModal(True)
        self.resize(300, 400)

        self.categories = categories
        self.current_category = current_category
        self._chosen_category = None

        self._create_ui()
        self._populate_list()

    def _create_ui(self) -> None:
        """Create the UI layout."""
        layout = QVBoxLayout(self)

        # List of categories
        self.category_list = QListWidget()
        self.category_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.category_list.keyPressEvent = self._on_key_press
        layout.addWidget(self.category_list)

        # OK/Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _populate_list(self) -> None:
        """Populate the category list."""
        self.category_list.clear()
        current_abbr = self.current_category.name if self.current_category else None

        for i, category in enumerate(self.categories):
            item = QListWidgetItem(category.abbreviation)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.category_list.addItem(item)

            # Pre-select current category
            if current_abbr and category.abbreviation == current_abbr:
                self.category_list.setCurrentRow(i)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on category item."""
        self._chosen_category = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def _on_key_press(self, event) -> None:
        """Handle key press (Enter to confirm, Escape to cancel)."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.category_list.currentItem()
            if current_item:
                self._chosen_category = current_item.data(Qt.ItemDataRole.UserRole)
                self.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super(QListWidgetItem, self.category_list).keyPressEvent(event)

    def get_chosen_category(self) -> Optional["FLExCategory"]:
        """Get the chosen category.

        Returns:
            The selected FLExCategory or None if cancelled
        """
        if self.result() == QDialog.DialogCode.Accepted:
            if not self._chosen_category:
                current_item = self.category_list.currentItem()
                if current_item:
                    self._chosen_category = current_item.data(Qt.ItemDataRole.UserRole)
            return self._chosen_category
        return None
