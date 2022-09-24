import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import sys

class QTextEdit(qtw.QTextEdit):
    # overriding method in case of some events
    def keyPressEvent(self, event: QKeyEvent) -> None:
        # doubling up brackets and quotes automatically
        if event.type() == QEvent.KeyPress and event.key() in [Qt.Key_ParenLeft, Qt.Key_QuoteDbl,
        Qt.Key_BraceLeft, Qt.Key_BracketLeft]:
            cursor = self.textCursor()
            if event.key() == Qt.Key_ParenLeft:
                self.insertPlainText("()")
            elif event.key() == Qt.Key_QuoteDbl:
                self.insertPlainText("\"\"")
            elif event.key() == Qt.Key_BraceLeft:
                self.insertPlainText("{}")
            elif event.key() == Qt.Key_BracketLeft:
                self.insertPlainText("[]")
            # moving cursor back one to be in between brackets
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            # reconnecting cursor to widget
            self.setTextCursor(cursor)
            return
        # otherwise falling back to default super method of parent class
        return super().keyPressEvent(event)