import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import re
import sys

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}

    # method to add each mapping to the dict
    def set_mapping(self, condition, condition_format):
        self._mapping[condition] = condition_format

    # overriding main highlight function to be able to highlight based on conditional logic and also regex
    def highlightBlock(self, text_to_highlight):
        for condition, format in self._mapping.items():
            # different types of conditions, logical ones are functions so will be callable
            if hasattr(condition, "__call__"):
                # find out if matches condition
                split_words = text_to_highlight.split()
                for c, word in enumerate(split_words):
                    if condition(word.strip())==True:
                        # finding the start index of word that matches condition using regex
                        # stripping word but matches including punctuation right after word (word boundary before)
                        iterator = re.finditer(f"\\b{word}(?=[\W_]+|$)", text_to_highlight)
                        for match in iterator:
                            # then highlighting using method of parent class qsyntaxhighlighter, not defined here
                            self.setFormat(match.start(), len(word), format)

            # regex condition otherwise
            else:
                for match in re.finditer(condition, text_to_highlight):
                    start, end = match.span()
                    self.setFormat(start, end - start, format)
    
    # clearing mappings by setting to an empty dict
    def clear_mappings(self):
        self._mapping = {}
