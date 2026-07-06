import sys
import unicodedata
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem

class PasteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab-Separated Data Alignment")
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Create the grid table, with the row and column headers hidden
        self.table = QTableWidget()

        layout.addWidget(self.table)
        
        # Paste Button
        self.btn_paste = QPushButton("Paste from Clipboard")
        self.btn_paste.clicked.connect(self.paste_data)
        layout.addWidget(self.btn_paste)

    def paste_data(self):
        # Get text from system clipboard
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        # Break text into rows and columns using U+0009 (\t)
        rows = [line.split('\t') for line in text.strip().split('\n') if line]
        
        if not rows:
            return

        # If any character on the first row belongs to a right-to-left script (Arabic, Hebrew,
        # etc. - detected via Unicode's bidirectional category rather than hard-coded ranges),
        # lay the table out right to left; otherwise use the normal left-to-right direction.
        first_row_is_rtl = any(unicodedata.bidirectional(ch) in ('R', 'AL') for cell in rows[0] for ch in cell)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft if first_row_is_rtl else Qt.LayoutDirection.LeftToRight)

        # Configure table dimensions
        num_rows = len(rows)
        num_cols = max(len(row) for row in rows)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        
        # Populate the grid
        for row_idx, row in enumerate(rows):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(item.strip()))
                
        # Keep the vertical header (so its column still shows) but blank out the auto-numbered row labels
        self.table.setVerticalHeaderLabels([''] * num_rows)
        self.table.setHorizontalHeaderLabels([''] * num_cols)

        self.apply_bold_formatting(rows, num_cols)

        # Automatically resize columns to fit the content perfectly (after bolding, so the
        # wider bold text is accounted for)
        self.table.resizeColumnsToContents()

        self.resize_window_to_fit_table()

    def apply_bold_formatting(self, rows, num_cols):
        # Look for a "new record" indicator column: one that's blank on some rows (continuation
        # rows of a record) and filled on others (the row that starts a new record). A column
        # like this signals a grouped layout of row-labeled data blocks; plain rectangular data
        # won't have one, and gets no bold formatting.
        indicator_col = next(
            (col for col in range(num_cols)
             if any(col >= len(row) or not row[col].strip() for row in rows)
             and any(col < len(row) and row[col].strip() for row in rows)),
            None
        )

        if indicator_col is None:
            return

        # Bold every row where the indicator column starts a new record.
        for row_idx, row in enumerate(rows):
            if indicator_col < len(row) and row[indicator_col].strip():
                for col_idx in range(num_cols):
                    self.set_bold(row_idx, col_idx)

        # The "row header" column is the first fully-populated column after the indicator - e.g.
        # the repeated "Word" / "Morphemes" / "Lex. Entries" labels on every row of a record.
        header_col = next(
            (col for col in range(indicator_col + 1, num_cols)
             if all(col < len(row) and row[col].strip() for row in rows)),
            None
        )

        if header_col is not None:
            for row_idx in range(len(rows)):
                self.set_bold(row_idx, header_col)

    def set_bold(self, row, col):
        item = self.table.item(row, col)

        if item:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

    def resize_window_to_fit_table(self):
        table = self.table

        width = sum(table.columnWidth(col) for col in range(table.columnCount()))
        height = sum(table.rowHeight(row) for row in range(table.rowCount()))

        # The (blanked but still visible) headers take up their own space, which the column/row
        # sums above don't include - add the vertical header's width and the horizontal header's
        # height, or the table has no room for them and shows scrollbars instead.
        vHeader = table.verticalHeader()
        hHeader = table.horizontalHeader()

        if vHeader and vHeader.isVisible():
            width += vHeader.width()

        if hHeader and hHeader.isVisible():
            height += hHeader.height()

        frame = table.frameWidth() * 2
        width += frame
        height += frame

        # A couple of extra pixels absorb any rounding between the column-width sum and what
        # Qt actually needs to render every column without a scrollbar.
        width += 2
        height += 2

        # Require the table to be exactly this size, then let the dialog's layout grow to
        # fit it (along with the paste button and margins) so the whole table is visible
        # with no scrollbars.
        table.setMinimumSize(width, height)
        self.adjustSize()

        # Drop the minimum size back down afterward so the window stays freely resizeable
        # (including smaller than the full table) rather than being pinned to this size.
        table.setMinimumSize(0, 0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = PasteDialog()
    dialog.show()
    sys.exit(app.exec())