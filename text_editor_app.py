import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon
import nltk
import re
import time
import sys

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}

    def set_mapping(self, condition, condition_format):
        self._mapping[condition] = condition_format

# overriding main highlight function to be able to highlight based on conditional logic and also regex
    def highlightBlock(self, text_to_highlight):
        for condition, format in self._mapping.items():
            # different types of conditions, logical ones are functions so will be callable
            if hasattr(condition, "__call__"):
                # find out if matches condition
                # matches = [i for i in text_to_highlight.split() if condition(i)==True]
                split_words = text_to_highlight.split()
                for c, word in enumerate(split_words):
                    if condition(word)==True:
                        start = sum([len(i) for i in split_words[:c]]) + c
                        self.setFormat(start, len(word), format)
            # regex condition otherwise
            else:
                for match in re.finditer(condition, text_to_highlight):
                    start, end = match.span()
                    self.setFormat(start, end - start, format)

# worker thread for background process, using singal to pass info back to gui app
# and adding a class property to pass from gui to thread
class WorkerThread(QThread):
    return_value = pyqtSignal(object)
    def __init__(self, text):
        super(WorkerThread, self).__init__()
        self.text = text

        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []

    def run(self):
        # method automatically runs when the gui starts the thread
        # runs the other main method set_pos_lists and emits it back for the app to catch
        self.return_value.emit(self.set_pos_lists())

    def set_pos_lists(self):
        # thinking get all the words from the input, pos tag and assign to list depending on which one they are?
        all_words = set(self.text.split())
        # the big parts of speech for now
        verb_tag_start = "VB"
        noun_tag_start = "NN"
        adjective_tag_start = "JJ"
        adverb_tag_start = "RB"

        for word, tag in nltk.pos_tag(all_words):
            if tag.startswith((verb_tag_start, noun_tag_start, adjective_tag_start, adverb_tag_start)):
                if tag.startswith(verb_tag_start):
                    self.verbs.append(word)
                elif tag.startswith(noun_tag_start):
                    self.nouns.append(word)
                elif tag.startswith(adjective_tag_start):
                    self.adjs.append(word)
                else:
                    self.adverbs.append(word)

        result_dict = {"verbs": self.verbs, "nouns": self.nouns, "adjs": self.adjs, "adverbs": self.adverbs}

        return result_dict

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []

        width, height = 1500, 1000
        self.setWindowTitle("Text Editor")
        self.setMinimumSize(width, height)
        pixmapi = qtw.QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)

        self.setWindowIcon(icon)

        self.highlighter = SyntaxHighlighter()
        # self.text_input = qtw.QTextEdit(self, lineWrapMode=qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth=100)

        self.define_conditions()
        self.setCentralWidget(self.text_input)
        # self.set_pos_lists()
        self.setStyleSheet("QTextEdit {background-color: rgb(0, 0, 0); color: white}")

        self.start_worker_thread()

    def start_worker_thread(self):
        # starting worker thread and triggering something when it finishes
        self.worker = WorkerThread(self.text_input.toPlainText())
        self.worker.start()
        self.worker.finished.connect(self.when_worker_finished)
        self.worker.return_value.connect(self.handle_pos_returned)

    def when_worker_finished(self):
        # what to do when the worker thread is finished
        # here trying to just run it again
        self.start_worker_thread()

    def handle_pos_returned(self, value):
        self.verbs = value.get("verbs")
        self.nouns = value.get("nouns")
        self.adjs = value.get("adjs")
        self.adverbs = value.get("adverbs")

    def define_conditions(self):
        self.highlighter.setDocument(None)

        verb_format = QTextCharFormat()
        verb_format.setForeground(Qt.green)

        noun_format = QTextCharFormat()
        noun_format.setForeground(Qt.red)

        adj_format = QTextCharFormat()
        adj_format.setForeground(Qt.magenta)

        adverb_format = QTextCharFormat()
        adverb_format.setForeground(Qt.cyan)

        pos_info = [[lambda x: x in self.verbs, verb_format], [lambda x: x in self.nouns, noun_format],
        [lambda x: x in self.adjs, adj_format], [lambda x: x in self.adverbs, adverb_format]]

        for i, j in pos_info:
            self.highlighter.set_mapping(i, j)

        # comments with hashtag for now
        comment_format = QTextCharFormat()
        cadet_blue = QColor('#5F9EA0')
        comment_format.setForeground(cadet_blue)

        self.highlighter.set_mapping(r'#.*$', comment_format)

        self.text_input = qtw.QTextEdit(self, lineWrapMode=qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth=100)
        self.highlighter.setDocument(self.text_input.document())

# running app
if __name__=="__main__":
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
