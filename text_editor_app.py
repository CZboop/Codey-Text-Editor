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
                split_words = text_to_highlight.split()
                for c, word in enumerate(split_words):
                    if condition(word)==True:
                        # finding the start index of word that matches condition using regex
                        iterator = re.finditer(f"\\b{word}\\b", text_to_highlight)
                        for match in iterator:
                            # then highlighting using method of parent class qsyntaxhighlighter, not defined here
                            self.setFormat(match.start(), len(word), format)

            # regex condition otherwise
            else:
                for match in re.finditer(condition, text_to_highlight):
                    start, end = match.span()
                    self.setFormat(start, end - start, format)

    def clear_mappings(self):
        self._mapping = {}

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

class StatusThread(QThread):
    cursor_value = pyqtSignal(list)
    def __init__(self, cursor_info):
        super(StatusThread, self).__init__()
        self.cursor_info = cursor_info

    def run(self):
        print("running")
        self.cursor_value.emit(self.return_cursor_info())

    def return_cursor_info(self):
        return self.cursor_info

# overriding text edit widget to have some text completion type features
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

class CustomiseDialog(qtw.QDialog):
    def __init__(self, mode):
        super().__init__()

        self.font_size = None
        self.font_family = None
        self.mode = mode

        self.verb_colour = None
        self.noun_colour = None
        self.adverb_colour = None
        self.adj_colour = None
        self.comment_colour = None

        self.setWindowTitle("Customisation Menu")
        width, height = 750, 400
        self.setMinimumSize(width, height)

        pixmapi = qtw.QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

        self.layout = qtw.QVBoxLayout()
        self.font_size_label = qtw.QLabel("Font Size")
        self.layout.addWidget(self.font_size_label)

        self.font_size_box = qtw.QSpinBox()
        self.font_size_box.setMinimum(8)
        self.font_size_box.setMaximum(300)
        self.layout.addWidget(self.font_size_box)

        # font family picker
        self.font_family_label = qtw.QLabel("Font")
        self.layout.addWidget(self.font_family_label)
        self.font_dropdown = qtw.QComboBox(self)
        font_list = ["Consolas", "Calibri", "Courier", "Helvetica", "Times", ]
        for font in font_list:
            self.font_dropdown.addItem(font)
        self.layout.addWidget(self.font_dropdown)

        self.highlight_colour_label = qtw.QLabel("Highlight Colours")
        self.layout.addWidget(self.highlight_colour_label)

        # customising colours for parts of speech and comments
        self.verb_dialog_button = qtw.QPushButton("Choose Verb Colour", self)
        self.layout.addWidget(self.verb_dialog_button)
        self.verb_dialog_button.clicked.connect(self.verb_colour_picker)

        self.noun_dialog_button = qtw.QPushButton("Choose Noun Colour", self)
        self.layout.addWidget(self.noun_dialog_button)
        self.noun_dialog_button.clicked.connect(self.noun_colour_picker)

        self.adverb_dialog_button = qtw.QPushButton("Choose Adverb Colour", self)
        self.layout.addWidget(self.adverb_dialog_button)
        self.adverb_dialog_button.clicked.connect(self.adverb_colour_picker)

        self.adj_dialog_button = qtw.QPushButton("Choose Adjective Colour", self)
        self.layout.addWidget(self.adj_dialog_button)
        self.adj_dialog_button.clicked.connect(self.adj_colour_picker)

        self.comment_dialog_button = qtw.QPushButton("Choose Comment Colour", self)
        self.layout.addWidget(self.comment_dialog_button)
        self.comment_dialog_button.clicked.connect(self.comment_colour_picker)

        # toggle light/ dark mode
        self.button_text = "Toggle Light/Dark Mode"
        self.toggle_button = qtw.QPushButton(self.button_text, self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.switch_mode)
        self.layout.addWidget(self.toggle_button)

        self.apply_label = qtw.QLabel("Apply Changes")
        self.layout.addWidget(self.apply_label)

        # button called apply changes but this will return class with set properties to be then applied from the main app window
        self.apply_button = qtw.QPushButton("Apply", self)
        self.layout.addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.submitclose)

        self.setLayout(self.layout)

    def submitclose(self):
        self.set_font_size()
        self.set_font_family()
        self.accept()

    def set_font_size(self):
        self.font_size = self.font_size_box.value()

    def set_font_family(self):
        self.font_family = str(self.font_dropdown.currentText())

    def verb_colour_picker(self):
        verb_colour_picker = qtw.QColorDialog().getColor()
        self.verb_colour = QColor(verb_colour_picker)

    def noun_colour_picker(self):
        noun_colour_picker = qtw.QColorDialog().getColor()
        self.noun_colour = QColor(noun_colour_picker)

    def adverb_colour_picker(self):
        adverb_colour_picker = qtw.QColorDialog().getColor()
        self.adverb_colour = QColor(adverb_colour_picker)

    def adj_colour_picker(self):
        adj_colour_picker = qtw.QColorDialog().getColor()
        self.adj_colour = QColor(adj_colour_picker)

    def comment_colour_picker(self):
        comment_colour_picker = qtw.QColorDialog().getColor()
        self.comment_colour = QColor(comment_colour_picker)

    def switch_mode(self):
        self.button_text = "Switch to Dark Mode" if self.mode == "light" else "Switch to Light Mode"
        self.mode = "light" if self.mode == "dark" else "dark"
        self.update()
        self.show()

