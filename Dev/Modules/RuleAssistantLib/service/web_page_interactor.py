"""Web Page Interactor - QWebChannel bridge to JavaScript"""

from PyQt6.QtCore import QObject, pyqtSlot


class WebPageInteractor(QObject):
    """QObject that receives calls from JavaScript via QWebChannel.

    The JavaScript function toApp() calls methods on this object
    to communicate user interactions (clicks on tree elements).
    """

    def __init__(self, controller):
        """Initialize the interactor.

        Args:
            controller: The main window controller to notify of interactions
        """
        super().__init__()
        self._controller = controller
        self._x_coord = 0
        self._y_coord = 0

    @pyqtSlot(int)
    def setXCoord(self, x: int) -> None:
        """Set the X coordinate of the mouse click.

        Args:
            x: Screen X coordinate
        """
        self._x_coord = x

    @pyqtSlot(int)
    def setYCoord(self, y: int) -> None:
        """Set the Y coordinate of the mouse click.

        Args:
            y: Screen Y coordinate
        """
        self._y_coord = y

    @pyqtSlot(str)
    def setItemClickedOn(self, item: str) -> None:
        """Process a click on a tree element.

        Args:
            item: The element identifier (e.g., "w.5" for word with id 5)
        """
        if self._controller:
            self._controller.process_item_clicked_on(item, self._x_coord, self._y_coord)

    @property
    def x_coord(self) -> int:
        """Get the stored X coordinate."""
        return self._x_coord

    @property
    def y_coord(self) -> int:
        """Get the stored Y coordinate."""
        return self._y_coord
