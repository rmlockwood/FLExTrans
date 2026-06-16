#
#   DisjointFeaturesEditorDlg.py
#
#   Matthew Lee, Ron Lockwood - original Java version by Andy Black
#   SIL International
#   September 2023
#
#   Version 3.16.1 - 6/16/26 - Ron Lockwood
#    Apply coding conventions; camelCase naming.
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Refactored: widgets/layout now live in DisjointFeaturesEditor.ui (compiled to
#    DisjointFeaturesEditor.py as Ui_DisjointFeaturesEditorDialog). This controller
#    holds the behavior.
#
#  Controller for the Disjoint Features Editor dialog.
"""Disjoint Features Editor Dialog"""

import os

from PyQt6.QtWidgets import (
    QDialog, QTableWidgetItem, QLabel, QComboBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QCoreApplication
from typing import Optional, TYPE_CHECKING

import FTPaths
from RAutils import PhraseType, DISJOINT_NUMBER, DISJOINT_SG, DISJOINT_PL

if TYPE_CHECKING:

    from RAutils import FLExTransRuleGenerator, FLExData

from DisjointFeaturesEditor import Ui_DisjointFeaturesEditorDialog

_translate = QCoreApplication.translate

class DisjointFeaturesEditorDialog(QDialog):
    """Modal dialog for editing disjoint feature sets."""

    # The first two pairings are required, so a set always has at least this many
    # (matches the Java editor's minimumPairings = 2).
    MINIMUM_PAIRINGS = 2

    def __init__(self, generator: "FLExTransRuleGenerator", flexData: "FLExData", parent=None):

        super().__init__(parent)
        self.ui = Ui_DisjointFeaturesEditorDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.generator = generator
        self.flexData = flexData
        self._selectedIndex = -1

        # Guard against re-entrant signal handlers.
        self._updating = False

        self._setupWidgets()
        self._connectSignals()

        self._populateList()
        self._updateButtonStates()

        # Load the first set automatically when the editor opens (matches Java).
        if self.generator.disjointFeatures:

            self.setsTable.selectRow(0)

    def _setupWidgets(self) -> None:
        """Alias the .ui widgets, apply behavioral tweaks the .ui can't express, and
        populate the combos/slider that are driven by data."""

        # Alias the generated UI widgets to shorter controller-side names.
        self.setsTable = self.ui.sets_table
        self.nameField = self.ui.name_field
        self.languageCombo = self.ui.language_combo
        self.cofeatureCombo = self.ui.cofeature_combo
        self.pairingSlider = self.ui.pairing_slider
        self._addButton = self.ui.add_button
        self._deleteButton = self.ui.delete_button

        # Read-only summary grid: no editing, row selection, no focus rectangle, and a
        # stylesheet so Qt draws its own selection (removing the Win11 accent bar).
        self.setsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setsTable.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setsTable.setStyleSheet(
            "QTableView { outline: 0; }"
            "QTableView::item { border: 0; }"
            "QTableView::item:selected {"
            " background-color: palette(highlight); color: palette(highlighted-text); }"
        )
        header = self.setsTable.horizontalHeader()

        if header is not None:

            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.ui.splitter.setSizes([300, 350])

        # Language combo: store the language code as item data so the display text can
        # be translated without affecting the logic that reads the selection.
        self.languageCombo.addItem(_translate("DisjointFeaturesEditorDialog", "Source"), "source")
        self.languageCombo.addItem(_translate("DisjointFeaturesEditorDialog", "Target"), "target")

        # Collect the .ui pairing combos into the lists the logic uses.
        self.pairingFields: list[tuple[QComboBox, QComboBox]] = []
        self._pairingRowWidgets: list[tuple[QComboBox, QComboBox]] = []

        for i in range(1, 7):

            fc = getattr(self.ui, f"feature_combo_{i}")
            vc = getattr(self.ui, f"value_combo_{i}")
            self.pairingFields.append((fc, vc))
            self._pairingRowWidgets.append((fc, vc))

        self._populateCofeatureCombo(PhraseType.target)
        currentCofeature = self.cofeatureCombo.currentText()

        for fc, vc in self.pairingFields:

            self._populateFeatureCombo(fc, PhraseType.target, currentCofeature)
            self._populateValueCombo(vc, PhraseType.target, currentCofeature)

        # Numbers under the (disabled) slider; Qt sliders don't render tick labels.
        for n in range(self.MINIMUM_PAIRINGS, 7):

            if n > self.MINIMUM_PAIRINGS:

                self.ui.sliderNumbersLayout.addStretch()

            self.ui.sliderNumbersLayout.addWidget(QLabel(str(n)))

        self._updatePairingRowVisibility(self.MINIMUM_PAIRINGS)

    def _connectSignals(self) -> None:
        """Wire the .ui widgets to the controller's handlers."""

        self.setsTable.itemSelectionChanged.connect(self._onSetSelected)
        self.nameField.textChanged.connect(self._onNameChanged)
        self.languageCombo.currentIndexChanged.connect(self._onLanguageChanged)
        self.cofeatureCombo.currentIndexChanged.connect(self._onCofeatureChanged)
        self.pairingSlider.sliderMoved.connect(self._onPairingSliderChanged)
        self._addButton.clicked.connect(self._onAddSet)
        self._deleteButton.clicked.connect(self._onDeleteSet)
        self.ui.close_button.clicked.connect(self.accept)

        for i, (fc, vc) in enumerate(self.pairingFields):

            fc.currentIndexChanged.connect(lambda _idx, row=i: self._onPairingFeatureChanged(row))
            vc.currentIndexChanged.connect(lambda _idx, row=i: self._onPairingValueChanged(row))

    @staticmethod
    def _makeCell(text: str) -> QTableWidgetItem:
        """A read-only (non-editable) grid cell."""

        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        return item

    def _populateList(self) -> None:
        """Populate the disjoint feature sets table."""

        self.setsTable.setRowCount(len(self.generator.disjointFeatures))

        for i, ds in enumerate(self.generator.disjointFeatures):

            langDisplay = (_translate("DisjointFeaturesEditorDialog", "Source") if ds.language.value == "source" else _translate("DisjointFeaturesEditorDialog", "Target"))
            self.setsTable.setItem(i, 0, self._makeCell(ds.name))
            self.setsTable.setItem(i, 1, self._makeCell(langDisplay))
            self.setsTable.setItem(i, 2, self._makeCell(ds.coFeatureName))

    def _featuresForLanguage(self, language) -> list:
        """FLEx features for the given phrase (source vs target), matching Java,
        which draws on the source or target features depending on the set."""

        if not self.flexData:

            return []

        if language == PhraseType.source:

            return self.flexData.sourceData.features

        return self.flexData.targetData.features

    def _populateCofeatureCombo(self, language) -> None:
        """Distinguishing feature combo: limited to the "number" feature, as in
        the Java editor (the only feature the disjoint editor currently supports)."""

        self.cofeatureCombo.clear()
        names = [f.name for f in self._featuresForLanguage(language)
                 if f.name == DISJOINT_NUMBER]
        self.cofeatureCombo.addItems(names)

    def _populateFeatureCombo(self, combo: QComboBox, language, coFeatureName: str) -> None:
        """Subfeature combo: all FLEx feature names except the distinguishing
        (co-)feature, matching the Java flexFeatureMinusCoFeatureNames list."""

        combo.clear()
        names = sorted({f.name for f in self._featuresForLanguage(language)
                        if f.name != coFeatureName})
        combo.addItems(names)

    def _populateValueCombo(self, combo: QComboBox, language, coFeatureName: str) -> None:
        """Feature value combo: the co-feature's values, limited to "sg"/"pl", as
        in the Java editor (the only values the disjoint editor currently supports)."""

        combo.clear()

        if not coFeatureName:

            return

        for feature in self._featuresForLanguage(language):

            if feature.name == coFeatureName:

                for v in feature.values:

                    if v.abbreviation in (DISJOINT_SG, DISJOINT_PL):

                        combo.addItem(v.abbreviation)

                break

    def _updatePairingRowVisibility(self, count: int) -> None:
        """Show rows 0..count-1, hide rows count..5."""

        for i, (fc, vc) in enumerate(self._pairingRowWidgets):

            visible = i < count
            fc.setVisible(visible)
            vc.setVisible(visible)

    def _onSetSelected(self) -> None:

        rows = self.setsTable.selectedIndexes()

        if rows:

            self._selectedIndex = rows[0].row()
            self._updateEditorFromSelection()
        else:
            self._selectedIndex = -1

    def _updateEditorFromSelection(self) -> None:
        """Load selected set into editor widgets (blocks signals to avoid write-back)."""

        if not (0 <= self._selectedIndex < len(self.generator.disjointFeatures)):

            return

        self._updating = True

        try:
            ds = self.generator.disjointFeatures[self._selectedIndex]
            self.nameField.setText(ds.name)
            langIndex = self.languageCombo.findData(ds.language.value)
            self.languageCombo.setCurrentIndex(langIndex if langIndex >= 0 else 0)

            # Repopulate the combos (limited like Java) for this set's language.
            self._populateCofeatureCombo(ds.language)
            self.cofeatureCombo.setCurrentText(ds.coFeatureName)

            for fc, vc in self.pairingFields:

                self._populateFeatureCombo(fc, ds.language, ds.coFeatureName)
                self._populateValueCombo(vc, ds.language, ds.coFeatureName)

            count = max(len(ds.pairings), self.MINIMUM_PAIRINGS)
            self.pairingSlider.setValue(count)

            for i in range(6):

                fc, vc = self.pairingFields[i]

                if i < len(ds.pairings):

                    pairing = ds.pairings[i]
                    fc.setCurrentText(pairing.flexFeatureName)
                    vc.setCurrentText(pairing.coFeatureValue)
                else:
                    fc.setCurrentIndex(0)
                    vc.setCurrentIndex(0)

            self._updatePairingRowVisibility(count)
        finally:
            self._updating = False

    def _onNameChanged(self) -> None:

        if self._updating:

            return

        if 0 <= self._selectedIndex < len(self.generator.disjointFeatures):

            self.generator.disjointFeatures[self._selectedIndex].name = self.nameField.text()
            item = self.setsTable.item(self._selectedIndex, 0)

            if item:

                item.setText(self.nameField.text())

    def _onLanguageChanged(self) -> None:

        if self._updating:

            return

        if 0 <= self._selectedIndex < len(self.generator.disjointFeatures):

            lang = PhraseType.source if self.languageCombo.currentData() == "source" else PhraseType.target
            self.generator.disjointFeatures[self._selectedIndex].language = lang

    def _onCofeatureChanged(self) -> None:

        if self._updating:

            return

        if 0 <= self._selectedIndex < len(self.generator.disjointFeatures):

            ds = self.generator.disjointFeatures[self._selectedIndex]
            newName = self.cofeatureCombo.currentText()
            ds.coFeatureName = newName
            item = self.setsTable.item(self._selectedIndex, 2)

            if item:

                item.setText(newName)

            # Repopulate the subfeature and value combos for the new co-feature
            # (subfeature list excludes the co-feature; values are limited to sg/pl).
            self._updating = True

            try:
                for fc, vc in self.pairingFields:

                    currentFeat = fc.currentText()
                    currentVal = vc.currentText()
                    self._populateFeatureCombo(fc, ds.language, newName)
                    self._populateValueCombo(vc, ds.language, newName)
                    fc.setCurrentText(currentFeat)
                    vc.setCurrentText(currentVal)
            finally:
                self._updating = False

    def _onPairingFeatureChanged(self, row: int) -> None:
        """Write pairing feature name back to model."""

        if self._updating:

            return

        if not (0 <= self._selectedIndex < len(self.generator.disjointFeatures)):

            return

        ds = self.generator.disjointFeatures[self._selectedIndex]

        if row < len(ds.pairings):

            ds.pairings[row].flexFeatureName = self.pairingFields[row][0].currentText()

    def _onPairingValueChanged(self, row: int) -> None:
        """Write pairing co-feature value back to model."""

        if self._updating:

            return

        if not (0 <= self._selectedIndex < len(self.generator.disjointFeatures)):

            return

        ds = self.generator.disjointFeatures[self._selectedIndex]

        if row < len(ds.pairings):

            ds.pairings[row].coFeatureValue = self.pairingFields[row][1].currentText()

    def _onPairingSliderChanged(self) -> None:

        if not (0 <= self._selectedIndex < len(self.generator.disjointFeatures)):

            return

        ds = self.generator.disjointFeatures[self._selectedIndex]
        newCount = self.pairingSlider.value()

        while len(ds.pairings) < newCount:

            from RAutils import DisjointFeatureValuePairing
            ds.pairings.append(DisjointFeatureValuePairing())

        while len(ds.pairings) > newCount:

            ds.pairings.pop()

        self._updatePairingRowVisibility(newCount)

    def _onAddSet(self) -> None:

        from RAutils import DisjointFeatureSet, DisjointFeatureValuePairing, PhraseType

        # Default the distinguishing feature to "number" (the only supported one), so
        # the Feature value lists populate with its sg/pl values.
        newSet = DisjointFeatureSet(
            name="New Set",
            coFeatureName=DISJOINT_NUMBER,
            language=PhraseType.target
        )
        newSet.pairings = [DisjointFeatureValuePairing() for _ in range(self.MINIMUM_PAIRINGS)]
        self.generator.disjointFeatures.append(newSet)
        self._populateList()
        self._updateButtonStates()

        # Select the newly added set so it loads in the editor for editing.
        self.setsTable.selectRow(len(self.generator.disjointFeatures) - 1)

    def _onDeleteSet(self) -> None:

        if 0 <= self._selectedIndex < len(self.generator.disjointFeatures):

            self.generator.disjointFeatures.pop(self._selectedIndex)
            self._populateList()
            self._selectedIndex = -1
            self._updateButtonStates()

    def _updateButtonStates(self) -> None:
        """At most one disjoint feature set is allowed: enable Add only when there
        are none, and enable Delete only when there is at least one."""

        hasSet = len(self.generator.disjointFeatures) > 0
        self._addButton.setEnabled(not hasSet)
        self._deleteButton.setEnabled(hasSet)
