#
#   ListChooserDialog.py
#
#   Ron Lockwood
#   SIL International
#   6/15/26
#
#   Version 3.16.2 - 6/16/26 - Ron Lockwood
#    Enable alternating row colors in the chooser list.
#
#   Version 3.16.1 - 6/16/26 - Ron Lockwood
#    Refactored to coding conventions; camelCase naming.
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Initial version..
#
#  A small reusable modal dialog that lets the user pick one item from a list.
#  Used by the Rule Assistant's category and feature-value choosers.

"""Generic single-item list chooser dialog."""

import os
from typing import Optional, Sequence, Tuple, Any

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import FTPaths

class ListChooserDialog(QDialog):

    """Modal dialog showing a list of items; returns the data behind the chosen one.

    items is a sequence of (display_text, data) pairs. The selected item's data is
    returned by chosenData() / choose() (or None if the dialog was cancelled).
    """

    def __init__(self, title: str, items: "Sequence[Tuple[str, Any]]", currentIndex: int = 0, parent=None):

        super().__init__(parent)

        # Basic window setup: caller's title, the FLExTrans icon, modal behavior and a reasonable default size.
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setModal(True)
        self.resize(350, 400)

        # The dialog is a simple vertical stack: the list on top, OK/Cancel buttons below.
        layout = QVBoxLayout(self)

        # Build the list widget with one row per (display_text, data) pair. We stash the data object on the item itself (under UserRole) so the chosen
        # data can be returned later without having to re-derive it from the displayed text.
        self._list = QListWidget()

        # Paint rows in alternating tones (Base / AlternateBase) so they're easier to scan, matching the rule list.
        self._list.setAlternatingRowColors(True)

        for text, data in items:

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self._list.addItem(item)

        # Pre-select the caller's current row, but only if it is a valid index.
        if 0 <= currentIndex < self._list.count():

            self._list.setCurrentRow(currentIndex)

        # Double-clicking a row, or pressing Enter on it, accepts the dialog - the same as clicking OK - so the user doesn't have to make a separate trip to the button.
        self._list.itemDoubleClicked.connect(lambda _item: self.accept())
        self._list.itemActivated.connect(lambda _item: self.accept())

        layout.addWidget(self._list)

        # Standard OK/Cancel buttons. OK is made the default so it responds to Enter.
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        okButton = buttonBox.button(QDialogButtonBox.StandardButton.Ok)

        if okButton is not None:

            okButton.setDefault(True)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(buttonBox)

    def chosenData(self) -> Optional[Any]:

        """The data behind the selected item if the dialog was accepted, else None."""

        # Only hand back data when the user actually accepted (OK / double-click / Enter); a cancelled dialog yields None.
        if self.result() == QDialog.DialogCode.Accepted:

            item = self._list.currentItem()

            if item is not None:

                return item.data(Qt.ItemDataRole.UserRole)

        return None

    @staticmethod
    def choose(parent, title: str, items: "Sequence[Tuple[str, Any]]", currentIndex: int = 0) -> Optional[Any]:

        """Convenience: build the dialog, show it modally, and return the chosen data (or None)."""

        dialog = ListChooserDialog(title, items, currentIndex, parent)

        # exec() blocks until the user accepts or cancels; only pull the data on accept.
        if dialog.exec() == QDialog.DialogCode.Accepted:

            return dialog.chosenData()

        return None
