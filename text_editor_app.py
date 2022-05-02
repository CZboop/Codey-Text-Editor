import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat
import nltk
import re

import sys

test_words = ['this', 'is', 'highlighted']

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}

    def set_mapping(self, condition, condition_format):
        self._mapping[condition] = condition_format

    def highlightBlock(self, text_to_highlight):
        for condition, format in self._mapping.items():
            # find out if matches condition
            for match in re.finditer(condition, text_to_highlight):
                start, end = match.span()
                self.setFormat(start, end - start, format)

# issue is how to handle back and forth to and from the gui/ across threads
# actually no problem can just pass and back and forth as class arg and signal
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
        # print(self.text)
        # need to use signal rather than just returning to pass back across threads
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
        return {"verbs": self.verbs, "nouns": self.nouns, "adjs": self.adjs, "adverbs": self.adverbs}


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        width, height = 1500, 1000
        self.setWindowTitle("Text Editor")
        self.setMinimumSize(width, height)

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
        # print(value)
        pass
        # TODO: probably assign as properties of the mainwindow class then handle highlighting as below with word match regex initially

    def define_conditions(self):
        word_format = QTextCharFormat()
        word_format.setForeground(Qt.red)
        # using regex for now, but just using it to check for a logical condition bit long?
        pattern = "(?:[\s]|^)({})(?=[\s]|$)".format("|".join(test_words))

        self.highlighter.set_mapping(pattern, word_format)

        # verb_format = QTextCharFormat()
        # verb_format.setForeground(Qt.green)
        # verb_pattern = "(?:[\s]|^)({})(?=[\s]|$)".format("|".join(self.verbs))
        #
        # self.highlighter.set_mapping(verb_pattern, verb_format)

        self.text_input = qtw.QTextEdit(self, lineWrapMode=qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth=100)
        self.highlighter.setDocument(self.text_input.document())


app = qtw.QApplication(sys.argv)

window = MainWindow()
window.show()

if __name__=="__main__":
    app.exec()
