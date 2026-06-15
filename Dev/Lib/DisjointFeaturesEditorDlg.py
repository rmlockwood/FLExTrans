#
#   DisjointFeaturesEditorDlg.py
#
#   Matthew Lee, Ron Lockwood - original Java version by Andy Black
#   SIL International
#   September 2023
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Refactored: widgets/layout now live in DisjointFeaturesEditor.ui (compiled to
#    DisjointFeaturesEditor.py as Ui_DisjointFeaturesEditorDialog). This controller
#    holds the behavior.
#
#  Controller for the Disjoint Features Editor dialog.
"""Disjoint Features Editor Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QTableWidgetItem, QLabel, QComboBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, QCoreApplication
from typing import Optional, TYPE_CHECKING

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

    def __init__(self, generator: "FLExTransRuleGenerator", flex_data: "FLExData", parent=None):
        super().__init__(parent)
        self.ui = Ui_DisjointFeaturesEditorDialog()
        self.ui.setupUi(self)

        self.generator = generator
        self.flex_data = flex_data
        self._selected_index = -1
        self._updating = False  # guard against re-entrant signal handlers

        self._setup_widgets()
        self._connect_signals()

        self._populate_list()
        self._update_button_states()

        # Load the first set automatically when the editor opens (matches Java).
        if self.generator.disjoint_features:
            self.sets_table.selectRow(0)

    def _setup_widgets(self) -> None:
        """Alias the .ui widgets, apply behavioral tweaks the .ui can't express, and
        populate the combos/slider that are driven by data."""
        self.sets_table = self.ui.sets_table
        self.name_field = self.ui.name_field
        self.language_combo = self.ui.language_combo
        self.cofeature_combo = self.ui.cofeature_combo
        self.pairing_slider = self.ui.pairing_slider
        self._add_button = self.ui.add_button
        self._delete_button = self.ui.delete_button

        # Read-only summary grid: no editing, row selection, no focus rectangle, and a
        # stylesheet so Qt draws its own selection (removing the Win11 accent bar).
        self.sets_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sets_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sets_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sets_table.setStyleSheet(
            "QTableView { outline: 0; }"
            "QTableView::item { border: 0; }"
            "QTableView::item:selected {"
            " background-color: palette(highlight); color: palette(highlighted-text); }"
        )
        header = self.sets_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.ui.splitter.setSizes([300, 350])

        # Language combo: store the language code as item data so the display text can
        # be translated without affecting the logic that reads the selection.
        self.language_combo.addItem(_translate("DisjointFeaturesEditorDialog", "Source"), "source")
        self.language_combo.addItem(_translate("DisjointFeaturesEditorDialog", "Target"), "target")

        # Collect the .ui pairing combos into the lists the logic uses.
        self.pairing_fields: list[tuple[QComboBox, QComboBox]] = []
        self._pairing_row_widgets: list[tuple[QComboBox, QComboBox]] = []
        for i in range(1, 7):
            fc = getattr(self.ui, f"feature_combo_{i}")
            vc = getattr(self.ui, f"value_combo_{i}")
            self.pairing_fields.append((fc, vc))
            self._pairing_row_widgets.append((fc, vc))

        self._populate_cofeature_combo(PhraseType.target)
        current_cofeature = self.cofeature_combo.currentText()
        for fc, vc in self.pairing_fields:
            self._populate_feature_combo(fc, PhraseType.target, current_cofeature)
            self._populate_value_combo(vc, PhraseType.target, current_cofeature)

        # Numbers under the (disabled) slider; Qt sliders don't render tick labels.
        for n in range(self.MINIMUM_PAIRINGS, 7):
            if n > self.MINIMUM_PAIRINGS:
                self.ui.sliderNumbersLayout.addStretch()
            self.ui.sliderNumbersLayout.addWidget(QLabel(str(n)))

        self._update_pairing_row_visibility(self.MINIMUM_PAIRINGS)

    def _connect_signals(self) -> None:
        """Wire the .ui widgets to the controller's handlers."""
        self.sets_table.itemSelectionChanged.connect(self._on_set_selected)
        self.name_field.textChanged.connect(self._on_name_changed)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.cofeature_combo.currentIndexChanged.connect(self._on_cofeature_changed)
        self.pairing_slider.sliderMoved.connect(self._on_pairing_slider_changed)
        self._add_button.clicked.connect(self._on_add_set)
        self._delete_button.clicked.connect(self._on_delete_set)
        self.ui.close_button.clicked.connect(self.accept)
        for i, (fc, vc) in enumerate(self.pairing_fields):
            fc.currentIndexChanged.connect(lambda _idx, row=i: self._on_pairing_feature_changed(row))
            vc.currentIndexChanged.connect(lambda _idx, row=i: self._on_pairing_value_changed(row))

    @staticmethod
    def _make_cell(text: str) -> QTableWidgetItem:
        """A read-only (non-editable) grid cell."""
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def _populate_list(self) -> None:
        """Populate the disjoint feature sets table."""
        self.sets_table.setRowCount(len(self.generator.disjoint_features))
        for i, ds in enumerate(self.generator.disjoint_features):
            lang_display = (_translate("DisjointFeaturesEditorDialog", "Source")
                            if ds.language.value == "source"
                            else _translate("DisjointFeaturesEditorDialog", "Target"))
            self.sets_table.setItem(i, 0, self._make_cell(ds.name))
            self.sets_table.setItem(i, 1, self._make_cell(lang_display))
            self.sets_table.setItem(i, 2, self._make_cell(ds.co_feature_name))

    def _features_for_language(self, language) -> list:
        """FLEx features for the given phrase (source vs target), matching Java,
        which draws on the source or target features depending on the set."""
        if not self.flex_data:
            return []
        if language == PhraseType.source:
            return self.flex_data.source_data.features
        return self.flex_data.target_data.features

    def _populate_cofeature_combo(self, language) -> None:
        """Distinguishing feature combo: limited to the "number" feature, as in
        the Java editor (the only feature the disjoint editor currently supports)."""
        self.cofeature_combo.clear()
        names = [f.name for f in self._features_for_language(language)
                 if f.name == DISJOINT_NUMBER]
        self.cofeature_combo.addItems(names)

    def _populate_feature_combo(self, combo: QComboBox, language, co_feature_name: str) -> None:
        """Subfeature combo: all FLEx feature names except the distinguishing
        (co-)feature, matching the Java flexFeatureMinusCoFeatureNames list."""
        combo.clear()
        names = sorted({f.name for f in self._features_for_language(language)
                        if f.name != co_feature_name})
        combo.addItems(names)

    def _populate_value_combo(self, combo: QComboBox, language, co_feature_name: str) -> None:
        """Feature value combo: the co-feature's values, limited to "sg"/"pl", as
        in the Java editor (the only values the disjoint editor currently supports)."""
        combo.clear()
        if not co_feature_name:
            return
        for feature in self._features_for_language(language):
            if feature.name == co_feature_name:
                for v in feature.values:
                    if v.abbreviation in (DISJOINT_SG, DISJOINT_PL):
                        combo.addItem(v.abbreviation)
                break

    def _update_pairing_row_visibility(self, count: int) -> None:
        """Show rows 0..count-1, hide rows count..5."""
        for i, (fc, vc) in enumerate(self._pairing_row_widgets):
            visible = i < count
            fc.setVisible(visible)
            vc.setVisible(visible)

    def _on_set_selected(self) -> None:
        rows = self.sets_table.selectedIndexes()
        if rows:
            self._selected_index = rows[0].row()
            self._update_editor_from_selection()
        else:
            self._selected_index = -1

    def _update_editor_from_selection(self) -> None:
        """Load selected set into editor widgets (blocks signals to avoid write-back)."""
        if not (0 <= self._selected_index < len(self.generator.disjoint_features)):
            return
        self._updating = True
        try:
            ds = self.generator.disjoint_features[self._selected_index]
            self.name_field.setText(ds.name)
            lang_index = self.language_combo.findData(ds.language.value)
            self.language_combo.setCurrentIndex(lang_index if lang_index >= 0 else 0)

            # Repopulate the combos (limited like Java) for this set's language.
            self._populate_cofeature_combo(ds.language)
            self.cofeature_combo.setCurrentText(ds.co_feature_name)
            for fc, vc in self.pairing_fields:
                self._populate_feature_combo(fc, ds.language, ds.co_feature_name)
                self._populate_value_combo(vc, ds.language, ds.co_feature_name)

            count = max(len(ds.pairings), self.MINIMUM_PAIRINGS)
            self.pairing_slider.setValue(count)

            for i in range(6):
                fc, vc = self.pairing_fields[i]
                if i < len(ds.pairings):
                    pairing = ds.pairings[i]
                    fc.setCurrentText(pairing.flex_feature_name)
                    vc.setCurrentText(pairing.co_feature_value)
                else:
                    fc.setCurrentIndex(0)
                    vc.setCurrentIndex(0)

            self._update_pairing_row_visibility(count)
        finally:
            self._updating = False

    def _on_name_changed(self) -> None:
        if self._updating:
            return
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            self.generator.disjoint_features[self._selected_index].name = self.name_field.text()
            item = self.sets_table.item(self._selected_index, 0)
            if item:
                item.setText(self.name_field.text())

    def _on_language_changed(self) -> None:
        if self._updating:
            return
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            lang = PhraseType.source if self.language_combo.currentData() == "source" else PhraseType.target
            self.generator.disjoint_features[self._selected_index].language = lang

    def _on_cofeature_changed(self) -> None:
        if self._updating:
            return
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            ds = self.generator.disjoint_features[self._selected_index]
            new_name = self.cofeature_combo.currentText()
            ds.co_feature_name = new_name
            item = self.sets_table.item(self._selected_index, 2)
            if item:
                item.setText(new_name)
            # Repopulate the subfeature and value combos for the new co-feature
            # (subfeature list excludes the co-feature; values are limited to sg/pl).
            self._updating = True
            try:
                for fc, vc in self.pairing_fields:
                    current_feat = fc.currentText()
                    current_val = vc.currentText()
                    self._populate_feature_combo(fc, ds.language, new_name)
                    self._populate_value_combo(vc, ds.language, new_name)
                    fc.setCurrentText(current_feat)
                    vc.setCurrentText(current_val)
            finally:
                self._updating = False

    def _on_pairing_feature_changed(self, row: int) -> None:
        """Write pairing feature name back to model."""
        if self._updating:
            return
        if not (0 <= self._selected_index < len(self.generator.disjoint_features)):
            return
        ds = self.generator.disjoint_features[self._selected_index]
        if row < len(ds.pairings):
            ds.pairings[row].flex_feature_name = self.pairing_fields[row][0].currentText()

    def _on_pairing_value_changed(self, row: int) -> None:
        """Write pairing co-feature value back to model."""
        if self._updating:
            return
        if not (0 <= self._selected_index < len(self.generator.disjoint_features)):
            return
        ds = self.generator.disjoint_features[self._selected_index]
        if row < len(ds.pairings):
            ds.pairings[row].co_feature_value = self.pairing_fields[row][1].currentText()

    def _on_pairing_slider_changed(self) -> None:
        if not (0 <= self._selected_index < len(self.generator.disjoint_features)):
            return
        ds = self.generator.disjoint_features[self._selected_index]
        new_count = self.pairing_slider.value()
        while len(ds.pairings) < new_count:
            from RAutils import DisjointFeatureValuePairing
            ds.pairings.append(DisjointFeatureValuePairing())
        while len(ds.pairings) > new_count:
            ds.pairings.pop()
        self._update_pairing_row_visibility(new_count)

    def _on_add_set(self) -> None:
        from RAutils import DisjointFeatureSet, DisjointFeatureValuePairing, PhraseType
        # Default the distinguishing feature to "number" (the only supported one), so
        # the Feature value lists populate with its sg/pl values.
        new_set = DisjointFeatureSet(
            name="New Set",
            co_feature_name=DISJOINT_NUMBER,
            language=PhraseType.target
        )
        new_set.pairings = [DisjointFeatureValuePairing() for _ in range(self.MINIMUM_PAIRINGS)]
        self.generator.disjoint_features.append(new_set)
        self._populate_list()
        self._update_button_states()
        # Select the newly added set so it loads in the editor for editing.
        self.sets_table.selectRow(len(self.generator.disjoint_features) - 1)

    def _on_delete_set(self) -> None:
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            self.generator.disjoint_features.pop(self._selected_index)
            self._populate_list()
            self._selected_index = -1
            self._update_button_states()

    def _update_button_states(self) -> None:
        """At most one disjoint feature set is allowed: enable Add only when there
        are none, and enable Delete only when there is at least one."""
        has_set = len(self.generator.disjoint_features) > 0
        self._add_button.setEnabled(not has_set)
        self._delete_button.setEnabled(has_set)
