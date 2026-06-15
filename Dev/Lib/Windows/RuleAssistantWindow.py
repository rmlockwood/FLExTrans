#
#   RuleAssistantPy
#
#   Matthew Lee, Ron Lockwood - original Java version by Andy Black
#   SIL International
#   September 2023
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Fixed #1361. Grey out context menu items in the tree view when the
#    operation doesn't apply to the clicked-on item (matching the Java version).

"""Main Window for FLExTrans Rule Assistant"""
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

import os
from typing import Optional, NamedTuple
from pathlib import Path
import logging
import tempfile
from datetime import datetime

# Fallback crash log
_crash_log = Path(tempfile.gettempdir()) / 'RuleAssistantWindow_CRASH.log'

def _write_crash_log(msg):
    """Direct file write as fallback"""
    try:
        with open(_crash_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {msg}\n")
            f.flush()
    except:
        pass

_write_crash_log("[INIT] main_window.py module loading")

# Setup logging - robust version
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# Remove any existing handlers to avoid duplicates
for handler in _logger.handlers[:]:
    _logger.removeHandler(handler)

try:
    _log_file = __file__.replace('.py', '.log')
    _file_handler = logging.FileHandler(_log_file, mode='w')
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(_file_handler)
except Exception:
    pass

_logger.propagate = True
_write_crash_log("[INIT] RuleAssistantWindow.py module loaded")
_logger.info("RuleAssistantWindow.py module loaded")

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QListWidget, QListWidgetItem, QLineEdit, QPlainTextEdit,
    QCheckBox, QPushButton, QMenu, QComboBox, QMessageBox,
    QInputDialog, QDialog
)
# LAZY IMPORT: QWebEngine moved to __init__ to avoid early initialization
# from PyQt6.QtWebEngineWidgets import QWebEngineView
# from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, QUrl, QPoint, QSize, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QKeySequence, QShortcut, QAction

_translate = QCoreApplication.translate

from RAutils import (
    FLExTransRuleGenerator, PhraseType, HeadValue, PermutationsValue, Word,
    FLExData, XMLBackEndProvider, XMLFLExDataBackEndProvider,
    RuleIdentifierAndParentSetter, ConstituentFinder, ValidityChecker,
    WebPageProducer, WebPageInteractor, ApplicationPreferences,
)
from CategoryChooser import CategoryChooserDialog
from FeatureValueChooser import FeatureValueChooserDialog
from DisjointFeaturesEditor import DisjointFeaturesEditorDialog


class WindowResult(NamedTuple):
    """Result returned from main window."""
    saved: bool
    rule_index: Optional[int]
    launch_lrt: bool