# main application
class MainWindow(qtw.QMainWindow):
    # adding some extra properties the default constructor
    def __init__(self):
        super().__init__()

        self.mode = "dark"

        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []

        self.verb_colour = QColor("#b5ea78")
        self.noun_colour = QColor("#f1c96e")
        self.adj_colour = QColor("#b77fd7")
        self.adverb_colour = QColor("#c97477")
        self.comment_colour = QColor("#5F9EA0")

        self.filename = None

        self.font_family = "Consolas"
        self.font_size = 10

        # some setup for the application window
        width, height = 1500, 1000
        self.setWindowTitle("Untitled - Text Editor")
        self.setMinimumSize(width, height)
        pixmapi = qtw.QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

        # setting up ribbon menu
        file_menu = self.menuBar().addMenu('&File')
        edit_menu = self.menuBar().addMenu('&Edit')
        format_menu = self.menuBar().addMenu('&Format')
        view_menu = self.menuBar().addMenu('&View')
        help_menu = self.menuBar().addMenu('&Help')

        # creating actions and connecting them to methods they will trigger
        self.exit_action = qtw.QAction(self)
        self.exit_action.setText('&Exit')
        self.exit_action.triggered.connect(self.exit_method)

        self.save_action = qtw.QAction(self)
        self.save_action.setText('&Save')
        self.save_action.triggered.connect(self.save_method)

        self.save_as_action = qtw.QAction(self)
        self.save_as_action.setText('&Save As')
        self.save_as_action.triggered.connect(self.save_as_method)

        self.load_action = qtw.QAction(self)
        self.load_action.setText('&Open File')
        self.load_action.triggered.connect(self.load_file_method)

        self.new_file_action = qtw.QAction(self)
        self.new_file_action.setText('&New File')
        self.new_file_action.triggered.connect(self.new_file_method)

        self.customise_action = qtw.QAction(self)
        self.customise_action.setText('&Customise')
        self.customise_action.triggered.connect(self.customise_menu_method)

        # adding actions to menu, in the order will appear in the menu
        file_menu.addAction(self.new_file_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(self.exit_action)

        format_menu.addAction(self.customise_action)

        #setting up bottom status bar
        self.statusbar = qtw.QStatusBar()
        self.setStatusBar(self.statusbar)

        # adding keyboard shortcuts
        self.shortcut_comment = qtw.QShortcut(QKeySequence('Ctrl+/'), self)
        self.shortcut_comment.activated.connect(self.comment_shortcut)

        # adding an instance of syntaxhighlighter and text input(assigned in define_conditions)
        self.highlighter = SyntaxHighlighter()

        self.setup_highlighter()
        self.setCentralWidget(self.text_input)

        self.line_column_label = f"Line {self.get_cursor_loc()[0]}, Column {self.get_cursor_loc()[1]}"
        self.statusbar.showMessage(self.line_column_label)
        self.start_status_thread()

        # setting some styling and starting worker thread background processes
        self.setStyleSheet("QTextEdit {background-color: rgb(30, 30, 30); color: white}")

        self.start_worker_thread()

    def get_cursor_loc(self):
        cursor = self.text_input.textCursor()
        # print(cursor.columnNumber())
        return [cursor.blockNumber() + 1, cursor.columnNumber() + 1]

    def exit_method(self):
        qtw.qApp.quit()

    def save_method(self):
        if not self.filename:
            self.save_as_method()
        else:
            text = self.text_input.toPlainText()
            with open(self.filename + '.txt', 'w') as file:
                file.write(text)

    def save_as_method(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(self, 'Save file', '', 'Text files (*.txt)')
        self.filename = filename
        if len(filename) > 0:
            self.setWindowTitle('{} - Text Editor'.format(self.filename))
            text = self.text_input.toPlainText()
            with open(self.filename, 'w') as file:
                file.write(text)

    def load_file_method(self):
        # select file using QFileDialog
        filename, _ = qtw.QFileDialog.getOpenFileName(self, 'Open File', '', 'Text Files (*.txt)')
        # read contents using general read file
        with open(filename, 'r') as file:
            file_text = file.read()
        # insert text into the text box
        self.text_input.insertPlainText(file_text)
        # set filename to name of opened file
        self.filename = filename
        self.setWindowTitle('{} - Text Editor'.format(self.filename))

    def new_file_method(self):
        # checking if latest updates have been saved
        if self.unsaved_changes():
            # dialog to ask whether to save
            want_to_save = qtw.QMessageBox.question(self, 'Save Changes', 'There are unsaved changes. Would you like to save?',
            qtw.QMessageBox.Yes | qtw.QMessageBox.No)
            if want_to_save == qtw.QMessageBox.Yes:
                # save if has filename else save as (logic already in save method)
                self.save_method()
            # cancelling new file if neither button pressed
            elif want_to_save != qtw.QMessageBox.No:
                return
        # make a new file by resetting everything including filename and text input contents
        self.reset_properties()

    def unsaved_changes(self):
        # if it's still untitled can assume unsaved changes as long as it's not empty
        current_text = self.text_input.toPlainText()
        if self.filename == None:
            if len(current_text) == 0:
                return False
            else:
                return True
        # otherwise check if the file at path is the same as the contents of text input
        else:
            with open(self.filename, 'r') as file:
                saved_text = file.read()
            if current_text == saved_text:
                return False
            else:
                return True

    def reset_properties(self):
        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []

        self.filename = None
        self.setWindowTitle("Untitled - Text Editor")
        self.setup_highlighter()
        self.setCentralWidget(self.text_input)

    def customise_menu_method(self):
        customise_menu = CustomiseDialog(self.mode)
        # customise_menu.exec()
        if customise_menu.exec_():
            self.update_font(customise_menu.font_size, customise_menu.font_family)
            self.update_highlight_colours(customise_menu.verb_colour, customise_menu.noun_colour, customise_menu.adverb_colour, customise_menu.adj_colour, customise_menu.comment_colour)
            self.update_mode(customise_menu.mode)

    def update_mode(self, mode):
        self.mode = mode
        if mode == "light":
            self.setStyleSheet("QTextEdit {background-color: rgb(255, 255, 255); color: black}")
        else:
            self.setStyleSheet("QTextEdit {background-color: rgb(30, 30, 30); color: white}")

    def update_font(self, font_size, font_family):
        self.font_size = font_size
        self.font_family = font_family
        # setting existing font to be the size given
        cursor = self.text_input.textCursor()
        self.text_input.selectAll()
        self.text_input.setFontPointSize(self.font_size)
        self.text_input.setTextCursor(cursor)
        # setting this as size going forward, keeping current font family
        new_font = QFont(self.font_family, self.font_size)
        self.text_input.setFont(new_font)

    def update_highlight_colours(self, verb_colour, noun_colour, adverb_colour, adj_colour, comment_colour):
        if verb_colour:
            self.verb_colour = verb_colour
        if noun_colour:
            self.noun_colour = noun_colour
        if adverb_colour:
            self.adverb_colour = adverb_colour
        if adj_colour:
            self.adj_colour = adj_colour
        if comment_colour:
            self.comment_colour = comment_colour
        # applying these changes to the conditions of the text highlighter
        self.highlighter.clear_mappings()
        self.define_conditions()

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

    def start_status_thread(self):
        self.status = StatusThread(self.get_cursor_loc())
        self.status.start()
        self.status.finished.connect(self.when_status_finished)
        self.status.cursor_value.connect(self.update_status)

    def when_status_finished(self):
        self.start_status_thread()

    def update_status(self, info):
        self.line_column_label = f"Line {info[0]}, Column {info[1]}"
        self.statusbar.showMessage(self.line_column_label)

# defining formatting conditions for highlighting
# mostly based on word being in part of speech tagged list with some regex based formatting
    def setup_highlighter(self):
        # disconnecting highlighter from text input/document to refresh formatting conditions
        self.highlighter.setDocument(None)

        self.define_conditions()

        # creating the textedit box and connecting the highlighter to that box
        self.text_input = QTextEdit(self, lineWrapMode=qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth=100)
        self.text_input.setFont(QFont(self.font_family, self.font_size))
        self.highlighter.setDocument(self.text_input.document())

    def define_conditions(self):
        # formatting for some major parts of speech
        verb_format = QTextCharFormat()
        verb_format.setForeground(self.verb_colour)

        noun_format = QTextCharFormat()
        noun_format.setForeground(self.noun_colour)

        adj_format = QTextCharFormat()
        adj_format.setForeground(self.adj_colour)

        adverb_format = QTextCharFormat()
        adverb_format.setForeground(self.adverb_colour)

        # lambda function for cleaner evaluation in highlightblock method, call and check if true
        pos_info = [[lambda x: x in self.verbs, verb_format], [lambda x: x in self.nouns, noun_format],
        [lambda x: x in self.adjs, adj_format], [lambda x: x in self.adverbs, adverb_format]]

        # adding to the highlighter instance
        for i, j in pos_info:
            self.highlighter.set_mapping(i, j)

        # comment formatting with hashtag for now
        comment_format = QTextCharFormat()
        comment_format.setForeground(self.comment_colour)
        # regex for anything from hashtag till end of line
        self.highlighter.set_mapping(r'#.*$', comment_format)

# running app
if __name__=="__main__":
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
