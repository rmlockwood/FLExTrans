#
#   RuleAssistantMainWindow.py
#
#   Matthew Lee, Ron Lockwood - original Java version by Andy Black
#   SIL International
#   September 2023
#
#   Version 3.16.19 - 6/19/26 - Ron Lockwood
#    Affix context menu: move Insert feature below the insert-new prefix/suffix block, matching the word menu's layout.
#
#   Version 3.16.18 - 6/19/26 - Ron Lockwood
#    Fix Edit unmarked: look up the feature's real values from the full feature list, not the chooser list whose single-value in-use entry shadowed it.
#
#   Version 3.16.17 - 6/19/26 - Ron Lockwood
#    Feature chooser shows a space after the colon (e.g. "gender: pl"); strip spaces from the value before storing so the XML stays unspaced.
#
#   Version 3.16.16 - 6/19/26 - Ron Lockwood
#    Features-in-use: stop deduping by name so the single-value in-use entries (e.g. gender:α) show at the top of the feature chooser.
#
#   Version 3.16.15 - 6/18/26 - Ron Lockwood
#    Hoist all the scattered inline imports (RAutils names, deepcopy) up to the top-of-file import block.
#
#   Version 3.16.14 - 6/18/26 - Ron Lockwood
#    Share one helper for match/value assignment across edit/insert-feature handlers (word and affix insert now Greek-aware too).
#
#   Version 3.16.13 - 6/18/26 - Ron Lockwood
#    Edit feature: put a Greek agreement variable on the match attribute (not value) when the chosen value is Greek.
#
#   Version 3.16.12 - 6/17/26 - Ron Lockwood
#    Add a horizontal splitter between the rule information pane and the example data web view; save/restore its position.
#
#   Version 3.16.11 - 6/17/26 - Ron Lockwood
#    Save/restore the two splitter positions; stop marking a rule dirty while loading it (no false save prompt).
#
#   Version 3.16.10 - 6/17/26 - Ron Lockwood
#    Default the window size to the .ui design geometry when none is saved (no hard-coded default size).
#
#   Version 3.16.9 - 6/17/26 - Ron Lockwood
#    Help button jumps to the Rule Assistant section (#sRuleAssist); widen message-box title padding to 180.
#
#   Version 3.16.8 - 6/17/26 - Ron Lockwood
#    Edit unmarked excludes Greek agreement variables and warns when no real feature values exist.
#
#   Version 3.16.7 - 6/17/26 - Ron Lockwood
#    Help button opens UserDoc; Edit unmarked picks from the feature's values; message boxes widened to show their titles.
#
#   Version 3.16.6 - 6/17/26 - Ron Lockwood
#    Fix type-checker errors: type selected constituents to their subclasses, guard Optional accesses, match closeEvent signature.
#
#   Version 3.16.5 - 6/16/26 - Ron Lockwood
#    Locate features/affixes/words by object identity, not dataclass value-equality, so edits act on the clicked item.
#
#   Version 3.16.4 - 6/16/26 - Ron Lockwood
#    Apply coding conventions; camelCase naming.
#
#   Version 3.16.3 - 6/15/26 - Ron Lockwood
#    Get the LRT button working.
#
#   Version 3.16.2 - 6/15/26 - Ron Lockwood
#    Fix logic for which feature to add to the list. Made same as Java version.
#
#   Version 3.16.1 - 6/15/26 - Ron Lockwood
#    Remove logging code.
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Refactored: widgets/layout now live in RuleAssistantWindow.ui (compiled to
#    RuleAssistantWindow.py as Ui_RuleAssistantWindow). This controller holds the
#    behavior and ties the generated UI to the model.
#
#  Controller for the FLExTrans Rule Assistant main window.

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

import os
from typing import Optional, NamedTuple, cast
from pathlib import Path
from copy import deepcopy

from PyQt6.QtWidgets import (QMainWindow,  QListWidgetItem, QMenu, QMessageBox, QInputDialog, QDialog, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl, QPoint, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QKeySequence, QShortcut, QAction, QIcon, QCloseEvent, QDesktopServices

import FTPaths

_translate = QCoreApplication.translate

from RAutils import (
    FLExTransRuleGenerator, PhraseType, PermutationsValue, Word, Feature, Category, Affix, AffixType, Phrase, FLExData, XMLBackEndProvider, XMLFLExDataBackEndProvider,
    ConstituentFinder, ValidityChecker, WebPageProducer, WebPageInteractor, ApplicationPreferences,
    HeadValue, OverwriteRulesValue, FLExFeature, FLExFeatureValue, GREEK_VARIABLES,
)
from DisjointFeaturesEditorDlg import DisjointFeaturesEditorDialog
from ListChooserDialog import ListChooserDialog

# Generated from RuleAssistantWindow.ui by pyuic (do not hand-edit that file).
# Lives in Dev/Lib/Windows, which FlexTools puts on sys.path at runtime; the type checker can't see it.
from RuleAssistantWindow import Ui_RuleAssistantWindow # type: ignore

class WindowResult(NamedTuple):
    """Result returned from main window."""

    saved: bool
    ruleIndex: Optional[int]
    launchLrt: bool

def showMessageBox(parent, icon, title: str, text: str, buttons=QMessageBox.StandardButton.Ok, defaultButton=QMessageBox.StandardButton.NoButton):
    """Show a message box that is guaranteed wide enough to display its (sometimes long) window title.

    Qt sizes a message box to its message text, so a short message paired with a long window title leaves the title clipped in the
    title bar. We add a horizontal spacer to the box's grid layout, sized to the title text plus window-chrome padding, which forces
    a minimum width without shrinking a box that is already wider. Returns the StandardButton the user clicked.
    """

    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(buttons)

    if defaultButton != QMessageBox.StandardButton.NoButton:

        box.setDefaultButton(defaultButton)

    # Pad past the title text to leave room for the window icon, the min/max/close buttons, and frame margins in the title bar.
    requiredWidth = box.fontMetrics().horizontalAdvance(title) + 180
    grid = box.layout()

    if isinstance(grid, QGridLayout):

        spacer = QSpacerItem(requiredWidth, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        grid.addItem(spacer, grid.rowCount(), 0, 1, grid.columnCount())

    box.exec()
    return box.standardButton(box.clickedButton())

class RuleAssistantWindow(QMainWindow):
    """Main window for the Rule Assistant application.

    Displays rules in a tree format, manages editing and generation.
    """

    # Signal emitted when window finishes (for FlexTools integration)
    finished = pyqtSignal()

    def __init__(self, ruleFile: str, flexDataFile: str, testDataFile: str, cameFromLrt: bool = False, uiLangCode: str = "en", parent=None):
        """Initialize the main window.

        Args:
            ruleFile: Path to rule XML file
            flexDataFile: Path to FLEx metadata XML file
            testDataFile: Path to test data HTML file
            cameFromLrt: Whether launched from Live Rule Tester
            uiLangCode: UI language code
            parent: Parent widget
        """
        super().__init__(parent)

        self.ruleFile = ruleFile
        self.flexDataFile = flexDataFile
        self.testDataFile = testDataFile
        self.cameFromLrt = cameFromLrt
        self.uiLangCode = uiLangCode

        # Data and state
        self._generator: Optional[FLExTransRuleGenerator] = None
        self._flexData: Optional[FLExData] = None
        self._currentRuleIndex = 0
        self._dirty = False
        # True while we programmatically populate editor widgets, so their change signals don't mark the rule dirty.
        self._updating = False
        self._result = WindowResult(saved=False, ruleIndex=None, launchLrt=False)

        # Services
        self._producer = WebPageProducer()
        self._finder = ConstituentFinder()
        self._preferences = ApplicationPreferences()

        # Selected constituents for context menu operations
        self._selectedWord: Optional[Word] = None
        self._selectedCategory: Optional[Category] = None
        self._selectedFeature: Optional[Feature] = None
        self._selectedAffix: Optional[Affix] = None

        # Setup UI from the compiled .ui form
        self.ui = Ui_RuleAssistantWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self._aliasWidgets()
        self._createWebViews()
        self._populatePermutationsCombo()
        self._connectSignals()

        if self.cameFromLrt:

            self.testLrtButton.setEnabled(False)

        self._createContextMenus()
        self._setupKeyboardShortcuts()
        self._setupWebview()
        self._loadData()
        self._restoreWindowState()

        self.setWindowTitle(_translate("RuleAssistantWindow", "FLExTrans Rule Assistant"))

    def _aliasWidgets(self) -> None:
        """Expose the widgets created by the .ui under the names the rest of the
        controller uses."""

        # Alias each generated widget to a camelCase attribute used elsewhere in the controller.
        self.ruleList = self.ui.rule_list
        self.overwriteCheckbox = self.ui.overwrite_checkbox
        self.disjointButton = self.ui.disjoint_button
        self.ruleNameField = self.ui.rule_name_field
        self.ruleDescriptionField = self.ui.rule_description_field
        self.permutationsCombo = self.ui.permutations_combo
        self.testLrtButton = self.ui.test_lrt_button
        self.saveButton = self.ui.save_button
        self.saveCreateButton = self.ui.save_create_button
        self.saveAllButton = self.ui.save_all_button
        self.helpButton = self.ui.help_button

        # Splitter proportions (runtime tweak, not expressible in the .ui).
        self.ui.main_splitter.setSizes([200, 460])
        self.ui.v_splitter.setSizes([250, 750])
        self.ui.h_splitter.setSizes([400, 300])

    def _createWebViews(self) -> None:
        """Create the QWebEngineViews in code (kept out of the .ui to preserve the
        lazy initialization) and drop them into their placeholder layouts."""

        self.testDataView = QWebEngineView()
        self.ui.testDataLayout.addWidget(self.testDataView)
        self.treeView = QWebEngineView()
        self.ui.treeLayout.addWidget(self.treeView)

    def _populatePermutationsCombo(self) -> None:
        """Fill the permutations combo. A stable key is stored as item data so the
        displayed text can be translated without affecting the logic that reads it."""

        self.permutationsCombo.addItem(_translate("RuleAssistantWindow", "No"), "no")
        self.permutationsCombo.addItem(_translate("RuleAssistantWindow", "Including head-only rule"), "with head")
        self.permutationsCombo.addItem(_translate("RuleAssistantWindow", "Omitting head-only rule"), "not head")

    def _connectSignals(self) -> None:
        """Wire the .ui widgets to the controller's handlers."""

        self.ruleList.itemSelectionChanged.connect(self._onRuleSelected)
        self.ruleList.customContextMenuRequested.connect(self._onRuleListContextMenu)
        self.overwriteCheckbox.toggled.connect(self._onOverwriteToggled)
        self.disjointButton.clicked.connect(self._onDisjointFeatures)
        self.ruleNameField.textChanged.connect(self._onRuleNameChanged)
        self.ruleDescriptionField.textChanged.connect(self._onRuleDescriptionChanged)
        self.permutationsCombo.currentIndexChanged.connect(self._onPermutationsChanged)
        self.testLrtButton.clicked.connect(self._onTestInLrt)
        self.saveButton.clicked.connect(self._onSave)
        self.saveCreateButton.clicked.connect(self._onSaveCreate)
        self.saveAllButton.clicked.connect(self._onSaveCreateAll)
        self.helpButton.clicked.connect(self._onHelp)

    def _setupWebview(self) -> None:
        """Setup QWebEngineView with the QWebChannel bridge."""

        # Disable context menu on webview
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # Setup QWebChannel for full interactivity.
        self._channel = QWebChannel(self.treeView)
        self._interactor = WebPageInteractor(self)
        self._channel.registerObject("ftRuleGenApp", self._interactor)

        # page() is Optional; it is always present here, but guard to satisfy the type checker and be safe.
        treePage = self.treeView.page()

        if treePage is not None:

            treePage.setWebChannel(self._channel)

    @staticmethod
    def _addAction(menu: QMenu, text: str, slot) -> QAction:
        """Add a menu action and return it (typed; QMenu.addAction never returns None here)."""

        action = menu.addAction(text, slot)
        assert action is not None

        return action

    def _createContextMenus(self) -> None:
        """Create all context menus."""

        # Word context menu
        self._wordMenu = QMenu()
        self._wordMenu.addAction(_translate("RuleAssistantWindow", "Duplicate"), self._onWordDuplicate)
        self._wordMenu.addSeparator()
        self._wordMenu.addAction(_translate("RuleAssistantWindow", "Change number"), self._onWordChangeNumber)
        self._cmWordMarkAsHead = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Mark as head"), self._onWordMarkAsHead)
        self._cmWordRemoveHead = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Remove head marking"), self._onWordRemoveHead)
        self._wordMenu.addSeparator()
        self._wordMenu.addAction(_translate("RuleAssistantWindow", "Insert new before"), self._onWordInsertBefore)
        self._wordMenu.addAction(_translate("RuleAssistantWindow", "Insert new after"), self._onWordInsertAfter)
        self._wordMenu.addSeparator()
        self._cmWordInsertPrefix = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Insert prefix"), self._onWordInsertPrefix)
        self._cmWordInsertSuffix = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Insert suffix"), self._onWordInsertSuffix)
        self._cmWordInsertCategory = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Insert category"), self._onWordInsertCategory)
        self._cmWordInsertFeature = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Insert feature"), self._onWordInsertFeature)
        self._wordMenu.addSeparator()
        self._cmWordMoveLeft = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Move left"), self._onWordMoveLeft)
        self._cmWordMoveRight = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Move right"), self._onWordMoveRight)
        self._wordMenu.addSeparator()
        self._cmWordDelete = self._addAction(self._wordMenu, _translate("RuleAssistantWindow", "Delete"), self._onWordDelete)

        # Category context menu
        self._categoryMenu = QMenu()
        self._categoryMenu.addAction(_translate("RuleAssistantWindow", "Edit"), self._onCategoryEdit)
        self._categoryMenu.addSeparator()
        self._categoryMenu.addAction(_translate("RuleAssistantWindow", "Delete"), self._onCategoryDelete)

        # Feature context menu
        self._featureMenu = QMenu()
        self._featureMenu.addAction(_translate("RuleAssistantWindow", "Edit"), self._onFeatureEdit)
        self._featureMenu.addAction(_translate("RuleAssistantWindow", "Edit unmarked"), self._onFeatureEditUnmarked)
        self._cmFeatureEditRanking = self._addAction(self._featureMenu, _translate("RuleAssistantWindow", "Edit ranking"), self._onFeatureEditRanking)
        self._featureMenu.addSeparator()
        self._featureMenu.addAction(_translate("RuleAssistantWindow", "Delete"), self._onFeatureDelete)
        self._cmFeatureDeleteUnmarked = self._addAction(self._featureMenu, _translate("RuleAssistantWindow", "Delete unmarked"), self._onFeatureDeleteUnmarked)
        self._cmFeatureDeleteRanking = self._addAction(self._featureMenu, _translate("RuleAssistantWindow", "Delete ranking"), self._onFeatureDeleteRanking)

        # Affix context menu
        self._affixMenu = QMenu()
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Duplicate"), self._onAffixDuplicate)
        self._affixMenu.addSeparator()
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Toggle affix type"), self._onAffixToggleType)
        self._affixMenu.addSeparator()
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Insert new prefix before"), self._onAffixInsertPrefixBefore)
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Insert new prefix after"), self._onAffixInsertPrefixAfter)
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Insert new suffix before"), self._onAffixInsertSuffixBefore)
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Insert new suffix after"), self._onAffixInsertSuffixAfter)
        self._affixMenu.addSeparator()
        # Insert feature sits below the insert-new block, matching the position of "Insert feature" in the word context menu.
        self._cmAffixInsertFeature = self._addAction(self._affixMenu, _translate("RuleAssistantWindow", "Insert feature"), self._onAffixInsertFeature)
        self._affixMenu.addSeparator()
        self._cmAffixMoveLeft = self._addAction(self._affixMenu, _translate("RuleAssistantWindow", "Move left"), self._onAffixMoveLeft)
        self._cmAffixMoveRight = self._addAction(self._affixMenu, _translate("RuleAssistantWindow", "Move right"), self._onAffixMoveRight)
        self._affixMenu.addSeparator()
        self._affixMenu.addAction(_translate("RuleAssistantWindow", "Delete"), self._onAffixDelete)

        # Rule list context menu
        self._ruleMenu = QMenu()
        self._ruleMenu.addAction(_translate("RuleAssistantWindow", "Duplicate"), self._onRuleDuplicate)
        self._ruleMenu.addAction(_translate("RuleAssistantWindow", "Insert new before"), self._onRuleInsertBefore)
        self._ruleMenu.addAction(_translate("RuleAssistantWindow", "Insert new after"), self._onRuleInsertAfter)
        self._ruleMenu.addSeparator()
        self._cmRuleMoveUp = self._addAction(self._ruleMenu, _translate("RuleAssistantWindow", "Move up"), self._onRuleMoveUp)
        self._cmRuleMoveDown = self._addAction(self._ruleMenu, _translate("RuleAssistantWindow", "Move down"), self._onRuleMoveDown)
        self._ruleMenu.addSeparator()
        self._ruleMenu.addAction(_translate("RuleAssistantWindow", "Delete"), self._onRuleDelete)

    def _setupKeyboardShortcuts(self) -> None:
        """Setup keyboard shortcuts."""

        QShortcut(QKeySequence("Ctrl+S"), self, self._onSave)

    def _loadData(self) -> None:
        """Load rule and FLEx data files."""

        # Load rules
        self._generator = XMLBackEndProvider.loadDataFromFile(self.ruleFile)

        # Load FLEx data (optional)
        if self.flexDataFile:

            self._flexData = XMLFLExDataBackEndProvider.loadDataFromFile(self.flexDataFile)

        # Populate rule list
        self._populateRuleList()

        # Load test data
        if self.testDataFile and Path(self.testDataFile).exists():

            self.testDataView.load(QUrl.fromLocalFile(self.testDataFile))

        self._dirty = False

    def _populateRuleList(self) -> None:
        """Populate the rule list from generator."""

        self.ruleList.clear()

        if self._generator:

            for i, rule in enumerate(self._generator.flexTransRules):

                item = QListWidgetItem(rule.name or f"Rule {i+1}")
                self.ruleList.addItem(item)

        # Select first rule
        if self.ruleList.count() > 0:

            self.ruleList.setCurrentRow(0)

    def _showRule(self, index: int) -> None:
        """Show a rule in the editor.

        Args:
            index: Rule index
        """

        if not self._generator or index < 0 or index >= len(self._generator.flexTransRules):

            return

        self._currentRuleIndex = index
        rule = self._generator.flexTransRules[index]

        # Populate the editor widgets from the model. Setting these fires their change signals, so guard with _updating to keep the handlers from writing back and marking the (unchanged) rule dirty.
        self._updating = True

        try:
            self.ruleNameField.setText(rule.name)
            self.ruleDescriptionField.setPlainText(rule.description)

            permKey = {
                PermutationsValue.no: "no",
                PermutationsValue.not_head: "not head",
                PermutationsValue.with_head: "with head",
            }.get(rule.createPermutations, "with head")
            permIndex = self.permutationsCombo.findData(permKey)
            self.permutationsCombo.setCurrentIndex(permIndex if permIndex >= 0 else 0)

            # Update overwrite checkbox
            self.overwriteCheckbox.setChecked(self._generator.overwriteRules.value == "yes")

        finally:
            self._updating = False

        # Generate and show HTML
        html = self._producer.produceWebPage(rule)
        self.treeView.setHtml(html, QUrl("qrc:///"))

    def _refreshRuleView(self) -> None:
        """Refresh the current rule display after editing."""

        if self._generator and 0 <= self._currentRuleIndex < len(self._generator.flexTransRules):

            rule = self._generator.flexTransRules[self._currentRuleIndex]

            # Update list item text
            item = self.ruleList.item(self._currentRuleIndex)

            if item:

                item.setText(rule.name or f"Rule {self._currentRuleIndex + 1}")

            # Re-render HTML
            html = self._producer.produceWebPage(rule)
            self.treeView.setHtml(html, QUrl("qrc:///"))

    def _restoreWindowState(self) -> None:
        """Restore window size and position from preferences."""

        # setupUi() has already applied the design-time size from the .ui, so the current width/height IS the .ui default; use it whenever no size has been saved yet (and to repair bad saved sizes).
        defaultWidth = self.width()
        defaultHeight = self.height()

        x = self._preferences.getWindowPositionX()
        y = self._preferences.getWindowPositionY()
        w = self._preferences.getWindowWidth(defaultWidth)
        h = self._preferences.getWindowHeight(defaultHeight)
        maximized = self._preferences.getWindowMaximized()

        # Ensure window is visible on screen (not above y=0)
        if y < 0:

            y = 50

        if x < 0:

            x = 50

        if w < 400:

            w = defaultWidth

        if h < 300:

            h = defaultHeight

        self.setGeometry(x, y, w, h)

        # Restore the three splitter positions if the user has saved them; otherwise keep the defaults set in _setupWidgets.
        mainSizes = self._preferences.getMainSplitterSizes()

        if mainSizes:

            self.ui.main_splitter.setSizes(mainSizes)

        vSizes = self._preferences.getVSplitterSizes()

        if vSizes:

            self.ui.v_splitter.setSizes(vSizes)

        hSizes = self._preferences.getHSplitterSizes()

        if hSizes:

            self.ui.h_splitter.setSizes(hSizes)

        if maximized:

            self.showMaximized()
        else:
            self.show()

        # Restore selected rule
        lastRule = self._preferences.getLastSelectedRule()

        if 0 <= lastRule < self.ruleList.count():

            self.ruleList.setCurrentRow(lastRule)

    def _saveWindowState(self) -> None:
        """Save window state to preferences."""

        self._preferences.setWindowPositionX(self.x())
        self._preferences.setWindowPositionY(self.y())
        self._preferences.setWindowWidth(self.width())
        self._preferences.setWindowHeight(self.height())
        self._preferences.setWindowMaximized(self.isMaximized())
        self._preferences.setLastSelectedRule(self._currentRuleIndex)
        self._preferences.setMainSplitterSizes(self.ui.main_splitter.sizes())
        self._preferences.setVSplitterSizes(self.ui.v_splitter.sizes())
        self._preferences.setHSplitterSizes(self.ui.h_splitter.sizes())
        self._preferences.sync()

    def processItemClickedOn(self, item: str, x: int, y: int) -> None:
        """Process a click on a tree element.

        Args:
            item: Element identifier (e.g., "w.5")
            x: Screen X coordinate
            y: Screen Y coordinate
        """

        if not self._generator:

            return

        rule = self._generator.flexTransRules[self._currentRuleIndex]
        typeCode = item[0]

        try:
            identifier = int(item[2:])

        except (ValueError, IndexError):

            return

        # Find the constituent
        constituent = self._finder.findConstituent(rule, identifier)

        if not constituent:

            return

        pos = QPoint(x, y)

        # Show appropriate context menu based on type
        # The typeCode tells us the concrete constituent subclass, so cast accordingly (the finder returns the base type).
        if typeCode == "w":

            self._selectedWord = cast(Word, constituent)
            self._enableDisableWordMenuItems(constituent)
            self._wordMenu.exec(pos)

        elif typeCode == "c":

            self._selectedCategory = cast(Category, constituent)
            self._categoryMenu.exec(pos)

        elif typeCode == "f":

            self._selectedFeature = cast(Feature, constituent)
            self._enableDisableFeatureMenuItems(constituent)
            self._featureMenu.exec(pos)

        elif typeCode == "a":

            self._selectedAffix = cast(Affix, constituent)
            self._enableDisableAffixMenuItems(constituent)
            self._affixMenu.exec(pos)

        elif typeCode == "p":

            # Phrase click does nothing
            pass

    # ------------------------------------------------------------------
    # Context-menu item enable/disable (mirrors the Java MainController so operations that don't apply to the clicked-on item are greyed out).
    # ------------------------------------------------------------------
    def _flexCategoryHasValidFeatures(self, word, phraseType) -> bool:
        """True if the word's (or corresponding source word's) category exists in
        the FLEx data for this phrase and that category has valid features."""

        if not self._flexData:

            return False

        cat = word.getCategoryOfWordOrCorrespondingSourceWord()

        if not cat or not cat.name:

            return False

        for flexCat in self._flexData.getFlexCategoriesForPhrase(phraseType):

            if flexCat.abbreviation == cat.name:

                return len(flexCat.validFeatures) > 0

        return False

    def _enableDisableWordMenuItems(self, word) -> None:

        phrase = word.parent

        if phrase is None:

            return

        phraseType = phrase.phraseType
        index = self._indexByIdentity(phrase.words, word)

        self._cmWordMoveLeft.setEnabled(index != 0)
        self._cmWordMoveRight.setEnabled(index != len(phrase.words) - 1)
        self._cmWordDelete.setEnabled(not (index == 0 and len(phrase.words) == 1))

        # Can only insert a category if the word doesn't already have one.
        cat = word.getCategoryOfWordOrCorrespondingSourceWord()
        self._cmWordInsertCategory.setEnabled(not (cat and cat.name))

        if phraseType == PhraseType.source:

            self._cmWordMarkAsHead.setEnabled(False)
            self._cmWordRemoveHead.setEnabled(False)

        elif word.head == HeadValue.yes:

            self._cmWordMarkAsHead.setEnabled(False)
            self._cmWordRemoveHead.setEnabled(True)
        else:
            self._cmWordMarkAsHead.setEnabled(True)
            self._cmWordRemoveHead.setEnabled(False)

        # Affixes can only be inserted on a word that has none yet.
        noAffixes = len(word.affixes) == 0
        self._cmWordInsertPrefix.setEnabled(noAffixes)
        self._cmWordInsertSuffix.setEnabled(noAffixes)

        self._cmWordInsertFeature.setEnabled(self._flexCategoryHasValidFeatures(word, phraseType))

    def _enableDisableAffixMenuItems(self, affix) -> None:

        word = affix.parent

        if word is None:

            return

        index = self._indexByIdentity(word.affixes, affix)
        self._cmAffixMoveLeft.setEnabled(index != 0)
        self._cmAffixMoveRight.setEnabled(index != len(word.affixes) - 1)

        phrase = word.parent
        phraseType = phrase.phraseType if phrase is not None else None
        self._cmAffixInsertFeature.setEnabled(self._flexCategoryHasValidFeatures(word, phraseType))

    def _enableDisableFeatureMenuItems(self, feature) -> None:

        # Find the word that owns this feature (directly, or via an affix).
        owner = feature.parent
        thisWord = None

        if isinstance(owner, Word):

            thisWord = owner

        elif isinstance(owner, Affix) and isinstance(owner.parent, Word):

            thisWord = owner.parent

        phrase = thisWord.parent if thisWord is not None else None

        if isinstance(phrase, Phrase) and phrase.phraseType == PhraseType.target and thisWord is not None:

            # Ranking only makes sense when the word has more than one feature (counting features on the word and on all its affixes).
            featureCount = len(thisWord.features) + sum(len(a.features) for a in thisWord.affixes)
            self._cmFeatureEditRanking.setEnabled(featureCount > 1)
        else:
            self._cmFeatureEditRanking.setEnabled(False)

        self._cmFeatureDeleteUnmarked.setEnabled(len(feature.unmarked) > 0)
        self._cmFeatureDeleteRanking.setEnabled(feature.ranking > 0)

    def _enableDisableRuleMenuItems(self) -> None:

        self._cmRuleMoveUp.setEnabled(self._currentRuleIndex != 0)
        last = len(self._generator.flexTransRules) - 1 if self._generator else 0
        self._cmRuleMoveDown.setEnabled(self._currentRuleIndex != last)

    def _markDirty(self) -> None:
        """Mark the document as changed."""

        if not self._dirty:

            self._dirty = True

            # Update title with asterisk
            currentTitle = self.windowTitle()

            if not currentTitle.endswith("*"):

                self.setWindowTitle(currentTitle + "*")

    # Signal handlers
    def _onRuleSelected(self) -> None:
        """Handle rule selection in list."""

        row = self.ruleList.currentRow()

        if row >= 0:

            self._showRule(row)

    def _onRuleNameChanged(self) -> None:
        """Handle rule name text change."""

        if self._updating:

            return

        if self._generator and 0 <= self._currentRuleIndex < len(self._generator.flexTransRules):

            self._generator.flexTransRules[self._currentRuleIndex].name = self.ruleNameField.text()

            # Update list
            item = self.ruleList.item(self._currentRuleIndex)

            if item:

                item.setText(self.ruleNameField.text())

            self._markDirty()

    def _onRuleDescriptionChanged(self) -> None:
        """Handle rule description text change."""

        if self._updating:

            return

        if self._generator and 0 <= self._currentRuleIndex < len(self._generator.flexTransRules):

            self._generator.flexTransRules[self._currentRuleIndex].description = (self.ruleDescriptionField.toPlainText())
            self._markDirty()

    def _onPermutationsChanged(self) -> None:
        """Handle permutations combo change."""

        if self._updating:

            return

        if self._generator and 0 <= self._currentRuleIndex < len(self._generator.flexTransRules):

            keyToEnum = {
                "no": PermutationsValue.no,
                "with head": PermutationsValue.with_head,
                "not head": PermutationsValue.not_head,
            }
            self._generator.flexTransRules[self._currentRuleIndex].createPermutations = (keyToEnum.get(self.permutationsCombo.currentData(), PermutationsValue.with_head))
            self._markDirty()

    def _onOverwriteToggled(self) -> None:
        """Handle overwrite checkbox toggle."""

        if self._updating:

            return

        if self._generator:

            self._generator.overwriteRules = (OverwriteRulesValue.yes if self.overwriteCheckbox.isChecked() else OverwriteRulesValue.no)
            self._markDirty()

    def _onSave(self) -> None:
        """Handle Save button."""

        if self._generator:

            XMLBackEndProvider.saveDataToFile(self._generator, self.ruleFile)
            self._dirty = False

            # Update title
            currentTitle = self.windowTitle()

            if currentTitle.endswith("*"):

                self.setWindowTitle(currentTitle[:-1])

    def _onSaveCreate(self) -> None:
        """Handle Save/Create button."""

        if not self._generator:

            return

        rule = self._generator.flexTransRules[self._currentRuleIndex]
        isValid, errorMsg = ValidityChecker.validateRule(rule)

        if not isValid:

            showMessageBox(self, QMessageBox.Icon.Critical, _translate("RuleAssistantWindow", "Problem with rule"), errorMsg)

            return

        self._onSave()
        self._result = WindowResult(saved=True, ruleIndex=self._currentRuleIndex, launchLrt=False)
        self.close()

    def _onSaveCreateAll(self) -> None:
        """Handle Save/Create All button."""

        if not self._generator:

            return

        for i, rule in enumerate(self._generator.flexTransRules):

            isValid, errorMsg = ValidityChecker.validateRule(rule)

            if not isValid:

                showMessageBox(self, QMessageBox.Icon.Critical, _translate("RuleAssistantWindow", "Problem with rule"), errorMsg)

                return

        self._onSave()
        self._result = WindowResult(saved=True, ruleIndex=None, launchLrt=False)
        self.close()

    def _onTestInLrt(self) -> None:
        """Handle Test In LRT button: ask which save option to use, then save and
        close, flagging that the Live Rule Tester should be launched afterward
        (mirrors the Java MainController.handleTestInLRT)."""

        if not self._generator:

            return

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(_translate("RuleAssistantWindow", "Test in the Live Rule Tester"))
        box.setText(_translate("RuleAssistantWindow", "Choose which save option you want."))
        box.setInformativeText(_translate("RuleAssistantWindow", "Choose your option."))

        saveBtn = box.addButton(_translate("RuleAssistantWindow", "Save"), QMessageBox.ButtonRole.AcceptRole)
        saveCreateBtn = box.addButton(_translate("RuleAssistantWindow", "Save & Write"), QMessageBox.ButtonRole.AcceptRole)
        saveCreateAllBtn = box.addButton(_translate("RuleAssistantWindow", "Save & Write All"), QMessageBox.ButtonRole.AcceptRole)
        box.addButton(_translate("RuleAssistantWindow", "Cancel"), QMessageBox.ButtonRole.RejectRole)

        box.exec()
        clicked = box.clickedButton()

        if clicked is saveCreateBtn:

            # Validate and create just the current rule, then launch LRT.
            rule = self._generator.flexTransRules[self._currentRuleIndex]
            isValid, errorMsg = ValidityChecker.validateRule(rule)

            if not isValid:

                showMessageBox(self, QMessageBox.Icon.Critical, _translate("RuleAssistantWindow", "Problem with rule"), errorMsg)

                return

            self._onSave()
            self._result = WindowResult(saved=True, ruleIndex=self._currentRuleIndex, launchLrt=True)
            self.close()

        elif clicked is saveCreateAllBtn:

            # Validate and create all rules, then launch LRT.
            for rule in self._generator.flexTransRules:

                isValid, errorMsg = ValidityChecker.validateRule(rule)

                if not isValid:

                    showMessageBox(self, QMessageBox.Icon.Critical, _translate("RuleAssistantWindow", "Problem with rule"), errorMsg)

                    return

            self._onSave()
            self._result = WindowResult(saved=True, ruleIndex=None, launchLrt=True)
            self.close()

        elif clicked is saveBtn:

            # Save the rule file only (no rule generation), then launch LRT.
            for rule in self._generator.flexTransRules:

                isValid, errorMsg = ValidityChecker.validateRule(rule)

                if not isValid:

                    showMessageBox(self, QMessageBox.Icon.Critical, _translate("RuleAssistantWindow", "Problem with rule"), errorMsg)

                    return

            self._onSave()
            self._result = WindowResult(saved=False, ruleIndex=None, launchLrt=True)
            self.close()

        # Cancel: do nothing.

    def _onHelp(self) -> None:
        """Open the FLExTrans user documentation at the Rule Assistant section."""

        helpFile = os.path.join(FTPaths.HELP_DIR, "UserDoc.htm")

        # Guard so a missing file doesn't crash the tool.
        if not os.path.exists(helpFile):

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Help"), _translate("RuleAssistantWindow", "Help file not found: {file}").format(file=helpFile))

            return

        # Jump to the Rule Assistant section. os.startfile can't carry a #fragment, so build a file URL with the anchor and let Qt open it in the default browser.
        url = QUrl.fromLocalFile(helpFile)
        url.setFragment("sRuleAssist")
        QDesktopServices.openUrl(url)

    def _onDisjointFeatures(self) -> None:
        """Handle Disjoint Features button."""

        if not self._generator or not self._flexData:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Error"), _translate("RuleAssistantWindow", "No data loaded"))

            return

        dialog = DisjointFeaturesEditorDialog(self._generator, self._flexData, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:

            self._markDirty()
            self._refreshRuleView()

    def _onRuleListContextMenu(self, pos: QPoint) -> None:
        """Handle rule list context menu."""

        item = self.ruleList.itemAt(pos)

        if item:

            self._enableDisableRuleMenuItems()
            self._ruleMenu.exec(self.ruleList.mapToGlobal(pos))

    # Word menu handlers
    def _onWordDuplicate(self) -> None:
        """Duplicate selected word."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if not phrase:

            return

        index = self._indexByIdentity(phrase.words, self._selectedWord)
        newWord = deepcopy(self._selectedWord)
        phrase.words.insert(index + 1, newWord)
        self._markDirty()
        self._refreshRuleView()

    def _onWordChangeNumber(self) -> None:
        """Change selected word's number."""

        if not self._selectedWord:

            return

        newId, ok = QInputDialog.getText(self, _translate("RuleAssistantWindow", "Word Number"), _translate("RuleAssistantWindow", "Choose word number:"), text=self._selectedWord.wordId)

        if ok and newId:

            oldId = self._selectedWord.wordId

            # Update in both source and target phrases
            if self._generator:

                rule = self._generator.flexTransRules[self._currentRuleIndex]

                # Find and update source
                for word in rule.source.words:

                    if word.wordId == oldId:

                        word.wordId = newId

                # Find and update target
                for word in rule.target.words:

                    if word.wordId == oldId:

                        word.wordId = newId

            self._markDirty()
            self._refreshRuleView()

    def _onWordMarkAsHead(self) -> None:
        """Mark selected word as head."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if phrase:

            phrase.markWordAsHead(self._selectedWord)
            self._markDirty()
            self._refreshRuleView()

    def _onWordRemoveHead(self) -> None:
        """Remove head marking from selected word."""

        if not self._selectedWord:

            return

        self._selectedWord.head = HeadValue.no
        self._markDirty()
        self._refreshRuleView()

    def _onWordInsertBefore(self) -> None:
        """Insert word before selected word."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if not phrase:

            return

        index = self._indexByIdentity(phrase.words, self._selectedWord)
        phrase.insertNewWordAt(index)
        self._markDirty()
        self._refreshRuleView()

    def _onWordInsertAfter(self) -> None:
        """Insert word after selected word."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if not phrase:

            return

        index = self._indexByIdentity(phrase.words, self._selectedWord)
        phrase.insertNewWordAt(index + 1)
        self._markDirty()
        self._refreshRuleView()

    def _onWordInsertPrefix(self) -> None:
        """Insert prefix on selected word."""

        if not self._selectedWord:

            return

        newAffix = Affix(affixType=AffixType.prefix)
        self._selectedWord.affixes.append(newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _onWordInsertSuffix(self) -> None:
        """Insert suffix on selected word."""

        if not self._selectedWord:

            return

        newAffix = Affix(affixType=AffixType.suffix)
        self._selectedWord.affixes.append(newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _chooseCategory(self, categories, currentCategory):
        """Ask the user to pick a category from a list. Returns the chosen
        FLExCategory or None if cancelled."""

        items = [(c.abbreviation, c) for c in categories]
        currentIndex = 0

        if currentCategory is not None:

            for i, c in enumerate(categories):

                if c.abbreviation == currentCategory.name:

                    currentIndex = i

                    break

        return ListChooserDialog.choose(self, _translate("RuleAssistantWindow", "FLEx Category Chooser"), items, currentIndex)

    def _fullFlexFeaturesForWord(self, word):
        """Return the complete FLEx features valid for the word's category, each with all its values. This is the raw list, without the single-value "in use" quick-picks or disjoint-set synthetics that _flexFeaturesForWord prepends for the feature chooser. Use this when you need a feature's real values (e.g. the unmarked-value editor)."""

        if not self._flexData or word is None:

            return []

        phrase = word.parent

        if phrase is None:

            return []

        cat = word.getCategoryOfWordOrCorrespondingSourceWord()
        catAbbr = cat.name if cat else ""
        return self._flexData.getFeaturesInPhraseForCategory(phrase.phraseType, catAbbr)

    def _flexFeaturesForWord(self, word):
        """FLEx features to offer for a word, filtered to the word's category and
        phrase. Mirrors the Java MainController.processInsertFeature, which shows
        only the features valid for the word's category: features already in use
        first, then any applicable disjoint feature sets, then the rest of the
        category's features (rather than every feature in the project)."""

        if not self._flexData or word is None:

            return []

        phrase = word.parent

        if phrase is None:

            return []

        phraseType = phrase.phraseType
        featuresForCategory = self._fullFlexFeaturesForWord(word)
        featuresInUse = phrase.getFeaturesInUseForCategory(featuresForCategory)
        disjointFeatures = self._disjointFeaturesFor(featuresForCategory, phraseType)

        # Order matches Java (MainController.processInsertFeature): the single-value "in use" features first (a quick-pick of values already used in the phrase, e.g. gender:α), then the disjoint-set features, then the full list of the category's features.
        # No dedup here: the in-use entries are deliberately the same values that also appear in the full list below; surfacing them at the top is exactly the "easy access" behavior we want.
        return list(featuresInUse) + disjointFeatures + list(featuresForCategory)

    def _disjointFeaturesFor(self, featuresForCategory, phraseType):
        """Build a synthetic FLEx feature for each disjoint feature set whose
        sub-features are all present in this category. Mirrors the Java
        MainController.addAnyDisjointFeatures: each qualifying set becomes one
        feature named after the set, with the Greek variable values."""

        if not self._generator or not self._flexData:

            return []

        # Number of variable values comes from the phrase's FLEx data.
        if phraseType == PhraseType.source:

            maxVars = self._flexData.sourceData.maxVariables
        else:
            maxVars = self._flexData.targetData.maxVariables

        result = []

        for dfSet in self._generator.disjointFeatures:

            if dfSet.hasFlexFeatureInList(featuresForCategory):

                ff = FLExFeature(name=dfSet.name)

                for i in range(min(maxVars, len(GREEK_VARIABLES))):

                    ff.values.append(FLExFeatureValue(abbreviation=GREEK_VARIABLES[i], feature=ff))

                result.append(ff)

        return result

    def _chooseFeatureValue(self, features, currentFeature=None):
        """Ask the user to pick a feature:value pair from a list. Returns
        (FLExFeature, FLExFeatureValue) or None if cancelled."""

        items = []
        currentIndex = 0
        curLabel = currentFeature.label if currentFeature else None
        curValue = currentFeature.getMatchOrValue() if currentFeature else None

        for feature in features:

            for value in feature.values:

                if curLabel and feature.name == curLabel and value.abbreviation == curValue:

                    currentIndex = len(items)

                # Display a space after the colon (e.g. "gender: pl") for readability; the data tuple keeps the unspaced abbreviation, so what is written to the XML is unaffected.
                items.append((f"{feature.name}: {value.abbreviation}", (feature, value)))

        return ListChooserDialog.choose(self, _translate("RuleAssistantWindow", "FLEx Feature Value Chooser"), items, currentIndex)

    def _onWordInsertCategory(self) -> None:
        """Insert category on selected word."""

        if not self._selectedWord or not self._flexData:

            return

        # Get all available categories
        allCategories = []

        if self._flexData.sourceData:

            allCategories.extend(self._flexData.sourceData.categories)

        if self._flexData.targetData:

            allCategories.extend(self._flexData.targetData.categories)

        # Remove duplicates and sort
        seen = set()
        uniqueCategories = []

        for cat in allCategories:

            if cat.abbreviation not in seen:

                uniqueCategories.append(cat)
                seen.add(cat.abbreviation)

        if not uniqueCategories:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Error"), _translate("RuleAssistantWindow", "No categories available"))

            return

        # Get current category for pre-selection
        currentCategory = Category(name=self._selectedWord.wordCategory) if self._selectedWord.wordCategory else None

        chosen = self._chooseCategory(uniqueCategories, currentCategory)

        if chosen:

            self._selectedWord.wordCategory = chosen.abbreviation
            self._selectedWord.categoryConstituent = Category(name=chosen.abbreviation)
            self._markDirty()
            self._refreshRuleView()

    def _onWordInsertFeature(self) -> None:
        """Insert feature on selected word."""

        if not self._selectedWord or not self._flexData:

            return

        # Only offer features valid for the word's category (matches Java).
        allFeatures = self._flexFeaturesForWord(self._selectedWord)

        if not allFeatures:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Error"), _translate("RuleAssistantWindow", "No features available"))

            return

        result = self._chooseFeatureValue(allFeatures)

        if result:

            flexFeature, flexValue = result

            newFeature = Feature(label=flexFeature.name)

            # Assign the chosen abbreviation to the correct attribute based on whether it's a Greek variable or a concrete value.
            self._assignFeatureMatchOrValue(newFeature, flexValue.abbreviation)

            self._selectedWord.features.append(newFeature)
            self._markDirty()
            self._refreshRuleView()

    def _onWordMoveLeft(self) -> None:
        """Move selected word left."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if not phrase:

            return

        index = self._indexByIdentity(phrase.words, self._selectedWord)

        if index > 0:

            phrase.swapPositionOfWords(index, index - 1)
            self._markDirty()
            self._refreshRuleView()

    def _onWordMoveRight(self) -> None:
        """Move selected word right."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if not phrase:

            return

        index = self._indexByIdentity(phrase.words, self._selectedWord)

        if index < len(phrase.words) - 1:

            phrase.swapPositionOfWords(index, index + 1)
            self._markDirty()
            self._refreshRuleView()

    def _onWordDelete(self) -> None:
        """Delete selected word."""

        if not self._selectedWord or not self._generator:

            return

        phrase = self._findPhraseContainingWord(self._generator.flexTransRules[self._currentRuleIndex], self._selectedWord)

        if phrase:

            index = self._indexByIdentity(phrase.words, self._selectedWord)
            phrase.words.pop(index)
            self._markDirty()
            self._refreshRuleView()

    # Category menu handlers
    def _onCategoryEdit(self) -> None:
        """Edit selected category."""

        if not self._selectedCategory or not self._flexData:

            return

        # Get all available categories
        allCategories = []

        if self._flexData.sourceData:

            allCategories.extend(self._flexData.sourceData.categories)

        if self._flexData.targetData:

            allCategories.extend(self._flexData.targetData.categories)

        # Remove duplicates
        seen = set()
        uniqueCategories = []

        for cat in allCategories:

            if cat.abbreviation not in seen:

                uniqueCategories.append(cat)
                seen.add(cat.abbreviation)

        if not uniqueCategories:

            return

        currentCategory = Category(name=self._selectedCategory.name) if self._selectedCategory.name else None

        chosen = self._chooseCategory(uniqueCategories, currentCategory)

        if chosen:

            self._selectedCategory.name = chosen.abbreviation
            self._markDirty()
            self._refreshRuleView()

    def _onCategoryDelete(self) -> None:
        """Delete selected category."""

        if not self._selectedCategory or not self._generator:

            return

        rule = self._generator.flexTransRules[self._currentRuleIndex]

        # Find parent word and clear its category
        self._findAndClearCategory(rule, self._selectedCategory)
        self._markDirty()
        self._refreshRuleView()

    # Feature menu handlers
    @staticmethod
    def _assignFeatureMatchOrValue(feature, abbreviation: str) -> None:
        """Assign a chosen feature abbreviation to the correct attribute (matches Java).

        Greek agreement variables go on the match attribute (with value cleared); concrete feature values go on the value attribute (with match cleared)."""

        # Strip any surrounding spaces so the value stored (and later written to the XML) never picks up display spacing.
        abbreviation = abbreviation.strip()

        if FLExFeatureValue.isGreek(abbreviation):

            feature.match = abbreviation
            feature.value = ""
        else:
            feature.value = abbreviation
            feature.match = ""

    def _onFeatureEdit(self) -> None:
        """Edit selected feature."""

        if not self._selectedFeature or not self._flexData:

            return

        # Filter by the owning word's category (matches Java). The feature's owner is either the word directly or an affix on the word.
        owner = self._selectedFeature.parent

        if isinstance(owner, Word):

            ownerWord = owner

        elif isinstance(owner, Affix):

            ownerWord = owner.parent
        else:
            ownerWord = None

        allFeatures = self._flexFeaturesForWord(ownerWord)

        if not allFeatures:

            return

        # Pre-select current feature for dialog
        currentFeature = Feature(
            label=self._selectedFeature.label,
            value=self._selectedFeature.value
        ) if self._selectedFeature.label else None

        result = self._chooseFeatureValue(allFeatures, currentFeature)

        if result:

            flexFeature, flexValue = result
            self._selectedFeature.label = flexFeature.name

            # Assign the chosen abbreviation to the correct attribute based on whether it's a Greek variable or a concrete value.
            self._assignFeatureMatchOrValue(self._selectedFeature, flexValue.abbreviation)

            self._markDirty()
            self._refreshRuleView()

    def _onFeatureEditUnmarked(self) -> None:
        """Set the unmarked value of the selected feature by picking from the feature's FLEx values (matches Java).

        The Java version shows a list of the feature's possible values, not a free-text box, so the user can only choose
        a real value for the feature. (Clearing the unmarked value is handled separately by 'Delete unmarked'.)"""

        if not self._selectedFeature or not self._flexData:

            return

        # The feature's owner is either the word directly or an affix on the word; we filter FLEx values by that word.
        owner = self._selectedFeature.parent

        if isinstance(owner, Word):

            ownerWord = owner

        elif isinstance(owner, Affix):

            ownerWord = owner.parent
        else:
            ownerWord = None

        # Find the FLEx feature whose name matches this feature's label, so we can offer its values. Use the full feature list (not the chooser list, whose single-value "in use" entries would shadow the full feature and leave only the Greek value to offer).
        flexFeature = None

        for f in self._fullFlexFeaturesForWord(ownerWord):

            if f.name == self._selectedFeature.label:

                flexFeature = f
                break

        if not flexFeature or not flexFeature.values:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Edit unmarked"), _translate("RuleAssistantWindow", "No values available for this feature."))

            return

        # Build the value list, pre-selecting the current unmarked value if it is among them. Skip the Greek agreement variables (added to every feature for matching); an unmarked default must be a real value.
        items = []
        currentIndex = 0

        for value in flexFeature.values:

            if FLExFeatureValue.isGreek(value.abbreviation):

                continue

            if value.abbreviation == self._selectedFeature.unmarked:

                currentIndex = len(items)

            items.append((value.abbreviation, value.abbreviation))

        # Everything may have been a Greek variable, leaving no real value to choose.
        if not items:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Edit unmarked"), _translate("RuleAssistantWindow", "No feature values found."))

            return

        chosen = ListChooserDialog.choose(self, _translate("RuleAssistantWindow", "Unmarked Value Chooser"), items, currentIndex)

        if chosen is not None:

            self._selectedFeature.unmarked = chosen
            self._markDirty()
            self._refreshRuleView()

    def _onFeatureEditRanking(self) -> None:
        """Edit ranking of selected feature."""

        if not self._selectedFeature:

            return

        value, ok = QInputDialog.getInt(self, _translate("RuleAssistantWindow", "Ranking for Feature"), _translate("RuleAssistantWindow", "Choose ranking:"), self._selectedFeature.ranking, 0, 9999, 1)

        if ok:

            self._selectedFeature.ranking = value
            self._markDirty()
            self._refreshRuleView()

    def _onFeatureDelete(self) -> None:
        """Delete selected feature."""

        if not self._selectedFeature or not self._generator:

            return

        rule = self._generator.flexTransRules[self._currentRuleIndex]

        # Find parent word or affix and remove feature
        self._findAndRemoveFeature(rule, self._selectedFeature)
        self._markDirty()
        self._refreshRuleView()

    def _onFeatureDeleteUnmarked(self) -> None:
        """Delete unmarked value from selected feature."""

        if not self._selectedFeature:

            return

        self._selectedFeature.unmarked = ""
        self._markDirty()
        self._refreshRuleView()

    def _onFeatureDeleteRanking(self) -> None:
        """Delete ranking from selected feature."""

        if not self._selectedFeature:

            return

        self._selectedFeature.ranking = 0
        self._markDirty()
        self._refreshRuleView()

    # Affix menu handlers
    def _onAffixDuplicate(self) -> None:
        """Duplicate selected affix."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)
        newAffix = deepcopy(self._selectedAffix)
        self._selectedWord.affixes.insert(index + 1, newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _onAffixToggleType(self) -> None:
        """Toggle affix type (prefix <-> suffix)."""

        if not self._selectedAffix:

            return

        self._selectedAffix.affixType = (AffixType.suffix if self._selectedAffix.affixType == AffixType.prefix else AffixType.prefix)
        self._markDirty()
        self._refreshRuleView()

    def _onAffixInsertFeature(self) -> None:
        """Insert feature on selected affix."""

        if not self._selectedAffix or not self._flexData:

            return

        # Filter by the owning word's category (matches Java, which derives the word from the affix's parent).
        allFeatures = self._flexFeaturesForWord(self._selectedAffix.parent)

        if not allFeatures:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Error"), _translate("RuleAssistantWindow", "No features available"))

            return

        result = self._chooseFeatureValue(allFeatures)

        if result:

            flexFeature, flexValue = result

            newFeature = Feature(label=flexFeature.name)

            # Assign the chosen abbreviation to the correct attribute based on whether it's a Greek variable or a concrete value.
            self._assignFeatureMatchOrValue(newFeature, flexValue.abbreviation)
            
            self._selectedAffix.features.append(newFeature)
            self._markDirty()
            self._refreshRuleView()

    def _onAffixInsertPrefixBefore(self) -> None:
        """Insert prefix before selected affix."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)
        newAffix = Affix(affixType=AffixType.prefix)
        self._selectedWord.affixes.insert(index, newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _onAffixInsertPrefixAfter(self) -> None:
        """Insert prefix after selected affix."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)
        newAffix = Affix(affixType=AffixType.prefix)
        self._selectedWord.affixes.insert(index + 1, newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _onAffixInsertSuffixBefore(self) -> None:
        """Insert suffix before selected affix."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)
        newAffix = Affix(affixType=AffixType.suffix)
        self._selectedWord.affixes.insert(index, newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _onAffixInsertSuffixAfter(self) -> None:
        """Insert suffix after selected affix."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)
        newAffix = Affix(affixType=AffixType.suffix)
        self._selectedWord.affixes.insert(index + 1, newAffix)
        self._markDirty()
        self._refreshRuleView()

    def _onAffixMoveLeft(self) -> None:
        """Move selected affix left."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)

        if index > 0:

            self._selectedWord.affixes[index], self._selectedWord.affixes[index - 1] = self._selectedWord.affixes[index - 1], self._selectedWord.affixes[index]
            self._markDirty()
            self._refreshRuleView()

    def _onAffixMoveRight(self) -> None:
        """Move selected affix right."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)

        if index < len(self._selectedWord.affixes) - 1:

            self._selectedWord.affixes[index], self._selectedWord.affixes[index + 1] = self._selectedWord.affixes[index + 1], self._selectedWord.affixes[index]
            self._markDirty()
            self._refreshRuleView()

    def _onAffixDelete(self) -> None:
        """Delete selected affix."""

        if not self._selectedAffix or not self._selectedWord:

            return

        index = self._indexByIdentity(self._selectedWord.affixes, self._selectedAffix)
        self._selectedWord.affixes.pop(index)
        self._markDirty()
        self._refreshRuleView()

    # Rule menu handlers
    def _onRuleDuplicate(self) -> None:
        """Duplicate selected rule."""

        if self._generator:

            self._generator.duplicateRule(self._currentRuleIndex)
            self._populateRuleList()
            self._markDirty()

    def _onRuleInsertBefore(self) -> None:
        """Insert new rule before selected."""

        if not self._generator:

            return

        self._insertNewRuleAt(self._currentRuleIndex)

    def _onRuleInsertAfter(self) -> None:
        """Insert new rule after selected."""

        if not self._generator:

            return

        self._insertNewRuleAt(self._currentRuleIndex + 1)

    def _insertNewRuleAt(self, index: int) -> None:
        """Insert a new, editable rule (with word boxes) at the given index and
        select it so it is shown in the editor."""

        if not self._generator:

            return

        self._generator.insertNewRule(index, f"Rule {len(self._generator.flexTransRules) + 1}")
        self._populateRuleList()
        self.ruleList.setCurrentRow(index)
        self._markDirty()

    def _onRuleMoveUp(self) -> None:
        """Move selected rule up."""

        if not self._generator or self._currentRuleIndex <= 0:

            return

        rules = self._generator.flexTransRules
        rules[self._currentRuleIndex], rules[self._currentRuleIndex - 1] = rules[self._currentRuleIndex - 1], rules[self._currentRuleIndex]
        self._currentRuleIndex -= 1
        self._populateRuleList()
        self.ruleList.setCurrentRow(self._currentRuleIndex)
        self._markDirty()

    def _onRuleMoveDown(self) -> None:
        """Move selected rule down."""

        if not self._generator or self._currentRuleIndex >= len(self._generator.flexTransRules) - 1:

            return

        rules = self._generator.flexTransRules
        rules[self._currentRuleIndex], rules[self._currentRuleIndex + 1] = rules[self._currentRuleIndex + 1], rules[self._currentRuleIndex]
        self._currentRuleIndex += 1
        self._populateRuleList()
        self.ruleList.setCurrentRow(self._currentRuleIndex)
        self._markDirty()

    def _onRuleDelete(self) -> None:
        """Delete selected rule."""

        if not self._generator or self._currentRuleIndex < 0:

            return

        if len(self._generator.flexTransRules) == 1:

            showMessageBox(self, QMessageBox.Icon.Warning, _translate("RuleAssistantWindow", "Error"), _translate("RuleAssistantWindow", "Cannot delete the last rule"))

            return

        self._generator.flexTransRules.pop(self._currentRuleIndex)
        self._populateRuleList()

        if self._currentRuleIndex >= len(self._generator.flexTransRules):

            self._currentRuleIndex = len(self._generator.flexTransRules) - 1

        if self._currentRuleIndex >= 0:

            self.ruleList.setCurrentRow(self._currentRuleIndex)

        self._markDirty()

    # Helper methods
    def _indexByIdentity(self, items, target) -> int:
        """Return the position of target within items, matched by object identity.

        The rule constituents (Word, Affix, Feature, ...) are @dataclasses, so their
        auto-generated __eq__ compares by field values. list.index()/in/remove therefore match
        the first *value-equal* item, which is the wrong one when value-equal duplicates coexist
        (e.g. a duplicated affix, or two blank words/affixes). The selected constituent is always
        the exact instance the user clicked, so identity is the correct comparison. Returns -1 if
        not found, though the selected object should always be present.
        """

        for index, item in enumerate(items):

            if item is target:

                return index

        return -1

    def _findPhraseContainingWord(self, rule, word) -> Optional["Phrase"]:
        """Find which phrase contains the given word.

        Args:
            rule: The current FLExTransRule
            word: The Word to find

        Returns:
            The Phrase containing the word, or None
        """

        # Identity, not value-equality: a source word and a target word can be value-equal (e.g. same wordId and content), so "in" could report the wrong phrase.
        if self._indexByIdentity(rule.source.words, word) != -1:

            return rule.source

        if self._indexByIdentity(rule.target.words, word) != -1:

            return rule.target

        return None

    def _findAndRemoveFeature(self, rule, feature) -> None:
        """Find and remove a feature from a word or affix.

        Args:
            rule: The current FLExTransRule
            feature: The Feature to remove
        """

        # Match by object identity, not value equality. Feature is a @dataclass, so its auto-generated __eq__ compares field values; two boxes can hold value-equal features (e.g. the same BantuNounGender:β on both a word and its prefix). Using "in"/remove would then delete the first value-equal match found (the word's), not the one the user clicked.
        for word in rule.source.words + rule.target.words:

            for index, wordFeature in enumerate(word.features):

                if wordFeature is feature:

                    del word.features[index]

                    return

            for affix in word.affixes:

                for index, affixFeature in enumerate(affix.features):

                    if affixFeature is feature:

                        del affix.features[index]

                        return

    def _findAndClearCategory(self, rule, category) -> None:
        """Find and clear a category from its parent word.

        Args:
            rule: The current FLExTransRule
            category: The Category to clear
        """

        for word in rule.source.words + rule.target.words:

            # Compare by name since category objects may not be the same instance
            if word.categoryConstituent and word.categoryConstituent.name == category.name:

                word.wordCategory = ""
                word.categoryConstituent = Category(name="")

                return

    def getResult(self) -> WindowResult:
        """Get the result from the window.

        Returns:
            WindowResult tuple with (saved, ruleIndex, launchLrt)
        """

        return self._result

    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:
        """Handle window close event. The parameter name/type match QWidget.closeEvent."""

        if self._dirty:

            reply = showMessageBox(
                self, QMessageBox.Icon.Question,
                _translate("RuleAssistantWindow", "Changes may have been made."),
                _translate("RuleAssistantWindow", "Do you want to save any changes?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:

                self._onSave()

        self._saveWindowState()

        if a0 is not None:

            a0.accept()

        self.finished.emit()
