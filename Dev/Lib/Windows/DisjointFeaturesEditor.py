#
#   DisjointFeaturesEditor.py
#
#   Matthew Lee, Ron Lockwood - original Java version by Andy Black
#   SIL International
#   September 2023
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Fixes #1344. More fixes to the Disjoint Features Editor. Auto load the first set.
#    Disable certain controls. Numbers on slider.
#
#  Main window for the FLExTrans Rule Assistant application.
"""Disjoint Features Editor Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QWidget, QLabel, QLineEdit, QComboBox, QSlider, QPushButton, QGridLayout,
    QMessageBox, QFrame, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, QSize, QCoreApplication
from typing import Optional, TYPE_CHECKING

from RAutils import PhraseType, DISJOINT_NUMBER, DISJOINT_SG, DISJOINT_PL

if TYPE_CHECKING:
    from RAutils import FLExTransRuleGenerator, FLExData

_translate = QCoreApplication.translate


class DisjointFeaturesEditorDialog(QDialog):
    """Modal dialog for editing disjoint feature sets."""

    # The first two pairings are required, so a set always has at least this many
    # (matches the Java editor's minimumPairings = 2).
    MINIMUM_PAIRINGS = 2

    def __init__(self, generator: "FLExTransRuleGenerator", flex_data: "FLExData", parent=None):
        super().__init__(parent)
        self.setWindowTitle(_translate("RuleAssistantLib", "Disjoint Features Editor"))
        self.setModal(True)
        self.resize(700, 500)

        self.generator = generator
        self.flex_data = flex_data
        self._selected_index = -1
        self._updating = False  # guard against re-entrant signal handlers

        self._create_ui()
        self._populate_list()
        self._update_button_states()

        # Load the first set automatically when the editor opens (matches Java).
        if self.generator.disjoint_features:
            self.sets_table.selectRow(0)

    def _create_ui(self) -> None:
        """Create the UI layout."""
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sets_table = QTableWidget()
        self.sets_table.setColumnCount(3)
        # The grid is a read-only summary; sets are edited via the right-hand pane.
        self.sets_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sets_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Don't draw the dotted/coloured focus indicator inside cells.
        self.sets_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Styling the item switches Qt to its own item rendering, which removes the
        # native Windows 11 selection "accent bar" drawn at the left of each cell.
        self.sets_table.setStyleSheet(
            "QTableView { outline: 0; }"
            "QTableView::item { border: 0; }"
            "QTableView::item:selected {"
            " background-color: palette(highlight); color: palette(highlighted-text); }"
        )
        self.sets_table.setHorizontalHeaderLabels([
            _translate("RuleAssistantLib", "Name"),
            _translate("RuleAssistantLib", "Language"),
            _translate("RuleAssistantLib", "Distinguishing feature"),
        ])
        # Size each column to fit the wider of its header text and contents so
        # headers like "Distinguishing feature" aren't cut off.
        header = self.sets_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.sets_table.itemSelectionChanged.connect(self._on_set_selected)
        splitter.addWidget(self.sets_table)

        editor_pane = self._create_editor_pane()
        splitter.addWidget(editor_pane)

        splitter.setSizes([300, 350])
        main_layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        self._add_button = QPushButton(_translate("RuleAssistantLib", "Add new set"))
        self._add_button.clicked.connect(self._on_add_set)
        # Only one set is allowed; _update_button_states() enables this only when
        # there are no sets yet.
        button_layout.addWidget(self._add_button)

        self._delete_button = QPushButton(_translate("RuleAssistantLib", "Delete selected set"))
        self._delete_button.clicked.connect(self._on_delete_set)
        button_layout.addWidget(self._delete_button)

        button_layout.addStretch()

        close_button = QPushButton(_translate("RuleAssistantLib", "Close"))
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

    def _create_editor_pane(self) -> QWidget:
        """Create the right pane editor."""
        pane = QWidget()
        layout = QVBoxLayout(pane)

        layout.addWidget(QLabel(_translate("RuleAssistantLib", "Disjoint feature set")))
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(_translate("RuleAssistantLib", "Name")))
        self.name_field = QLineEdit()
        self.name_field.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self.name_field)
        layout.addLayout(name_layout)

        lang_layout = QHBoxLayout()
        lang_label = QLabel(_translate("RuleAssistantLib", "Language"))
        lang_layout.addWidget(lang_label)
        self.language_combo = QComboBox()
        # Store the language code as item data so the display text can be translated
        # without affecting the logic that reads the selection.
        self.language_combo.addItem(_translate("RuleAssistantLib", "Source"), "source")
        self.language_combo.addItem(_translate("RuleAssistantLib", "Target"), "target")
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        # Changing the language is not yet supported (matches the Java editor, which
        # disables the source/target radio buttons).
        lang_label.setEnabled(False)
        self.language_combo.setEnabled(False)
        lang_layout.addWidget(self.language_combo)
        layout.addLayout(lang_layout)

        cofeature_layout = QHBoxLayout()
        cofeature_layout.addWidget(QLabel(_translate("RuleAssistantLib", "Distinguishing feature")))
        self.cofeature_combo = QComboBox()
        self._populate_cofeature_combo(PhraseType.target)
        self.cofeature_combo.currentIndexChanged.connect(self._on_cofeature_changed)
        cofeature_layout.addWidget(self.cofeature_combo)
        layout.addLayout(cofeature_layout)

        # Separate the pairings (subfeatures) section from the widgets above.
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        self._pairings_grid = QGridLayout()
        self._pairings_grid.addWidget(QLabel(_translate("RuleAssistantLib", "Subfeature")), 0, 0)
        self._pairings_grid.addWidget(QLabel(_translate("RuleAssistantLib", "Feature value")), 0, 1)

        # Keep row widgets so we can show/hide them
        self._pairing_row_widgets: list[tuple[QWidget, QWidget]] = []
        self.pairing_fields: list[tuple[QComboBox, QComboBox]] = []

        current_cofeature = self.cofeature_combo.currentText()
        for i in range(6):
            feature_combo = QComboBox()
            value_combo = QComboBox()
            self._populate_feature_combo(feature_combo, PhraseType.target, current_cofeature)
            self._populate_value_combo(value_combo, PhraseType.target, current_cofeature)
            # Connect signals with index capture
            feature_combo.currentIndexChanged.connect(
                lambda _idx, row=i: self._on_pairing_feature_changed(row))
            value_combo.currentIndexChanged.connect(
                lambda _idx, row=i: self._on_pairing_value_changed(row))
            self._pairings_grid.addWidget(feature_combo, i + 1, 0)
            self._pairings_grid.addWidget(value_combo, i + 1, 1)
            self.pairing_fields.append((feature_combo, value_combo))
            self._pairing_row_widgets.append((feature_combo, value_combo))

        layout.addLayout(self._pairings_grid)

        slider_layout = QHBoxLayout()
        slider_label = QLabel(_translate("RuleAssistantLib", "Number of subfeatures:"))
        slider_layout.addWidget(slider_label)

        # The slider and its tick numbers are stacked so the numbers line up under it.
        slider_box = QVBoxLayout()
        slider_box.setSpacing(0)
        self.pairing_slider = QSlider(Qt.Orientation.Horizontal)
        self.pairing_slider.setMinimum(self.MINIMUM_PAIRINGS)  # Java constraint: first two pairings are required
        self.pairing_slider.setMaximum(6)
        self.pairing_slider.setValue(self.MINIMUM_PAIRINGS)
        self.pairing_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pairing_slider.setTickInterval(1)
        self.pairing_slider.sliderMoved.connect(self._on_pairing_slider_changed)
        # Changing the number of pairings is not yet supported (matches the Java
        # editor, which disables the slider); the count is fixed by the loaded set.
        self.pairing_slider.setEnabled(False)
        slider_label.setEnabled(False)
        slider_box.addWidget(self.pairing_slider)

        # Numbers under the slider (Qt sliders don't render tick labels themselves).
        numbers_layout = QHBoxLayout()
        numbers_layout.setContentsMargins(0, 0, 0, 0)
        for n in range(self.MINIMUM_PAIRINGS, 7):
            if n > self.MINIMUM_PAIRINGS:
                numbers_layout.addStretch()
            numbers_layout.addWidget(QLabel(str(n)))
        slider_box.addLayout(numbers_layout)

        slider_layout.addLayout(slider_box)
        layout.addLayout(slider_layout)

        layout.addStretch()
        self._update_pairing_row_visibility(self.MINIMUM_PAIRINGS)
        return pane

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
            lang_display = (_translate("RuleAssistantLib", "Source")
                            if ds.language.value == "source"
                            else _translate("RuleAssistantLib", "Target"))
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
            from RAutils import PhraseType
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
