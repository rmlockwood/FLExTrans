"""Disjoint Features Editor Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QWidget, QLabel, QLineEdit, QComboBox, QSlider, QPushButton, QGridLayout,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flex_trans_rule_generator import FLExTransRuleGenerator
    from flex_data import FLExData


class DisjointFeaturesEditorDialog(QDialog):
    """Modal dialog for editing disjoint feature sets.

    A simplified version that allows adding/removing disjoint feature sets
    and editing their pairings.
    """

    def __init__(self, generator: "FLExTransRuleGenerator", flex_data: "FLExData", parent=None):
        """Initialize the disjoint features editor.

        Args:
            generator: The FLExTransRuleGenerator to edit
            flex_data: The FLEx metadata for feature names
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Disjoint Features Editor")
        self.setModal(True)
        self.resize(700, 500)

        self.generator = generator
        self.flex_data = flex_data
        self._selected_index = -1

        self._create_ui()
        self._populate_list()

    def _create_ui(self) -> None:
        """Create the UI layout."""
        main_layout = QVBoxLayout(self)

        # Splitter: list on left, editor on right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: table of disjoint feature sets
        self.sets_table = QTableWidget()
        self.sets_table.setColumnCount(3)
        self.sets_table.setHorizontalHeaderLabels(["Name", "Language", "Co-Feature"])
        self.sets_table.itemSelectionChanged.connect(self._on_set_selected)
        splitter.addWidget(self.sets_table)

        # Right: editor panel
        editor_pane = self._create_editor_pane()
        splitter.addWidget(editor_pane)

        splitter.setSizes([300, 350])
        main_layout.addWidget(splitter)

        # Buttons at bottom
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
        """Create the right pane editor.

        Returns:
            QWidget containing the editor controls
        """
        pane = QWidget()
        layout = QVBoxLayout(pane)

        # Name field
        layout.addWidget(QLabel("Cover term"))
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_field = QLineEdit()
        self.name_field.textChanged.connect(self._on_name_changed)
        name_layout.addWidget(self.name_field)
        layout.addLayout(name_layout)

        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Source", "Target"])
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.language_combo)
        layout.addLayout(lang_layout)

        # Co-feature name
        cofeature_layout = QHBoxLayout()
        cofeature_layout.addWidget(QLabel("Co-feature name:"))
        self.cofeature_combo = QComboBox()
        self._populate_cofeature_combo()
        self.cofeature_combo.currentIndexChanged.connect(self._on_cofeature_changed)
        cofeature_layout.addWidget(self.cofeature_combo)
        layout.addLayout(cofeature_layout)

        # Pairings
        layout.addWidget(QLabel("Pairings"))
        pairings_layout = QGridLayout()

        pairings_layout.addWidget(QLabel("FLEx feature name"), 0, 0)
        pairings_layout.addWidget(QLabel("Co-feature value"), 0, 1)

        self.pairing_fields = []
        for i in range(6):
            feature_combo = QComboBox()
            value_combo = QComboBox()
            self._populate_feature_combo(feature_combo)
            pairings_layout.addWidget(feature_combo, i + 1, 0)
            pairings_layout.addWidget(value_combo, i + 1, 1)
            self.pairing_fields.append((feature_combo, value_combo))

        layout.addLayout(pairings_layout)

        # Slider for number of visible pairings
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Pairings:"))
        self.pairing_slider = QSlider(Qt.Orientation.Horizontal)
        self.pairing_slider.setMinimum(2)
        self.pairing_slider.setMaximum(6)
        self.pairing_slider.setValue(2)
        self.pairing_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pairing_slider.setTickInterval(1)
        self.pairing_slider.sliderMoved.connect(self._on_pairing_slider_changed)
        slider_layout.addWidget(self.pairing_slider)
        layout.addLayout(slider_layout)

        layout.addStretch()
        return pane

    def _populate_list(self) -> None:
        """Populate the disjoint feature sets table."""
        self.sets_table.setRowCount(len(self.generator.disjoint_features))

        for i, ds in enumerate(self.generator.disjoint_features):
            name_item = QTableWidgetItem(ds.name)
            lang_item = QTableWidgetItem(ds.language.value.capitalize())
            cofeature_item = QTableWidgetItem(ds.co_feature_name)

            self.sets_table.setItem(i, 0, name_item)
            self.sets_table.setItem(i, 1, lang_item)
            self.sets_table.setItem(i, 2, cofeature_item)

    def _populate_cofeature_combo(self) -> None:
        """Populate co-feature name combo with FLEx features."""
        self.cofeature_combo.clear()
        all_features = set()
        if self.flex_data:
            for feature in self.flex_data.source_data.features:
                all_features.add(feature.name)
            for feature in self.flex_data.target_data.features:
                all_features.add(feature.name)
        self.cofeature_combo.addItems(sorted(all_features))

    def _populate_feature_combo(self, combo: QComboBox) -> None:
        """Populate a feature combo with available FLEx features."""
        combo.clear()
        all_features = set()
        if self.flex_data:
            for feature in self.flex_data.source_data.features:
                all_features.add(feature.name)
            for feature in self.flex_data.target_data.features:
                all_features.add(feature.name)
        combo.addItems(sorted(all_features))

    def _on_set_selected(self) -> None:
        """Handle selection of a disjoint feature set."""
        rows = self.sets_table.selectedIndexes()
        if rows:
            self._selected_index = rows[0].row()
            self._update_editor_from_selection()
        else:
            self._selected_index = -1

    def _update_editor_from_selection(self) -> None:
        """Update editor fields from selected set."""
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            ds = self.generator.disjoint_features[self._selected_index]
            self.name_field.setText(ds.name)
            self.language_combo.setCurrentText(
                "Source" if ds.language.value == "source" else "Target"
            )
            self.cofeature_combo.setCurrentText(ds.co_feature_name)

            # Populate pairings
            for i in range(6):
                if i < len(ds.pairings):
                    pairing = ds.pairings[i]
                    self.pairing_fields[i][0].setCurrentText(pairing.flex_feature_name)
                    self.pairing_fields[i][1].setCurrentText(pairing.co_feature_value)
                else:
                    self.pairing_fields[i][0].setCurrentIndex(0)
                    self.pairing_fields[i][1].setCurrentIndex(0)

            self.pairing_slider.setValue(len(ds.pairings) if ds.pairings else 2)

    def _on_name_changed(self) -> None:
        """Handle name field change."""
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            self.generator.disjoint_features[self._selected_index].name = self.name_field.text()
            self.sets_table.item(self._selected_index, 0).setText(self.name_field.text())

    def _on_language_changed(self) -> None:
        """Handle language combo change."""
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            from enums import PhraseType
            lang = PhraseType.source if self.language_combo.currentText() == "Source" else PhraseType.target
            self.generator.disjoint_features[self._selected_index].language = lang

    def _on_cofeature_changed(self) -> None:
        """Handle co-feature name change."""
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            self.generator.disjoint_features[self._selected_index].co_feature_name = (
                self.cofeature_combo.currentText()
            )

    def _on_pairing_slider_changed(self) -> None:
        """Handle pairing slider change."""
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            ds = self.generator.disjoint_features[self._selected_index]
            new_count = self.pairing_slider.value()
            # Adjust pairings list
            while len(ds.pairings) < new_count:
                from disjoint_feature_set import DisjointFeatureValuePairing
                ds.pairings.append(DisjointFeatureValuePairing())
            while len(ds.pairings) > new_count:
                ds.pairings.pop()

    def _on_add_set(self) -> None:
        """Add a new disjoint feature set."""
        from disjoint_feature_set import DisjointFeatureSet, DisjointFeatureValuePairing
        from enums import PhraseType

        new_set = DisjointFeatureSet(
            name="New Set",
            co_feature_name="",
            language=PhraseType.target
        )
        new_set.pairings = [DisjointFeatureValuePairing(), DisjointFeatureValuePairing()]
        self.generator.disjoint_features.append(new_set)
        self._populate_list()

    def _on_delete_set(self) -> None:
        """Delete the selected disjoint feature set."""
        if 0 <= self._selected_index < len(self.generator.disjoint_features):
            self.generator.disjoint_features.pop(self._selected_index)
            self._populate_list()
            self._selected_index = -1
