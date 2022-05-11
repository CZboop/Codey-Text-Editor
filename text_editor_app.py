import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
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

# overriding text edit widget to have some text completion type features
class QTextEdit(qtw.QTextEdit):
    # overriding method in case of some events
    def keyPressEvent(self, event: QKeyEvent) -> None:
        # doubling up brackets and quotes automatically
        if event.type() == QEvent.KeyPress and event.key() in [Qt.Key_ParenLeft, Qt.Key_QuoteDbl,
        Qt.Key_Apostrophe, Qt.Key_BraceLeft, Qt.Key_BracketLeft]:
            cursor = self.textCursor()
            if event.key() == Qt.Key_ParenLeft:
                self.insertPlainText("()")
            elif event.key() == Qt.Key_QuoteDbl:
                self.insertPlainText("\"\"")
            elif event.key() == Qt.Key_Apostrophe:
                self.insertPlainText("\'\'")
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

# main application
class MainWindow(qtw.QMainWindow):
    # adding some extra properties the default constructor
    def __init__(self):
        super().__init__()

        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []

        # some setup for the application window
        width, height = 1500, 1000
        self.setWindowTitle("Text Editor")
        self.setMinimumSize(width, height)
        pixmapi = qtw.QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

        # setting up ribbon menu
        file_menu = self.menuBar().addMenu('&File')
        edit_menu = self.menuBar().addMenu('&Edit')
        view_menu = self.menuBar().addMenu('&View')
        help_menu = self.menuBar().addMenu('&Help')

        # creating actions and connecting them to methods they will trigger
        self.exit_action = qtw.QAction(self)
        self.exit_action.setText('&Exit')
        self.exit_action.triggered.connect(self.exit_method)

        self.save_action = qtw.QAction(self)
        self.save_action.setText('&Save')
        self.save_action.triggered.connect(self.save_method)

        # adding actions to menus
        file_menu.addAction(self.exit_action)
        file_menu.addAction(self.save_action)

        #setting up bottom status bar
        statusbar = qtw.QStatusBar()
        self.setStatusBar(statusbar)

        # adding keyboard shortcuts
        self.shortcut_comment = qtw.QShortcut(QKeySequence('Ctrl+/'), self)
        self.shortcut_comment.activated.connect(self.comment_shortcut)

        # adding an instance of syntaxhighlighter and text input(assigned in define_conditions)
        self.highlighter = SyntaxHighlighter()

        self.define_conditions()
        self.setCentralWidget(self.text_input)

        # setting some styling and starting worker thread background processes
        self.setStyleSheet("QTextEdit {background-color: rgb(0, 0, 0); color: white}")

        self.start_worker_thread()

    def exit_method(self):
        qtw.qApp.quit()

    def save_method(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(None, 'Save file', 'C:\\', 'Text files (*.txt)')
        text = self.text_input.toPlainText()
        with open(filename + '.txt', 'w') as file:
            file.write(text)

    def comment_shortcut(self):
        # using cursor positions and inserting text, getting current cursor info
        current_cursor = self.text_input.textCursor()
        current_cursor_pos = current_cursor.position()
        current_y = current_cursor.columnNumber()

        # move backward to start of line with columnnumber
        current_cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, current_y)
        # think have to reassign after each move of cursor?
        self.text_input.setTextCursor(current_cursor)
        self.text_input.insertPlainText('# ')
        # and reset to original position plus 2 for hashtag and space
        current_cursor.setPosition(current_cursor_pos + 2)
        self.text_input.setTextCursor(current_cursor)
        # TODO: should remove starting hashtag if one already there? currently will just add another one...

    def start_worker_thread(self):
        # starting worker thread and triggering method when it finishes
        self.worker = WorkerThread(self.text_input.toPlainText())
        self.worker.start()
        self.worker.finished.connect(self.when_worker_finished)
        # catching the returned signal from worker thread and passing to another method
        self.worker.return_value.connect(self.handle_pos_returned)

    def when_worker_finished(self):
        # what to do when the worker thread is finished, here just run it again
        self.start_worker_thread()

# reassigning values of part of speech lists after worker thread has processed text and returned them
    def handle_pos_returned(self, value):
        self.verbs = value.get("verbs")
        self.nouns = value.get("nouns")
        self.adjs = value.get("adjs")
        self.adverbs = value.get("adverbs")

# defining formatting conditions for highlighting
# mostly based on word being in part of speech tagged list with some regex based formatting
    def define_conditions(self):
        # disconnecting highlighter from text input/document to refresh formatting conditions
        self.highlighter.setDocument(None)

        # formatting for some major parts of speech
        verb_format = QTextCharFormat()
        verb_format.setForeground(Qt.green)

        noun_format = QTextCharFormat()
        noun_format.setForeground(Qt.red)

        adj_format = QTextCharFormat()
        adj_format.setForeground(Qt.magenta)

        adverb_format = QTextCharFormat()
        adverb_format.setForeground(Qt.cyan)

        # lambda function for cleaner evaluation in highlightblock method, call and check if true
        pos_info = [[lambda x: x in self.verbs, verb_format], [lambda x: x in self.nouns, noun_format],
        [lambda x: x in self.adjs, adj_format], [lambda x: x in self.adverbs, adverb_format]]

        # adding to the highlighter instance
        for i, j in pos_info:
            self.highlighter.set_mapping(i, j)

        # comment formatting with hashtag for now
        comment_format = QTextCharFormat()
        cadet_blue = QColor('#5F9EA0')
        comment_format.setForeground(cadet_blue)
        # regex for anything from hashtag till end of line
        self.highlighter.set_mapping(r'#.*$', comment_format)

        # creating the textedit box and connecting the highlighter to that box
        self.text_input = QTextEdit(self, lineWrapMode=qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth=100)
        self.highlighter.setDocument(self.text_input.document())

# running app
if __name__=="__main__":
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
