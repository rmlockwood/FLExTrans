#
#   ListChooserDialog.py
#
#   Ron Lockwood
#   SIL International
#   6/15/26
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Initial version..
#
#  A small reusable modal dialog that lets the user pick one item from a list.
#  Used by the Rule Assistant's category and feature-value choosers.

"""Generic single-item list chooser dialog."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox
from PyQt6.QtCore import Qt
from typing import Optional, Sequence, Tuple, Any


class ListChooserDialog(QDialog):
    """Modal dialog showing a list of items; returns the data behind the chosen one.

    items is a sequence of (display_text, data) pairs. The selected item's data is
    returned by chosen_data() / choose() (or None if the dialog was cancelled).
    """

    def __init__(self, title: str, items: "Sequence[Tuple[str, Any]]",
                 current_index: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(350, 400)

        layout = QVBoxLayout(self)

        self._list = QListWidget()
        for text, data in items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self._list.addItem(item)
        if 0 <= current_index < self._list.count():
            self._list.setCurrentRow(current_index)
        # Double-click or Enter on a row accepts the dialog.
        self._list.itemDoubleClicked.connect(lambda _item: self.accept())
        self._list.itemActivated.connect(lambda _item: self.accept())
        layout.addWidget(self._list)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button is not None:
            ok_button.setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def chosen_data(self) -> Optional[Any]:
        """The data behind the selected item if the dialog was accepted, else None."""
        if self.result() == QDialog.DialogCode.Accepted:
            item = self._list.currentItem()
            if item is not None:
                return item.data(Qt.ItemDataRole.UserRole)
        return None

    @staticmethod
    def choose(parent, title: str, items: "Sequence[Tuple[str, Any]]",
               current_index: int = 0) -> Optional[Any]:
        """Convenience: show the dialog and return the chosen data (or None)."""
        dialog = ListChooserDialog(title, items, current_index, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.chosen_data()
        return None