class RuleAssistantWindow(QMainWindow):
    """Main window for the Rule Assistant application.

    Displays rules in a tree format, manages editing and generation.
    """

    # Signal emitted when window finishes (for FlexTools integration)
    finished = pyqtSignal()


    def __init__(self, rule_file: str, flex_data_file: str, test_data_file: str,
                 came_from_lrt: bool = False, ui_lang_code: str = "en", parent=None):
        """Initialize the main window.

        Args:
            rule_file: Path to rule XML file
            flex_data_file: Path to FLEx metadata XML file
            test_data_file: Path to test data HTML file
            came_from_lrt: Whether launched from Live Rule Tester
            ui_lang_code: UI language code
            parent: Parent widget
        """
        _write_crash_log("[__init__] RuleAssistantWindow.__init__() starting")
        _logger.info("=" * 80)
        _logger.info("RuleAssistantWindow.__init__() called")
        _logger.info("=" * 80)
        _logger.info(f"  rule_file: {rule_file}")
        _logger.info(f"  flex_data_file: {flex_data_file}")
        _logger.info(f"  test_data_file: {test_data_file}")
        _logger.info(f"  came_from_lrt: {came_from_lrt}")
        _logger.info(f"  ui_lang_code: {ui_lang_code}")

        # LAZY IMPORT: Import QWebEngine only when window is created (not at module load)
        # This prevents Qt initialization issues when imported by FlexTools
        _write_crash_log("[__init__] About to lazy import QWebEngineView and QWebChannel")
        _logger.info("About to lazy import QWebEngineView and QWebChannel")
        global QWebEngineView, QWebChannel
        try:
            _write_crash_log("[__init__] QWebEngineView and QWebChannel imported successfully")
            _logger.info("QWebEngineView and QWebChannel imported successfully")
        except Exception as e:
            _write_crash_log(f"[__init__] FAILED to import QWebEngine: {e}")
            raise

        _write_crash_log("[__init__] About to call super().__init__()")
        _logger.info("About to call super().__init__()")
        try:
            super().__init__(parent)
            _write_crash_log("[__init__] super().__init__() completed successfully")
            _logger.info("super().__init__() completed")
        except Exception as e:
            _write_crash_log(f"[__init__] FAILED in super().__init__(): {e}")
            raise

        self.rule_file = rule_file
        self.flex_data_file = flex_data_file
        self.test_data_file = test_data_file
        self.came_from_lrt = came_from_lrt
        self.ui_lang_code = ui_lang_code

        # Data and state
        _write_crash_log("[__init__] Initializing data and state")
        _logger.info("Initializing data and state")
        self._generator: Optional[FLExTransRuleGenerator] = None
        self._flex_data: Optional[FLExData] = None
        self._current_rule_index = 0
        self._dirty = False
        self._result = WindowResult(saved=False, rule_index=None, launch_lrt=False)
        _write_crash_log("[__init__] Data and state initialized")

        # Services
        _write_crash_log("[__init__] Creating services")
        _logger.info("Creating services")
        self._producer = WebPageProducer()
        _write_crash_log("[__init__] WebPageProducer created")
        self._finder = ConstituentFinder()
        _write_crash_log("[__init__] ConstituentFinder created")
        self._preferences = ApplicationPreferences()
        _write_crash_log("[__init__] ApplicationPreferences created")
        _logger.info("Services created")

        # Selected constituents for context menu operations
        _write_crash_log("[__init__] Initializing selected constituents")
        self._selected_word: Optional[Word] = None
        self._selected_category = None
        self._selected_feature = None
        self._selected_affix = None

        # Setup UI
        _write_crash_log("[__init__] About to create UI")
        _logger.info("About to create UI")
        self._create_ui()
        _write_crash_log("[__init__] UI created successfully")
        _write_crash_log("[__init__] UI created successfully")
        _logger.info("UI created")

        _write_crash_log("[__init__] About to create context menus")
        _logger.info("About to create context menus")
        try:
            self._create_context_menus()
            _write_crash_log("[__init__] Context menus created successfully")
            _logger.info("Context menus created")
        except Exception as e:
            import traceback
            _write_crash_log(f"[__init__] FAILED to create context menus: {e}")
            _logger.error(f"Exception creating context menus: {e}")
            _logger.error(traceback.format_exc())
            # Don't crash - menus are optional, window can work without them
            _logger.warning("Continuing without context menus")

        _write_crash_log("[__init__] About to setup keyboard shortcuts")
        _logger.info("About to setup keyboard shortcuts")
        try:
            self._setup_keyboard_shortcuts()
            _write_crash_log("[__init__] Keyboard shortcuts setup successfully")
            _logger.info("Keyboard shortcuts setup")
        except Exception as e:
            import traceback
            _write_crash_log(f"[__init__] FAILED to setup keyboard shortcuts: {e}")
            _logger.error(f"Exception setting up keyboard shortcuts: {e}")
            _logger.error(traceback.format_exc())
            # Don't crash - shortcuts are optional
            _logger.warning("Continuing without keyboard shortcuts")

        # Setup WebView
        _write_crash_log("[__init__] About to setup WebView")
        _logger.info("About to setup WebView")
        self._setup_webview()
        _write_crash_log("[__init__] WebView setup complete")
        _logger.info("WebView setup complete")

        # Load data
        _write_crash_log("[__init__] About to load data")
        _logger.info("About to load data")
        self._load_data()
        _write_crash_log("[__init__] Data loaded successfully")
        _logger.info("Data loaded")

        # Restore window state
        _write_crash_log("[__init__] About to restore window state")
        _logger.info("About to restore window state")
        self._restore_window_state()
        _write_crash_log("[__init__] Window state restored successfully")
        _logger.info("Window state restored")

        _write_crash_log("[__init__] About to set window title")
        self.setWindowTitle(_translate("RuleAssistantLib", "FLExTrans Rule Assistant"))
        _write_crash_log("[__init__] Window title set successfully")
        _logger.info("Window title set")
        _write_crash_log("[__init__] RuleAssistantWindow.__init__() completed successfully")
        _logger.info("RuleAssistantWindow.__init__() completed successfully")

    def _create_ui(self) -> None:
        """Create the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left pane: rules list
        left_pane = self._create_left_pane()
        splitter.addWidget(left_pane)

        # Right pane: editor and browser
        right_pane = self._create_right_pane()
        splitter.addWidget(right_pane)

        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([200, 460])

        self.resize(660, 1000)

    def _create_left_pane(self) -> QWidget:
        """Create the left pane (rules list).

        Returns:
            QWidget containing the rules list
        """
        pane = QWidget()
        layout = QVBoxLayout(pane)

        # Title
        myTitle = _translate("RuleAssistantLib", "Rules")
        title = QLabel(myTitle)
        layout.addWidget(title)

        # Hint label
        hint = QLabel(_translate("RuleAssistantLib", "(Right-click to edit)"))
        hint.setStyleSheet("font-style: italic; color: gray;")
        layout.addWidget(hint)

        # Rules list
        self.rule_list = QListWidget()
        self.rule_list.itemSelectionChanged.connect(self._on_rule_selected)
        self.rule_list.customContextMenuRequested.connect(self._on_rule_list_context_menu)
        self.rule_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.rule_list)

        # Overwrite rules checkbox
        self.overwrite_checkbox = QCheckBox(_translate("RuleAssistantLib", "Overwrite rules(s)"))
        self.overwrite_checkbox.setToolTip(_translate("RuleAssistantLib", "Overwrite previous rule(s) that have the same name."))
        self.overwrite_checkbox.toggled.connect(self._on_overwrite_toggled)
        layout.addWidget(self.overwrite_checkbox)

        # Disjoint features button
        self.disjoint_button = QPushButton(_translate("RuleAssistantLib", "Set disjoint features"))
        self.disjoint_button.clicked.connect(self._on_disjoint_features)
        layout.addWidget(self.disjoint_button)

        return pane

    def _create_right_pane(self) -> QWidget:
        """Create the right pane (editor and browser).

        Returns:
            QWidget containing the editor controls and webviews
        """
        pane = QWidget()
        outer_layout = QVBoxLayout(pane)

        # Vertical splitter: top section (25%) / tree diagram (75%)
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        outer_layout.addWidget(v_splitter)

        # --- Top widget (name, description, test data, buttons) ---
        top_widget = QWidget()
        top_layout_v = QVBoxLayout(top_widget)

        # Top section: rule name, description, test data
        top_layout = QHBoxLayout()

        # Left: name and description
        left_top = QVBoxLayout()

        rule_name_label = QLabel(_translate("RuleAssistantLib", "Rule Name:"))
        self.rule_name_field = QLineEdit()
        self.rule_name_field.textChanged.connect(self._on_rule_name_changed)
        left_top.addWidget(rule_name_label)
        left_top.addWidget(self.rule_name_field)

        rule_desc_label = QLabel(_translate("RuleAssistantLib", "Description:"))
        self.rule_description_field = QPlainTextEdit()
        self.rule_description_field.setMaximumHeight(82)
        self.rule_description_field.textChanged.connect(self._on_rule_description_changed)
        left_top.addWidget(rule_desc_label)
        left_top.addWidget(self.rule_description_field)

        perm_layout = QHBoxLayout()
        perm_label = QLabel(_translate("RuleAssistantLib", "Create permutations:"))
        self.permutations_combo = QComboBox()
        # Store a stable key as item data so the displayed text can be translated
        # without affecting the logic that reads the selection.
        self.permutations_combo.addItem(_translate("RuleAssistantLib", "No"), "no")
        self.permutations_combo.addItem(_translate("RuleAssistantLib", "Including head-only rule"), "with head")
        self.permutations_combo.addItem(_translate("RuleAssistantLib", "Omitting head-only rule"), "not head")
        self.permutations_combo.currentIndexChanged.connect(self._on_permutations_changed)
        perm_layout.addWidget(perm_label)
        perm_layout.addWidget(self.permutations_combo)
        left_top.addLayout(perm_layout)

        top_layout.addLayout(left_top, 1)

        # Right: test data webview
        self.test_data_view = QWebEngineView()
        self.test_data_view.setMinimumWidth(300)
        top_layout.addWidget(self.test_data_view)

        top_layout_v.addLayout(top_layout)

        # Button bar
        button_layout = QHBoxLayout()
        self.test_lrt_button = QPushButton(_translate("RuleAssistantLib", "Test in LRT"))
        self.test_lrt_button.setToolTip(_translate("RuleAssistantLib", "Test in the Live Rule Tester tool."))
        self.test_lrt_button.clicked.connect(self._on_test_in_lrt)
        if self.came_from_lrt:
            self.test_lrt_button.setEnabled(False)
        button_layout.addWidget(self.test_lrt_button)

        self.save_button = QPushButton(_translate("RuleAssistantLib", "Save"))
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        self.save_create_button = QPushButton(_translate("RuleAssistantLib", "Save & Write"))
        self.save_create_button.clicked.connect(self._on_save_create)
        button_layout.addWidget(self.save_create_button)

        self.save_all_button = QPushButton(_translate("RuleAssistantLib", "Save & Write All"))
        self.save_all_button.clicked.connect(self._on_save_create_all)
        button_layout.addWidget(self.save_all_button)

        self.help_button = QPushButton(_translate("RuleAssistantLib", "Help"))
        self.help_button.clicked.connect(self._on_help)
        button_layout.addWidget(self.help_button)

        top_layout_v.addLayout(button_layout)

        v_splitter.addWidget(top_widget)

        # --- Bottom widget: main tree diagram (75%) ---
        self.tree_view = QWebEngineView()
        v_splitter.addWidget(self.tree_view)

        # Set split ratio: 25% top / 75% diagram
        # Use a large reference total so proportions are meaningful at any window size
        v_splitter.setSizes([250, 750])

        return pane

    def _setup_webview(self) -> None:
        """Setup QWebEngineView with optional QWebChannel bridge."""
        try:
            _write_crash_log("[webview] _setup_webview() starting")
            _logger.info("_setup_webview() starting")

            # Disable context menu on webview
            _write_crash_log("[webview] About to set context menu policy on tree_view")
            _logger.info("Setting context menu policy on tree_view")
            self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            _write_crash_log("[webview] Context menu policy set successfully")
            _logger.info("Context menu policy set")

            # Detect if we're in FlexTools mode (in-process) vs subprocess mode
            # RULE_ASSISTANT_STANDALONE=1: subprocess with isolated Qt event loop (can render)
            # RULE_ASSISTANT_STANDALONE not set: in-process within FlexTools (skip rendering)
            env_standalone = os.environ.get('RULE_ASSISTANT_STANDALONE')
            in_flextools = env_standalone != '1'
            in_flextools = False
            _write_crash_log(f"[webview] RULE_ASSISTANT_STANDALONE={env_standalone!r}, in_flextools={in_flextools}")
            _logger.info(f"RULE_ASSISTANT_STANDALONE={env_standalone!r}, in_flextools={in_flextools}")

            # Setup QWebChannel in subprocess mode only
            # In FlexTools (in-process) mode, skip to avoid conflicts
            if in_flextools:  # Skip QWebChannel in FlexTools in-process mode
                _write_crash_log("[webview] SKIPPING QWebChannel - will display tree as static HTML")
                _logger.warning("Skipping QWebChannel setup for stability")
                _logger.warning("Tree will display as static HTML - no interactive context menus")
                self._channel = None
                self._interactor = None
            else:
                # Standalone mode: setup QWebChannel for full interactivity
                try:
                    _write_crash_log("[webview] About to create QWebChannel")
                    _logger.info("Creating QWebChannel")
                    # Try with self.tree_view as parent instead of self.tree_view.page()
                    self._channel = QWebChannel(self.tree_view)
                    _write_crash_log("[webview] QWebChannel created successfully")
                    _logger.info("QWebChannel created successfully")

                    # Create interactor and register it
                    _write_crash_log("[webview] About to create WebPageInteractor")
                    _logger.info("Creating WebPageInteractor")
                    self._interactor = WebPageInteractor(self)
                    _write_crash_log("[webview] WebPageInteractor created successfully")
                    _logger.info("Registering object with QWebChannel")
                    _write_crash_log("[webview] About to register object with QWebChannel")
                    self._channel.registerObject("ftRuleGenApp", self._interactor)
                    _write_crash_log("[webview] Object registered with QWebChannel successfully")
                    _logger.info("Object registered with QWebChannel")

                    # Attach channel to page - this can crash in FlexTools mode
                    # Wrap in defensive try-catch
                    try:
                        _write_crash_log("[webview] About to set WebChannel on page")
                        _logger.info("Setting WebChannel on page")
                        self.tree_view.page().setWebChannel(self._channel)
                        _write_crash_log("[webview] WebChannel set on page successfully")
                        _logger.info("WebChannel set on page successfully")
                    except Exception as e:
                        _write_crash_log(f"[webview] FAILED to set WebChannel on page: {e}")
                        _logger.error(f"FAILED to set WebChannel on page: {e}")
                        import traceback
                        _logger.error(traceback.format_exc())
                        _write_crash_log("[webview] Continuing without WebChannel - interactivity disabled")
                        _logger.warning("WebChannel not attached to page - tree will be static display only")
                        # Don't crash - the window can still display the tree
                        self._channel = None
                        self._interactor = None

                except Exception as e:
                    _write_crash_log(f"[webview] FAILED to setup QWebChannel: {e}")
                    _logger.error(f"FAILED to setup QWebChannel: {e}")
                    import traceback
                    _logger.error(traceback.format_exc())
                    # Store the error but don't crash - the window can still display something
                    self._channel = None
                    self._interactor = None
                    _write_crash_log("[webview] QWebChannel setup failed - continuing without it")
                    _logger.warning("QWebChannel setup failed - tree view will have limited functionality")

            _write_crash_log("[webview] _setup_webview() completed successfully")
            _logger.info("_setup_webview() completed")
        except Exception as e:
            _write_crash_log(f"[webview] Exception in _setup_webview: {e}")
            import traceback
            _logger.error(f"Exception in _setup_webview: {e}")
            _logger.error(traceback.format_exc())
            raise

    @staticmethod
    def _add_action(menu: QMenu, text: str, slot) -> QAction:
        """Add a menu action and return it (typed; QMenu.addAction never returns None here)."""
        action = menu.addAction(text, slot)
        assert action is not None
        return action

    def _create_context_menus(self) -> None:
        """Create all context menus."""
        _write_crash_log("[menu] Creating word menu")
        # Word context menu
        self._word_menu = QMenu()
        _write_crash_log("[menu] Word menu created")
        self._word_menu.addAction(_translate("RuleAssistantLib", "Duplicate"), self._on_word_duplicate)
        self._word_menu.addSeparator()
        self._word_menu.addAction(_translate("RuleAssistantLib", "Change number"), self._on_word_change_number)
        self._cm_word_mark_as_head = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Mark as head"), self._on_word_mark_as_head)
        self._cm_word_remove_head = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Remove head marking"), self._on_word_remove_head)
        self._word_menu.addSeparator()
        self._word_menu.addAction(_translate("RuleAssistantLib", "Insert new before"), self._on_word_insert_before)
        self._word_menu.addAction(_translate("RuleAssistantLib", "Insert new after"), self._on_word_insert_after)
        self._word_menu.addSeparator()
        self._cm_word_insert_prefix = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Insert prefix"), self._on_word_insert_prefix)
        self._cm_word_insert_suffix = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Insert suffix"), self._on_word_insert_suffix)
        self._cm_word_insert_category = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Insert category"), self._on_word_insert_category)
        self._cm_word_insert_feature = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Insert feature"), self._on_word_insert_feature)
        self._word_menu.addSeparator()
        self._cm_word_move_left = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Move left"), self._on_word_move_left)
        self._cm_word_move_right = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Move right"), self._on_word_move_right)
        self._word_menu.addSeparator()
        self._cm_word_delete = self._add_action(self._word_menu, _translate("RuleAssistantLib", "Delete"), self._on_word_delete)

        # Category context menu
        self._category_menu = QMenu()
        self._category_menu.addAction(_translate("RuleAssistantLib", "Edit"), self._on_category_edit)
        self._category_menu.addSeparator()
        self._category_menu.addAction(_translate("RuleAssistantLib", "Delete"), self._on_category_delete)

        # Feature context menu
        self._feature_menu = QMenu()
        self._feature_menu.addAction(_translate("RuleAssistantLib", "Edit"), self._on_feature_edit)
        self._feature_menu.addAction(_translate("RuleAssistantLib", "Edit unmarked"), self._on_feature_edit_unmarked)
        self._cm_feature_edit_ranking = self._add_action(self._feature_menu, _translate("RuleAssistantLib", "Edit ranking"), self._on_feature_edit_ranking)
        self._feature_menu.addSeparator()
        self._feature_menu.addAction(_translate("RuleAssistantLib", "Delete"), self._on_feature_delete)
        self._cm_feature_delete_unmarked = self._add_action(self._feature_menu, _translate("RuleAssistantLib", "Delete unmarked"), self._on_feature_delete_unmarked)
        self._cm_feature_delete_ranking = self._add_action(self._feature_menu, _translate("RuleAssistantLib", "Delete ranking"), self._on_feature_delete_ranking)

        # Affix context menu
        self._affix_menu = QMenu()
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Duplicate"), self._on_affix_duplicate)
        self._affix_menu.addSeparator()
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Toggle affix type"), self._on_affix_toggle_type)
        self._affix_menu.addSeparator()
        self._cm_affix_insert_feature = self._add_action(self._affix_menu, _translate("RuleAssistantLib", "Insert feature"), self._on_affix_insert_feature)
        self._affix_menu.addSeparator()
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Insert new prefix before"), self._on_affix_insert_prefix_before)
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Insert new prefix after"), self._on_affix_insert_prefix_after)
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Insert new suffix before"), self._on_affix_insert_suffix_before)
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Insert new suffix after"), self._on_affix_insert_suffix_after)
        self._affix_menu.addSeparator()
        self._cm_affix_move_left = self._add_action(self._affix_menu, _translate("RuleAssistantLib", "Move left"), self._on_affix_move_left)
        self._cm_affix_move_right = self._add_action(self._affix_menu, _translate("RuleAssistantLib", "Move right"), self._on_affix_move_right)
        self._affix_menu.addSeparator()
        self._affix_menu.addAction(_translate("RuleAssistantLib", "Delete"), self._on_affix_delete)

        # Rule list context menu
        self._rule_menu = QMenu()
        self._rule_menu.addAction(_translate("RuleAssistantLib", "Duplicate"), self._on_rule_duplicate)
        self._rule_menu.addAction(_translate("RuleAssistantLib", "Insert new before"), self._on_rule_insert_before)
        self._rule_menu.addAction(_translate("RuleAssistantLib", "Insert new after"), self._on_rule_insert_after)
        self._rule_menu.addSeparator()
        self._cm_rule_move_up = self._add_action(self._rule_menu, _translate("RuleAssistantLib", "Move up"), self._on_rule_move_up)
        self._cm_rule_move_down = self._add_action(self._rule_menu, _translate("RuleAssistantLib", "Move down"), self._on_rule_move_down)
        self._rule_menu.addSeparator()
        self._rule_menu.addAction(_translate("RuleAssistantLib", "Delete"), self._on_rule_delete)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        _write_crash_log("[shortcut] Creating Ctrl+S shortcut")
        QShortcut(QKeySequence("Ctrl+S"), self, self._on_save)
        _write_crash_log("[shortcut] Ctrl+S shortcut created successfully")

    def _load_data(self) -> None:
        """Load rule and FLEx data files."""
        try:
            _write_crash_log("[load_data] _load_data() starting")
            _logger.info("_load_data() starting")

            # Load rules
            _write_crash_log("[load_data] About to load rules")
            _logger.info(f"Loading rules from: {self.rule_file}")
            self._generator = XMLBackEndProvider.load_data_from_file(self.rule_file)
            _write_crash_log(f"[load_data] Rules loaded: {len(self._generator.flex_trans_rules) if self._generator else 0}")
            _logger.info(f"Loaded {len(self._generator.flex_trans_rules) if self._generator else 0} rules")

            # Load FLEx data (optional)
            _write_crash_log("[load_data] About to load FLEx data")
            if self.flex_data_file:
                _logger.info(f"Loading FLEx data from: {self.flex_data_file}")
                self._flex_data = XMLFLExDataBackEndProvider.load_data_from_file(self.flex_data_file)
                _write_crash_log("[load_data] FLEx data loaded")
                _logger.info("FLEx data loaded")
            else:
                _write_crash_log("[load_data] No FLEx data file provided")
                _logger.info("No FLEx data file provided")

            # Populate rule list
            _write_crash_log("[load_data] About to populate rule list")
            _logger.info("Populating rule list")
            self._populate_rule_list()
            _write_crash_log(f"[load_data] Rule list populated")
            _logger.info(f"Rule list populated with {self.rule_list.count()} items")

            # Load test data
            _write_crash_log("[load_data] About to load test data")

            # Check if we're in FlexTools mode - loading HTML crashes in FlexTools
            env_standalone = os.environ.get('RULE_ASSISTANT_STANDALONE')
            in_flextools = env_standalone != '1'
            in_flextools = False

            if self.test_data_file and Path(self.test_data_file).exists():
                _write_crash_log(f"[load_data] Test data file exists: {self.test_data_file}")
                _logger.info(f"Loading test data from: {self.test_data_file}")

                if in_flextools:
                    _write_crash_log("[load_data] SKIPPING test data load in FlexTools mode (would crash)")
                    _logger.warning("Skipping test data load in FlexTools mode")
                else:
                    try:
                        _write_crash_log("[load_data] About to call test_data_view.load() (standalone mode)")
                        self.test_data_view.load(QUrl.fromLocalFile(self.test_data_file))
                        _write_crash_log("[load_data] test_data_view.load() completed")
                    except Exception as e:
                        _write_crash_log(f"[load_data] FAILED to load test data: {e}")
                        _logger.error(f"Failed to load test data: {e}")
                        import traceback
                        _logger.error(traceback.format_exc())
                _write_crash_log("[load_data] Test data loaded")
                _logger.info("Test data loaded")
            else:
                _write_crash_log(f"[load_data] No test data file or file doesn't exist")
                _logger.info(f"No test data: file={self.test_data_file}, exists={Path(self.test_data_file).exists() if self.test_data_file else False}")

            _write_crash_log("[load_data] About to mark as not dirty")
            self._dirty = False
            _write_crash_log("[load_data] _load_data() completed successfully")
            _logger.info("_load_data() completed successfully")
        except Exception as e:
            _write_crash_log(f"[load_data] Exception in _load_data: {e}")
            import traceback
            _logger.error(f"Exception in _load_data: {e}")
            _logger.error(traceback.format_exc())
            QMessageBox.critical(
                self,
                _translate("RuleAssistantLib", "Could not load data"),
                _translate("RuleAssistantLib", "Could not load data from file:\n") + str(e),
            )

    def _populate_rule_list(self) -> None:
        """Populate the rule list from generator."""
        try:
            _write_crash_log("[populate] _populate_rule_list() starting")
            self.rule_list.clear()
            _write_crash_log("[populate] Rule list cleared")

            if self._generator:
                _write_crash_log(f"[populate] About to add {len(self._generator.flex_trans_rules)} rules")
                for i, rule in enumerate(self._generator.flex_trans_rules):
                    _write_crash_log(f"[populate] Processing rule {i}: {rule.name}")
                    item = QListWidgetItem(rule.name or f"Rule {i+1}")
                    self.rule_list.addItem(item)
                    _write_crash_log(f"[populate] Added rule {i} to list")

            _write_crash_log(f"[populate] Total rules in list: {self.rule_list.count()}")

            # Select first rule
            _write_crash_log("[populate] About to select first rule")
            if self.rule_list.count() > 0:
                try:
                    _write_crash_log("[populate] Calling setCurrentRow(0)")
                    self.rule_list.setCurrentRow(0)
                    _write_crash_log("[populate] setCurrentRow(0) completed")
                except Exception as e:
                    _write_crash_log(f"[populate] FAILED to select first rule: {e}")
                    _logger.error(f"Failed to select first rule: {e}")
                    import traceback
                    _logger.error(traceback.format_exc())
                _write_crash_log("[populate] First rule selected")
            else:
                _write_crash_log("[populate] No rules to select")

            _write_crash_log("[populate] _populate_rule_list() completed successfully")
        except Exception as e:
            _write_crash_log(f"[populate] Exception in _populate_rule_list: {e}")
            import traceback
            _logger.error(f"Exception in _populate_rule_list: {e}")
            _logger.error(traceback.format_exc())
            raise

    def _show_rule(self, index: int) -> None:
        """Show a rule in the editor.

        Args:
            index: Rule index
        """
        try:
            _write_crash_log(f"[show_rule] _show_rule({index}) starting")
            if not self._generator or index < 0 or index >= len(self._generator.flex_trans_rules):
                _write_crash_log(f"[show_rule] Invalid index: {index}")
                return

            self._current_rule_index = index
            rule = self._generator.flex_trans_rules[index]
            _write_crash_log(f"[show_rule] Got rule at index {index}")

            # Update fields
            _write_crash_log("[show_rule] About to update rule name field")
            self.rule_name_field.setText(rule.name)
            _write_crash_log("[show_rule] Rule name field updated")

            _write_crash_log("[show_rule] About to update rule description field")
            self.rule_description_field.setPlainText(rule.description)
            _write_crash_log("[show_rule] Rule description field updated")

            _write_crash_log("[show_rule] About to update permutations combo")
            perm_key = {
                PermutationsValue.no: "no",
                PermutationsValue.not_head: "not head",
                PermutationsValue.with_head: "with head",
            }.get(rule.create_permutations, "with head")
            perm_index = self.permutations_combo.findData(perm_key)
            self.permutations_combo.setCurrentIndex(perm_index if perm_index >= 0 else 0)
            _write_crash_log("[show_rule] Permutations combo updated")

            # Generate and show HTML
            _write_crash_log("[show_rule] About to generate HTML")
            html = self._producer.produce_web_page(rule)
            _write_crash_log(f"[show_rule] HTML generated, length={len(html)}")

            # Check if we're in FlexTools mode - setHtml crashes in FlexTools
            env_standalone = os.environ.get('RULE_ASSISTANT_STANDALONE')
            in_flextools = env_standalone != '1'
            in_flextools = False
            _write_crash_log(f"[show_rule] RULE_ASSISTANT_STANDALONE={env_standalone!r}, in_flextools={in_flextools}")

            if in_flextools:
                _write_crash_log("[show_rule] SKIPPING setHtml in FlexTools mode - tree view will remain empty")
                _logger.warning("Skipping tree view HTML update in FlexTools mode")
                # Don't call setHtml - it crashes in FlexTools mode
                # The tree view will be empty, but the rule can still be edited
            else:
                _write_crash_log("[show_rule] About to call setHtml on tree_view (standalone mode)")
                _write_crash_log(f"[show_rule] tree_view size: {self.tree_view.width()}x{self.tree_view.height()}")
                try:
                    self.tree_view.setHtml(html, QUrl("qrc:///"))
                    _write_crash_log("[show_rule] setHtml completed successfully")
                    _write_crash_log(f"[show_rule] tree_view size after setHtml: {self.tree_view.width()}x{self.tree_view.height()}")
                except Exception as e:
                    _write_crash_log(f"[show_rule] setHtml failed with exception: {e}")
                    _logger.error(f"setHtml failed: {e}")
                    import traceback
                    _logger.error(traceback.format_exc())

            _write_crash_log("[show_rule] _show_rule() completed successfully")
        except Exception as e:
            _write_crash_log(f"[show_rule] Exception in _show_rule: {e}")
            import traceback
            _logger.error(f"Exception in _show_rule: {e}")
            _logger.error(traceback.format_exc())

        # Update overwrite checkbox
        self.overwrite_checkbox.setChecked(
            self._generator.overwrite_rules.value == "yes"
        )

    def _refresh_rule_view(self) -> None:
        """Refresh the current rule display after editing."""
        if self._generator and 0 <= self._current_rule_index < len(self._generator.flex_trans_rules):
            rule = self._generator.flex_trans_rules[self._current_rule_index]
            # Update list item text
            item = self.rule_list.item(self._current_rule_index)
            if item:
                item.setText(rule.name or f"Rule {self._current_rule_index + 1}")
            # Re-render HTML
            html = self._producer.produce_web_page(rule)
            self.tree_view.setHtml(html, QUrl("qrc:///"))

    def _restore_window_state(self) -> None:
        """Restore window size and position from preferences."""
        try:
            _write_crash_log("[window_state] _restore_window_state() starting")
            x = self._preferences.get_window_position_x()
            y = self._preferences.get_window_position_y()
            w = self._preferences.get_window_width()
            h = self._preferences.get_window_height()
            maximized = self._preferences.get_window_maximized()
            _write_crash_log(f"[window_state] Got preferences: x={x}, y={y}, w={w}, h={h}, max={maximized}")

            # Ensure window is visible on screen (not above y=0)
            if y < 0:
                y = 50
                _write_crash_log(f"[window_state] Adjusted y from negative to {y}")
            if x < 0:
                x = 50
                _write_crash_log(f"[window_state] Adjusted x from negative to {x}")
            if w < 400:
                w = 1200
                _write_crash_log(f"[window_state] Adjusted w from {w} to 1200")
            if h < 300:
                h = 800
                _write_crash_log(f"[window_state] Adjusted h from {h} to 800")

            _write_crash_log("[window_state] About to call setGeometry")
            self.setGeometry(x, y, w, h)
            _write_crash_log("[window_state] setGeometry completed")

            # Check if we're in FlexTools mode - show() crashes in FlexTools
            env_standalone = os.environ.get('RULE_ASSISTANT_STANDALONE')
            in_flextools = env_standalone != '1'
            in_flextools = False

            _write_crash_log(f"[window_state] RULE_ASSISTANT_STANDALONE={env_standalone!r}, in_flextools={in_flextools}")

            if in_flextools:
                _write_crash_log("[window_state] SKIPPING show/showMaximized in FlexTools mode")
                _logger.warning("Skipping show/showMaximized in FlexTools mode - window managed by FlexTools")
            else:
                if maximized:
                    _write_crash_log("[window_state] About to call showMaximized")
                    self.showMaximized()
                    _write_crash_log("[window_state] showMaximized completed")
                else:
                    _write_crash_log("[window_state] About to call show")
                    self.show()
                    _write_crash_log("[window_state] show completed")

            # Restore selected rule
            _write_crash_log("[window_state] About to restore selected rule")
            last_rule = self._preferences.get_last_selected_rule()
            _write_crash_log(f"[window_state] last_rule={last_rule}, rule_list.count()={self.rule_list.count()}")
            if 0 <= last_rule < self.rule_list.count():
                _write_crash_log(f"[window_state] About to setCurrentRow({last_rule})")
                self.rule_list.setCurrentRow(last_rule)
                _write_crash_log("[window_state] setCurrentRow completed")

            _write_crash_log("[window_state] _restore_window_state() completed successfully")
        except Exception as e:
            _write_crash_log(f"[window_state] Exception in _restore_window_state: {e}")
            import traceback
            _logger.error(f"Exception in _restore_window_state: {e}")
            _logger.error(traceback.format_exc())

    def _save_window_state(self) -> None:
        """Save window state to preferences."""
        self._preferences.set_window_position_x(self.x())
        self._preferences.set_window_position_y(self.y())
        self._preferences.set_window_width(self.width())
        self._preferences.set_window_height(self.height())
        self._preferences.set_window_maximized(self.isMaximized())
        self._preferences.set_last_selected_rule(self._current_rule_index)
        self._preferences.sync()

    def process_item_clicked_on(self, item: str, x: int, y: int) -> None:
        """Process a click on a tree element.

        Args:
            item: Element identifier (e.g., "w.5")
            x: Screen X coordinate
            y: Screen Y coordinate
        """
        if not self._generator:
            return

        rule = self._generator.flex_trans_rules[self._current_rule_index]
        type_code = item[0]
        try:
            identifier = int(item[2:])
        except (ValueError, IndexError):
            return

        # Find the constituent
        constituent = self._finder.find_constituent(rule, identifier)
        if not constituent:
            return

        pos = QPoint(x, y)

        # Show appropriate context menu based on type
        if type_code == "w":
            self._selected_word = constituent
            self._enable_disable_word_menu_items(constituent)
            self._word_menu.exec(pos)
        elif type_code == "c":
            self._selected_category = constituent
            self._category_menu.exec(pos)
        elif type_code == "f":
            self._selected_feature = constituent
            self._enable_disable_feature_menu_items(constituent)
            self._feature_menu.exec(pos)
        elif type_code == "a":
            self._selected_affix = constituent
            self._enable_disable_affix_menu_items(constituent)
            self._affix_menu.exec(pos)
        elif type_code == "p":
            # Phrase click does nothing
            pass

    # ------------------------------------------------------------------
    # Context-menu item enable/disable (mirrors the Java MainController so
    # operations that don't apply to the clicked-on item are greyed out).
    # ------------------------------------------------------------------
    def _flex_category_has_valid_features(self, word, phrase_type) -> bool:
        """True if the word's (or corresponding source word's) category exists in
        the FLEx data for this phrase and that category has valid features."""
        if not self._flex_data:
            return False
        cat = word.get_category_of_word_or_corresponding_source_word()
        if not cat or not cat.name:
            return False
        for flex_cat in self._flex_data.get_flex_categories_for_phrase(phrase_type):
            if flex_cat.abbreviation == cat.name:
                return len(flex_cat.valid_features) > 0
        return False

    def _enable_disable_word_menu_items(self, word) -> None:
        from RAutils import PhraseType, HeadValue
        phrase = word.parent
        if phrase is None:
            return
        phrase_type = phrase.phrase_type
        index = phrase.words.index(word)

        self._cm_word_move_left.setEnabled(index != 0)
        self._cm_word_move_right.setEnabled(index != len(phrase.words) - 1)
        self._cm_word_delete.setEnabled(not (index == 0 and len(phrase.words) == 1))

        # Can only insert a category if the word doesn't already have one.
        cat = word.get_category_of_word_or_corresponding_source_word()
        self._cm_word_insert_category.setEnabled(not (cat and cat.name))

        if phrase_type == PhraseType.source:
            self._cm_word_mark_as_head.setEnabled(False)
            self._cm_word_remove_head.setEnabled(False)
        elif word.head == HeadValue.yes:
            self._cm_word_mark_as_head.setEnabled(False)
            self._cm_word_remove_head.setEnabled(True)
        else:
            self._cm_word_mark_as_head.setEnabled(True)
            self._cm_word_remove_head.setEnabled(False)

        # Affixes can only be inserted on a word that has none yet.
        no_affixes = len(word.affixes) == 0
        self._cm_word_insert_prefix.setEnabled(no_affixes)
        self._cm_word_insert_suffix.setEnabled(no_affixes)

        self._cm_word_insert_feature.setEnabled(
            self._flex_category_has_valid_features(word, phrase_type))

    def _enable_disable_affix_menu_items(self, affix) -> None:
        word = affix.parent
        if word is None:
            return
        index = word.affixes.index(affix)
        self._cm_affix_move_left.setEnabled(index != 0)
        self._cm_affix_move_right.setEnabled(index != len(word.affixes) - 1)

        phrase = word.parent
        phrase_type = phrase.phrase_type if phrase is not None else None
        self._cm_affix_insert_feature.setEnabled(
            self._flex_category_has_valid_features(word, phrase_type))

    def _enable_disable_feature_menu_items(self, feature) -> None:
        from RAutils import PhraseType, Word, Affix
        # Find the word that owns this feature (directly, or via an affix).
        owner = feature.parent
        this_word = None
        if isinstance(owner, Word):
            this_word = owner
        elif isinstance(owner, Affix) and isinstance(owner.parent, Word):
            this_word = owner.parent

        phrase = this_word.parent if this_word is not None else None
        if phrase is not None and phrase.phrase_type == PhraseType.target and this_word is not None:
            # Ranking only makes sense when the word has more than one feature
            # (counting features on the word and on all its affixes).
            feature_count = len(this_word.features) + sum(len(a.features) for a in this_word.affixes)
            self._cm_feature_edit_ranking.setEnabled(feature_count > 1)
        else:
            self._cm_feature_edit_ranking.setEnabled(False)

        self._cm_feature_delete_unmarked.setEnabled(len(feature.unmarked) > 0)
        self._cm_feature_delete_ranking.setEnabled(feature.ranking > 0)

    def _enable_disable_rule_menu_items(self) -> None:
        self._cm_rule_move_up.setEnabled(self._current_rule_index != 0)
        last = len(self._generator.flex_trans_rules) - 1 if self._generator else 0
        self._cm_rule_move_down.setEnabled(self._current_rule_index != last)

    def _mark_dirty(self) -> None:
        """Mark the document as changed."""
        if not self._dirty:
            self._dirty = True
            # Update title with asterisk
            current_title = self.windowTitle()
            if not current_title.endswith("*"):
                self.setWindowTitle(current_title + "*")

    # Signal handlers
    def _on_rule_selected(self) -> None:
        """Handle rule selection in list."""
        try:
            _write_crash_log("[select] _on_rule_selected() called")
            row = self.rule_list.currentRow()
            _write_crash_log(f"[select] Current row: {row}")
            if row >= 0:
                _write_crash_log(f"[select] About to show rule {row}")
                self._show_rule(row)
                _write_crash_log(f"[select] Rule {row} shown successfully")
            _write_crash_log("[select] _on_rule_selected() completed")
        except Exception as e:
            _write_crash_log(f"[select] Exception in _on_rule_selected: {e}")
            import traceback
            _logger.error(f"Exception in _on_rule_selected: {e}")
            _logger.error(traceback.format_exc())

    def _on_rule_name_changed(self) -> None:
        """Handle rule name text change."""
        if self._generator and 0 <= self._current_rule_index < len(self._generator.flex_trans_rules):
            self._generator.flex_trans_rules[self._current_rule_index].name = self.rule_name_field.text()
            # Update list
            item = self.rule_list.item(self._current_rule_index)
            if item:
                item.setText(self.rule_name_field.text())
            self._mark_dirty()

    def _on_rule_description_changed(self) -> None:
        """Handle rule description text change."""
        if self._generator and 0 <= self._current_rule_index < len(self._generator.flex_trans_rules):
            self._generator.flex_trans_rules[self._current_rule_index].description = (
                self.rule_description_field.toPlainText()
            )
            self._mark_dirty()

    def _on_permutations_changed(self) -> None:
        """Handle permutations combo change."""
        if self._generator and 0 <= self._current_rule_index < len(self._generator.flex_trans_rules):
            key_to_enum = {
                "no": PermutationsValue.no,
                "with head": PermutationsValue.with_head,
                "not head": PermutationsValue.not_head,
            }
            self._generator.flex_trans_rules[self._current_rule_index].create_permutations = (
                key_to_enum.get(self.permutations_combo.currentData(), PermutationsValue.with_head)
            )
            self._mark_dirty()

    def _on_overwrite_toggled(self) -> None:
        """Handle overwrite checkbox toggle."""
        from RAutils import OverwriteRulesValue
        if self._generator:
            self._generator.overwrite_rules = (
                OverwriteRulesValue.yes if self.overwrite_checkbox.isChecked()
                else OverwriteRulesValue.no
            )
            self._mark_dirty()

    def _on_save(self) -> None:
        """Handle Save button."""
        if self._generator:
            XMLBackEndProvider.save_data_to_file(self._generator, self.rule_file)
            self._dirty = False
            # Update title
            current_title = self.windowTitle()
            if current_title.endswith("*"):
                self.setWindowTitle(current_title[:-1])
            QMessageBox.information(self, _translate("RuleAssistantLib", "Saved"), _translate("RuleAssistantLib", "Rules saved successfully"))

    def _on_save_create(self) -> None:
        """Handle Save/Create button."""
        if not self._generator:
            return
        rule = self._generator.flex_trans_rules[self._current_rule_index]
        is_valid, error_msg = ValidityChecker.validate_rule(rule)
        if not is_valid:
            QMessageBox.critical(self, _translate("RuleAssistantLib", "Problem with rule"), error_msg)
            return
        self._on_save()
        self._result = WindowResult(saved=True, rule_index=self._current_rule_index, launch_lrt=False)
        self.close()

    def _on_save_create_all(self) -> None:
        """Handle Save/Create All button."""
        if not self._generator:
            return
        for i, rule in enumerate(self._generator.flex_trans_rules):
            is_valid, error_msg = ValidityChecker.validate_rule(rule)
            if not is_valid:
                QMessageBox.critical(self, _translate("RuleAssistantLib", "Problem with rule"), error_msg)
                return
        self._on_save()
        self._result = WindowResult(saved=True, rule_index=None, launch_lrt=False)
        self.close()

    def _on_test_in_lrt(self) -> None:
        """Handle Test In LRT button."""
        # TODO: Implement with a confirmation dialog
        pass

    def _on_help(self) -> None:
        """Handle Help button."""
        QMessageBox.information(self, _translate("RuleAssistantLib", "Help"), _translate("RuleAssistantLib", "See documentation for help"))

    def _on_disjoint_features(self) -> None:
        """Handle Disjoint Features button."""
        if not self._generator or not self._flex_data:
            QMessageBox.warning(self, _translate("RuleAssistantLib", "Error"), _translate("RuleAssistantLib", "No data loaded"))
            return

        dialog = DisjointFeaturesEditorDialog(self._generator, self._flex_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_rule_list_context_menu(self, pos: QPoint) -> None:
        """Handle rule list context menu."""
        item = self.rule_list.itemAt(pos)
        if item:
            self._enable_disable_rule_menu_items()
            self._rule_menu.exec(self.rule_list.mapToGlobal(pos))

    # Word menu handlers
    def _on_word_duplicate(self) -> None:
        """Duplicate selected word."""
        if not self._selected_word or not self._generator:
            return

        from copy import deepcopy
        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if not phrase:
            return

        index = phrase.words.index(self._selected_word)
        new_word = deepcopy(self._selected_word)
        phrase.words.insert(index + 1, new_word)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_word_change_number(self) -> None:
        """Change selected word's number."""
        if not self._selected_word:
            return

        new_id, ok = QInputDialog.getText(
            self, _translate("RuleAssistantLib", "Word Number"),
            _translate("RuleAssistantLib", "Choose word number:"),
            text=self._selected_word.word_id
        )
        if ok and new_id:
            old_id = self._selected_word.word_id
            # Update in both source and target phrases
            if self._generator:
                rule = self._generator.flex_trans_rules[self._current_rule_index]
                # Find and update source
                for word in rule.source.words:
                    if word.word_id == old_id:
                        word.word_id = new_id
                # Find and update target
                for word in rule.target.words:
                    if word.word_id == old_id:
                        word.word_id = new_id
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_word_mark_as_head(self) -> None:
        """Mark selected word as head."""
        if not self._selected_word or not self._generator:
            return

        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if phrase:
            phrase.mark_word_as_head(self._selected_word)
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_word_remove_head(self) -> None:
        """Remove head marking from selected word."""
        if not self._selected_word:
            return

        from RAutils import HeadValue
        self._selected_word.head = HeadValue.no
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_word_insert_before(self) -> None:
        """Insert word before selected word."""
        if not self._selected_word or not self._generator:
            return

        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if not phrase:
            return

        index = phrase.words.index(self._selected_word)
        phrase.insert_new_word_at(index)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_word_insert_after(self) -> None:
        """Insert word after selected word."""
        if not self._selected_word or not self._generator:
            return

        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if not phrase:
            return

        index = phrase.words.index(self._selected_word)
        phrase.insert_new_word_at(index + 1)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_word_insert_prefix(self) -> None:
        """Insert prefix on selected word."""
        if not self._selected_word:
            return

        from RAutils import Affix
        from RAutils import AffixType
        new_affix = Affix(affix_type=AffixType.prefix)
        self._selected_word.affixes.append(new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_word_insert_suffix(self) -> None:
        """Insert suffix on selected word."""
        if not self._selected_word:
            return

        from RAutils import Affix
        from RAutils import AffixType
        new_affix = Affix(affix_type=AffixType.suffix)
        self._selected_word.affixes.append(new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_word_insert_category(self) -> None:
        """Insert category on selected word."""
        if not self._selected_word or not self._flex_data:
            return

        # Get all available categories
        all_categories = []
        if self._flex_data.source_data:
            all_categories.extend(self._flex_data.source_data.categories)
        if self._flex_data.target_data:
            all_categories.extend(self._flex_data.target_data.categories)

        # Remove duplicates and sort
        seen = set()
        unique_categories = []
        for cat in all_categories:
            if cat.abbreviation not in seen:
                unique_categories.append(cat)
                seen.add(cat.abbreviation)

        if not unique_categories:
            QMessageBox.warning(self, _translate("RuleAssistantLib", "Error"), _translate("RuleAssistantLib", "No categories available"))
            return

        # Get current category for pre-selection
        from RAutils import Category
        current_category = Category(name=self._selected_word.word_category) if self._selected_word.word_category else None

        dialog = CategoryChooserDialog(unique_categories, current_category, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chosen = dialog.get_chosen_category()
            if chosen:
                self._selected_word.word_category = chosen.abbreviation
                self._selected_word.category_constituent = Category(name=chosen.abbreviation)
                self._mark_dirty()
                self._refresh_rule_view()

    def _on_word_insert_feature(self) -> None:
        """Insert feature on selected word."""
        if not self._selected_word or not self._flex_data:
            return

        # Get all available features
        all_features = []
        if self._flex_data.source_data:
            all_features.extend(self._flex_data.source_data.features)
        if self._flex_data.target_data:
            all_features.extend(self._flex_data.target_data.features)

        if not all_features:
            QMessageBox.warning(self, _translate("RuleAssistantLib", "Error"), _translate("RuleAssistantLib", "No features available"))
            return

        dialog = FeatureValueChooserDialog(all_features, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_chosen_value()
            if result:
                flex_feature, flex_value = result
                from RAutils import Feature
                new_feature = Feature(
                    label=flex_feature.name,
                    value=flex_value.abbreviation
                )
                self._selected_word.features.append(new_feature)
                self._mark_dirty()
                self._refresh_rule_view()

    def _on_word_move_left(self) -> None:
        """Move selected word left."""
        if not self._selected_word or not self._generator:
            return

        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if not phrase:
            return

        index = phrase.words.index(self._selected_word)
        if index > 0:
            phrase.swap_position_of_words(index, index - 1)
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_word_move_right(self) -> None:
        """Move selected word right."""
        if not self._selected_word or not self._generator:
            return

        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if not phrase:
            return

        index = phrase.words.index(self._selected_word)
        if index < len(phrase.words) - 1:
            phrase.swap_position_of_words(index, index + 1)
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_word_delete(self) -> None:
        """Delete selected word."""
        if not self._selected_word or not self._generator:
            return

        phrase = self._find_phrase_containing_word(
            self._generator.flex_trans_rules[self._current_rule_index],
            self._selected_word
        )
        if phrase:
            index = phrase.words.index(self._selected_word)
            phrase.words.pop(index)
            self._mark_dirty()
            self._refresh_rule_view()

    # Category menu handlers
    def _on_category_edit(self) -> None:
        """Edit selected category."""
        if not self._selected_category or not self._flex_data:
            return

        # Get all available categories
        all_categories = []
        if self._flex_data.source_data:
            all_categories.extend(self._flex_data.source_data.categories)
        if self._flex_data.target_data:
            all_categories.extend(self._flex_data.target_data.categories)

        # Remove duplicates
        seen = set()
        unique_categories = []
        for cat in all_categories:
            if cat.abbreviation not in seen:
                unique_categories.append(cat)
                seen.add(cat.abbreviation)

        if not unique_categories:
            return

        from RAutils import Category
        current_category = Category(name=self._selected_category.name) if self._selected_category.name else None

        dialog = CategoryChooserDialog(unique_categories, current_category, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chosen = dialog.get_chosen_category()
            if chosen:
                self._selected_category.name = chosen.abbreviation
                self._mark_dirty()
                self._refresh_rule_view()

    def _on_category_delete(self) -> None:
        """Delete selected category."""
        if not self._selected_category or not self._generator:
            return

        rule = self._generator.flex_trans_rules[self._current_rule_index]
        # Find parent word and clear its category
        self._find_and_clear_category(rule, self._selected_category)
        self._mark_dirty()
        self._refresh_rule_view()

    # Feature menu handlers
    def _on_feature_edit(self) -> None:
        """Edit selected feature."""
        if not self._selected_feature or not self._flex_data:
            return

        # Get all available features
        all_features = []
        if self._flex_data.source_data:
            all_features.extend(self._flex_data.source_data.features)
        if self._flex_data.target_data:
            all_features.extend(self._flex_data.target_data.features)

        if not all_features:
            return

        from RAutils import Feature
        # Pre-select current feature for dialog
        current_feature = Feature(
            label=self._selected_feature.label,
            value=self._selected_feature.value
        ) if self._selected_feature.label else None

        dialog = FeatureValueChooserDialog(all_features, current_feature, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_chosen_value()
            if result:
                flex_feature, flex_value = result
                self._selected_feature.label = flex_feature.name
                self._selected_feature.value = flex_value.abbreviation
                self._selected_feature.match = ""
                self._mark_dirty()
                self._refresh_rule_view()

    def _on_feature_edit_unmarked(self) -> None:
        """Edit unmarked value of selected feature."""
        if not self._selected_feature:
            return

        text, ok = QInputDialog.getText(
            self, _translate("RuleAssistantLib", "Edit unmarked"),
            _translate("RuleAssistantLib", "Enter unmarked value:"),
            text=self._selected_feature.unmarked
        )
        if ok:
            self._selected_feature.unmarked = text
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_feature_edit_ranking(self) -> None:
        """Edit ranking of selected feature."""
        if not self._selected_feature:
            return

        value, ok = QInputDialog.getInt(
            self, _translate("RuleAssistantLib", "Ranking for Feature"),
            _translate("RuleAssistantLib", "Choose ranking:"),
            self._selected_feature.ranking,
            0, 9999, 1
        )
        if ok:
            self._selected_feature.ranking = value
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_feature_delete(self) -> None:
        """Delete selected feature."""
        if not self._selected_feature or not self._generator:
            return

        rule = self._generator.flex_trans_rules[self._current_rule_index]
        # Find parent word or affix and remove feature
        self._find_and_remove_feature(rule, self._selected_feature)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_feature_delete_unmarked(self) -> None:
        """Delete unmarked value from selected feature."""
        if not self._selected_feature:
            return
        self._selected_feature.unmarked = ""
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_feature_delete_ranking(self) -> None:
        """Delete ranking from selected feature."""
        if not self._selected_feature:
            return
        self._selected_feature.ranking = 0
        self._mark_dirty()
        self._refresh_rule_view()

    # Affix menu handlers
    def _on_affix_duplicate(self) -> None:
        """Duplicate selected affix."""
        if not self._selected_affix or not self._selected_word:
            return

        from copy import deepcopy
        index = self._selected_word.affixes.index(self._selected_affix)
        new_affix = deepcopy(self._selected_affix)
        self._selected_word.affixes.insert(index + 1, new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_affix_toggle_type(self) -> None:
        """Toggle affix type (prefix <-> suffix)."""
        if not self._selected_affix:
            return

        from RAutils import AffixType
        self._selected_affix.affix_type = (
            AffixType.suffix if self._selected_affix.affix_type == AffixType.prefix
            else AffixType.prefix
        )
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_affix_insert_feature(self) -> None:
        """Insert feature on selected affix."""
        if not self._selected_affix or not self._flex_data:
            return

        # Get all available features
        all_features = []
        if self._flex_data.source_data:
            all_features.extend(self._flex_data.source_data.features)
        if self._flex_data.target_data:
            all_features.extend(self._flex_data.target_data.features)

        if not all_features:
            QMessageBox.warning(self, _translate("RuleAssistantLib", "Error"), _translate("RuleAssistantLib", "No features available"))
            return

        dialog = FeatureValueChooserDialog(all_features, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.get_chosen_value()
            if result:
                flex_feature, flex_value = result
                from RAutils import Feature
                new_feature = Feature(
                    label=flex_feature.name,
                    value=flex_value.abbreviation
                )
                self._selected_affix.features.append(new_feature)
                self._mark_dirty()
                self._refresh_rule_view()

    def _on_affix_insert_prefix_before(self) -> None:
        """Insert prefix before selected affix."""
        if not self._selected_affix or not self._selected_word:
            return

        from RAutils import Affix
        from RAutils import AffixType
        index = self._selected_word.affixes.index(self._selected_affix)
        new_affix = Affix(affix_type=AffixType.prefix)
        self._selected_word.affixes.insert(index, new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_affix_insert_prefix_after(self) -> None:
        """Insert prefix after selected affix."""
        if not self._selected_affix or not self._selected_word:
            return

        from RAutils import Affix
        from RAutils import AffixType
        index = self._selected_word.affixes.index(self._selected_affix)
        new_affix = Affix(affix_type=AffixType.prefix)
        self._selected_word.affixes.insert(index + 1, new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_affix_insert_suffix_before(self) -> None:
        """Insert suffix before selected affix."""
        if not self._selected_affix or not self._selected_word:
            return

        from RAutils import Affix
        from RAutils import AffixType
        index = self._selected_word.affixes.index(self._selected_affix)
        new_affix = Affix(affix_type=AffixType.suffix)
        self._selected_word.affixes.insert(index, new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_affix_insert_suffix_after(self) -> None:
        """Insert suffix after selected affix."""
        if not self._selected_affix or not self._selected_word:
            return

        from RAutils import Affix
        from RAutils import AffixType
        index = self._selected_word.affixes.index(self._selected_affix)
        new_affix = Affix(affix_type=AffixType.suffix)
        self._selected_word.affixes.insert(index + 1, new_affix)
        self._mark_dirty()
        self._refresh_rule_view()

    def _on_affix_move_left(self) -> None:
        """Move selected affix left."""
        if not self._selected_affix or not self._selected_word:
            return

        index = self._selected_word.affixes.index(self._selected_affix)
        if index > 0:
            self._selected_word.affixes[index], self._selected_word.affixes[index - 1] = \
                self._selected_word.affixes[index - 1], self._selected_word.affixes[index]
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_affix_move_right(self) -> None:
        """Move selected affix right."""
        if not self._selected_affix or not self._selected_word:
            return

        index = self._selected_word.affixes.index(self._selected_affix)
        if index < len(self._selected_word.affixes) - 1:
            self._selected_word.affixes[index], self._selected_word.affixes[index + 1] = \
                self._selected_word.affixes[index + 1], self._selected_word.affixes[index]
            self._mark_dirty()
            self._refresh_rule_view()

    def _on_affix_delete(self) -> None:
        """Delete selected affix."""
        if not self._selected_affix or not self._selected_word:
            return

        index = self._selected_word.affixes.index(self._selected_affix)
        self._selected_word.affixes.pop(index)
        self._mark_dirty()
        self._refresh_rule_view()

    # Rule menu handlers
    def _on_rule_duplicate(self) -> None:
        """Duplicate selected rule."""
        if self._generator:
            self._generator.duplicate_rule(self._current_rule_index)
            self._populate_rule_list()
            self._mark_dirty()

    def _on_rule_insert_before(self) -> None:
        """Insert new rule before selected."""
        if not self._generator:
            return

        from RAutils import FLExTransRule
        from RAutils import Source, Target

        new_rule = FLExTransRule(
            name=f"Rule {len(self._generator.flex_trans_rules) + 1}",
            source=Source(),
            target=Target()
        )
        self._generator.flex_trans_rules.insert(self._current_rule_index, new_rule)
        self._populate_rule_list()
        self._mark_dirty()

    def _on_rule_insert_after(self) -> None:
        """Insert new rule after selected."""
        if not self._generator:
            return

        from RAutils import FLExTransRule
        from RAutils import Source, Target

        new_rule = FLExTransRule(
            name=f"Rule {len(self._generator.flex_trans_rules) + 1}",
            source=Source(),
            target=Target()
        )
        self._generator.flex_trans_rules.insert(self._current_rule_index + 1, new_rule)
        self._populate_rule_list()
        self._mark_dirty()

    def _on_rule_move_up(self) -> None:
        """Move selected rule up."""
        if not self._generator or self._current_rule_index <= 0:
            return

        rules = self._generator.flex_trans_rules
        rules[self._current_rule_index], rules[self._current_rule_index - 1] = \
            rules[self._current_rule_index - 1], rules[self._current_rule_index]
        self._current_rule_index -= 1
        self._populate_rule_list()
        self.rule_list.setCurrentRow(self._current_rule_index)
        self._mark_dirty()

    def _on_rule_move_down(self) -> None:
        """Move selected rule down."""
        if not self._generator or self._current_rule_index >= len(self._generator.flex_trans_rules) - 1:
            return

        rules = self._generator.flex_trans_rules
        rules[self._current_rule_index], rules[self._current_rule_index + 1] = \
            rules[self._current_rule_index + 1], rules[self._current_rule_index]
        self._current_rule_index += 1
        self._populate_rule_list()
        self.rule_list.setCurrentRow(self._current_rule_index)
        self._mark_dirty()

    def _on_rule_delete(self) -> None:
        """Delete selected rule."""
        if not self._generator or self._current_rule_index < 0:
            return

        if len(self._generator.flex_trans_rules) == 1:
            QMessageBox.warning(self, _translate("RuleAssistantLib", "Error"), _translate("RuleAssistantLib", "Cannot delete the last rule"))
            return

        self._generator.flex_trans_rules.pop(self._current_rule_index)
        self._populate_rule_list()
        if self._current_rule_index >= len(self._generator.flex_trans_rules):
            self._current_rule_index = len(self._generator.flex_trans_rules) - 1
        if self._current_rule_index >= 0:
            self.rule_list.setCurrentRow(self._current_rule_index)
        self._mark_dirty()

    # Helper methods
    def _find_phrase_containing_word(self, rule, word) -> Optional["Phrase"]:
        """Find which phrase contains the given word.

        Args:
            rule: The current FLExTransRule
            word: The Word to find

        Returns:
            The Phrase containing the word, or None
        """
        if word in rule.source.words:
            return rule.source
        if word in rule.target.words:
            return rule.target
        return None

    def _find_and_remove_feature(self, rule, feature) -> None:
        """Find and remove a feature from a word or affix.

        Args:
            rule: The current FLExTransRule
            feature: The Feature to remove
        """
        for word in rule.source.words + rule.target.words:
            if feature in word.features:
                word.features.remove(feature)
                return
            for affix in word.affixes:
                if feature in affix.features:
                    affix.features.remove(feature)
                    return

    def _find_and_clear_category(self, rule, category) -> None:
        """Find and clear a category from its parent word.

        Args:
            rule: The current FLExTransRule
            category: The Category to clear
        """
        for word in rule.source.words + rule.target.words:
            # Compare by name since category objects may not be the same instance
            if word.category_constituent and word.category_constituent.name == category.name:
                word.word_category = ""
                from RAutils import Category
                word.category_constituent = Category(name="")
                return

    def get_result(self) -> WindowResult:
        """Get the result from the window.

        Returns:
            WindowResult tuple with (saved, rule_index, launch_lrt)
        """
        return self._result

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        _logger.info("closeEvent() called")
        try:
            if self._dirty:
                reply = QMessageBox.question(
                    self, _translate("RuleAssistantLib", "Changes may have been made."),
                    _translate("RuleAssistantLib", "Do you want to save any changes?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._on_save()

            self._save_window_state()
            event.accept()
            self.finished.emit()
            _logger.info("closeEvent() completed successfully")
        except Exception as e:
            import traceback
            _logger.error(f"Exception in closeEvent: {e}")
            _logger.error(traceback.format_exc())
            event.accept()  # Accept anyway to allow window to close
