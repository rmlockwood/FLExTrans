"""Disjoint Features Editor Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QWidget, QLabel, QLineEdit, QComboBox, QSlider, QPushButton, QGridLayout,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from RAutils import FLExTransRuleGenerator, FLExData


class DisjointFeaturesEditorDialog(QDialog):
    """Modal dialog for editing disjoint feature sets."""

    def __init__(self, generator: "FLExTransRuleGenerator", flex_data: "FLExData", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Disjoint Features Editor")
        self.setModal(True)
        self.resize(700, 500)

        self.generator = generator
        self.flex_data = flex_data
        self._selected_index = -1
        self._updating = False  # guard against re-entrant signal handlers

        self._create_ui()
        self._populate_list()

    def _create_ui(self) -> None:
        """Create the UI layout."""
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sets_table = QTableWidget()
        self.sets_table.setColumnCount(3)
        self.sets_table.setHorizontalHeaderLabels(["Name", "Language", "Co-Feature"])
        self.sets_table.itemSelectionChanged.connect(self._on_set_selected)
        splitter.addWidget(self.sets_table)

        editor_pane = self._create_editor_pane()
        splitter.addWidget(editor_pane)

        splitter.setSizes([300, 350])
        main_layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New Set")
        add_button.clicked.connect(self._on_add_set)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Delete Set")
        delete_button.clicked.connect(self._on_delete_set)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

    def _create_editor_pane(self) -> QWidget:
        """Create the right pane editor."""
        pane = QWidget()
        layout = QVBoxLayout(pane)

        layout.addWidget(QLabel("Cover term"))
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_field = QLineEdit()
        self.name_field.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self.name_field)
        layout.addLayout(name_layout)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Source", "Target"])
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.language_combo)
        layout.addLayout(lang_layout)

        cofeature_layout = QHBoxLayout()
        cofeature_layout.addWidget(QLabel("Co-feature name:"))
        self.cofeature_combo = QComboBox()
        self._populate_cofeature_combo()
        self.cofeature_combo.currentIndexChanged.connect(self._on_cofeature_changed)
        cofeature_layout.addWidget(self.cofeature_combo)
        layout.addLayout(cofeature_layout)

        layout.addWidget(QLabel("Pairings"))
        self._pairings_grid = QGridLayout()
        self._pairings_grid.addWidget(QLabel("FLEx feature name"), 0, 0)
        self._pairings_grid.addWidget(QLabel("Co-feature value"), 0, 1)

        # Keep row widgets so we can show/hide them
        self._pairing_row_widgets: list[tuple[QWidget, QWidget]] = []
        self.pairing_fields: list[tuple[QComboBox, QComboBox]] = []

        current_cofeature = self.cofeature_combo.currentText()
        for i in range(6):
            feature_combo = QComboBox()
            value_combo = QComboBox()
            self._populate_feature_combo(feature_combo)
            self._populate_value_combo(value_combo, current_cofeature)
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
        slider_layout.addWidget(QLabel("Pairings:"))
        self.pairing_slider = QSlider(Qt.Orientation.Horizontal)
        self.pairing_slider.setMinimum(3)  # Java constraint: minimum 3
        self.pairing_slider.setMaximum(6)
        self.pairing_slider.setValue(3)
        self.pairing_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pairing_slider.setTickInterval(1)
        self.pairing_slider.sliderMoved.connect(self._on_pairing_slider_changed)
        slider_layout.addWidget(self.pairing_slider)
        layout.addLayout(slider_layout)

        layout.addStretch()
        self._update_pairing_row_visibility(3)
        return pane

    def _populate_list(self) -> None:
        """Populate the disjoint feature sets table."""
        self.sets_table.setRowCount(len(self.generator.disjoint_features))
        for i, ds in enumerate(self.generator.disjoint_features):
            self.sets_table.setItem(i, 0, QTableWidgetItem(ds.name))
            self.sets_table.setItem(i, 1, QTableWidgetItem(ds.language.value.capitalize()))
            self.sets_table.setItem(i, 2, QTableWidgetItem(ds.co_feature_name))

    def _populate_cofeature_combo(self) -> None:
        """Populate co-feature name combo with FLEx feature names."""
        self.cofeature_combo.clear()
        self.cofeature_combo.addItems(sorted(self._get_all_feature_names()))

    def _populate_feature_combo(self, combo: QComboBox) -> None:
        """Populate a FLEx feature name combo."""
        combo.clear()
        combo.addItems(sorted(self._get_all_feature_names()))

    def _populate_value_combo(self, combo: QComboBox, co_feature_name: str) -> None:
        """Populate a co-feature value combo with values of the named feature."""
        combo.clear()
        if not self.flex_data or not co_feature_name:
            return
        values: set[str] = set()
        for feature in self.flex_data.source_data.features:
            if feature.name == co_feature_name:
                for v in feature.values:
                    values.add(v.abbreviation)
        for feature in self.flex_data.target_data.features:
            if feature.name == co_feature_name:
                for v in feature.values:
                    values.add(v.abbreviation)
        combo.addItems(sorted(values))

    def _get_all_feature_names(self) -> set[str]:
        names: set[str] = set()
        if self.flex_data:
            for f in self.flex_data.source_data.features:
                names.add(f.name)
            for f in self.flex_data.target_data.features:
                names.add(f.name)
        return names

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
            self.language_combo.setCurrentText(
                "Source" if ds.language.value == "source" else "Target"
            )
            self.cofeature_combo.setCurrentText(ds.co_feature_name)

            # Repopulate value combos for the loaded co-feature
            for _fc, vc in self.pairing_fields:
                self._populate_value_combo(vc, ds.co_feature_name)

            count = max(len(ds.pairings), 3)
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
            lang = PhraseType.source if self.language_combo.currentText() == "Source" else PhraseType.target
            self.generator.disjoint_features[self._selected_index].language = lang

    def _on_cofeature_changed(self) -> None:
        if self._updating:
            return
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            new_name = self.cofeature_combo.currentText()
            self.generator.disjoint_features[self._selected_index].co_feature_name = new_name
            item = self.sets_table.item(self._selected_index, 2)
            if item:
                item.setText(new_name)
            # Repopulate value combos with the new co-feature's values
            self._updating = True
            try:
                for _fc, vc in self.pairing_fields:
                    current_val = vc.currentText()
                    self._populate_value_combo(vc, new_name)
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
        new_set = DisjointFeatureSet(
            name="New Set",
            co_feature_name="",
            language=PhraseType.target
        )
        new_set.pairings = [DisjointFeatureValuePairing() for _ in range(3)]
        self.generator.disjoint_features.append(new_set)
        self._populate_list()

    def _on_delete_set(self) -> None:
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            self.generator.disjoint_features.pop(self._selected_index)
            self._populate_list()
            self._selected_index = -1
