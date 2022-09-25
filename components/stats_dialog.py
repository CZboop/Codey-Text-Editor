import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import sys

class StatsDialog(qtw.QDialog):
    def __init__(self, stats):
        super().__init__()
        self.word_count = stats[0]
        self.char_count = stats[1]

        self.verb_count = stats[2]
        self.noun_count = stats[3]
        self.adj_count = stats[4]
        self.adv_count = stats[5]

        self.setWindowTitle("Statistics")
        width, height = 450, 400
        self.setMinimumSize(width, height)

        pixmapi = qtw.QStyle.SP_FileDialogInfoView
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

        self.layout = qtw.QVBoxLayout()

        self.word_count_label = qtw.QLabel(f"Word Count: {self.word_count}")
        self.layout.addWidget(self.word_count_label)
        self.char_count_label = qtw.QLabel(f"Character Count: {self.char_count}")
        self.layout.addWidget(self.char_count_label)

        self.noun_count_label = qtw.QLabel(f"Noun Count: {self.noun_count}")
        self.layout.addWidget(self.noun_count_label)
        self.verb_count_label = qtw.QLabel(f"Verb Count: {self.verb_count}")
        self.layout.addWidget(self.verb_count_label)
        self.adj_count_label = qtw.QLabel(f"Adjective Count: {self.adj_count}")
        self.layout.addWidget(self.adj_count_label)
        self.adv_count_label = qtw.QLabel(f"Adverb Count: {self.adv_count}")
        self.layout.addWidget(self.adv_count_label)

        self.setLayout(self.layout)

    def submitclose(self):
        self.accept()