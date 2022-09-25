from components import SyntaxHighlighter
from components import QTextEdit
from components import WorkerThread
from components import CustomiseDialog
from components import StatsDialog

import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import nltk
import sys

class MainWindow(qtw.QMainWindow):
    # adding some extra properties to the default constructor
    def __init__(self):
        super().__init__()
        # starting in dark mode, can toggle to light mode in customise menu
        self.mode = "dark"
        # list of each part of speech for highlighting
        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []
        # initial highlight colours
        self.verb_colour = QColor("#b5ea78")
        self.noun_colour = QColor("#f1c96e")
        self.adj_colour = QColor("#b77fd7")
        self.adverb_colour = QColor("#c97477")
        self.comment_colour = QColor("#5F9EA0")
        # some default values 
        self.filename = None
        self.font_family = "Consolas"
        self.font_size = 10
        # calling some methods that will set properties of the window itself
        # adding the top ribbon menu and connecting it to relevant actions
        # setting up keyboard shortcuts
        self.window_setup()
        self.setup_menu()
        self.setup_shortcuts()
        # adding an instance of syntaxhighlighter and text input (assigned in define_conditions)
        self.highlighter = SyntaxHighlighter()
        self.setup_highlighter()
        self.setCentralWidget(self.text_input)
        # setting some styling and starting worker thread background processes
        self.setStyleSheet("QTextEdit {background-color: rgb(30, 30, 30); color: white}")
        self.start_worker_thread()

    def window_setup(self):
        # some setup for the application window - size, title, icon
        width, height = 1500, 1000
        self.setWindowTitle("Untitled - Text Editor")
        self.setMinimumSize(width, height)
        pixmapi = qtw.QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

    def setup_menu(self):
        # setting up ribbon menu
        file_menu = self.menuBar().addMenu('&File')
        edit_menu = self.menuBar().addMenu('&Edit')
        format_menu = self.menuBar().addMenu('&Format')
        view_menu = self.menuBar().addMenu('&View')

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

        self.wrap_text_action = qtw.QAction(self)
        self.wrap_text_action.setText('&Wrap Text')
        self.wrap_text_action.triggered.connect(self.wrap_text_method)
        self.wrap_text_action.setCheckable(True)
        self.wrap_text_action.setChecked(True)

        self.bold_action = qtw.QAction(self)
        self.bold_action.setText('&Bold')
        self.bold_action.triggered.connect(self.bold_method)
        self.bold_action.setCheckable(True)
        self.bold_action.setChecked(False)

        self.italic_action = qtw.QAction(self)
        self.italic_action.setText('&Italic')
        self.italic_action.triggered.connect(self.italic_method)
        self.italic_action.setCheckable(True)
        self.italic_action.setChecked(False)

        self.plus_font_action = qtw.QAction(self)
        self.plus_font_action.setText('&Increase Font')
        self.plus_font_action.triggered.connect(self.plus_font_method)

        self.minus_font_action = qtw.QAction(self)
        self.minus_font_action.setText('&Decrease Font')
        self.minus_font_action.triggered.connect(self.minus_font_method)

        self.stats_action = qtw.QAction(self)
        self.stats_action.setText('&Statistics')
        self.stats_action.triggered.connect(self.stats_method)

        # adding actions to menu, in the order will appear in the menu
        file_menu.addAction(self.new_file_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(self.exit_action)

        format_menu.addAction(self.customise_action)
        format_menu.addAction(self.wrap_text_action)

        edit_menu.addAction(self.bold_action)
        edit_menu.addAction(self.italic_action)
        edit_menu.addAction(self.stats_action)

        view_menu.addAction(self.plus_font_action)
        view_menu.addAction(self.minus_font_action)

        #setting up bottom status bar (no content)
        self.statusbar = qtw.QStatusBar()
        self.setStatusBar(self.statusbar)

    def setup_shortcuts(self):
        # adding keyboard shortcuts - what key sequence will trigger, and what method that will call
        self.shortcut_comment = qtw.QShortcut(QKeySequence('Ctrl+/'), self)
        self.shortcut_comment.activated.connect(self.comment_shortcut)

        self.shortcut_bold = qtw.QShortcut(QKeySequence('Ctrl+b'), self)
        self.shortcut_bold.activated.connect(self.bold_method)

        self.shortcut_italic = qtw.QShortcut(QKeySequence('Ctrl+i'), self)
        self.shortcut_italic.activated.connect(self.italic_method)

        self.shortcut_plus = qtw.QShortcut(QKeySequence('Ctrl+='), self)
        self.shortcut_plus.activated.connect(self.plus_font_method)

        self.shortcut_minus = qtw.QShortcut(QKeySequence('Ctrl+-'), self)
        self.shortcut_minus.activated.connect(self.minus_font_method)

    # shortcut for increasing font point size by two
    def plus_font_method(self):
        self.font_size += 2
        self.text_input.setFontPointSize(self.font_size)

    # shortcut for decreasing font point size by two
    def minus_font_method(self):
        self.font_size -= 2
        self.text_input.setFontPointSize(self.font_size)

    # method to bold or unbold font, either with shortcut of by clicking in menu
    def bold_method(self):
        # checking enum for bold else setting to normal
        if self.text_input.fontWeight() == 75:
            self.text_input.setFontWeight(QFont.Normal)
            self.bold_action.setChecked(False)

            # here checkin if some text was selected and if so...
            cursor = self.text_input.textCursor()
            
            if cursor.selectionStart() != cursor.selectionEnd():
                # will set current text to bold
                cursor.clearSelection()
                self.text_input.setTextCursor(cursor)
                # but then reset font to normal for new text written after
                self.text_input.setFontWeight(QFont.Normal)
                self.bold_action.setChecked(False)
                # currently above always sets to bold and not toggling depending on what current is (selection may be mixed)
        else:
            self.text_input.setFontWeight(QFont.Bold)
            self.bold_action.setChecked(True)
    
    # method to italicise or unitalicise font, either with shortcut of by clicking in menu
    def italic_method(self):
        # checking if already italic
        if self.text_input.fontItalic() == True:
            self.text_input.setFontItalic(False)
            self.italic_action.setChecked(False)

            # here checkin if some text was selected and if so...
            cursor = self.text_input.textCursor()
            
            if cursor.selectionStart() != cursor.selectionEnd():
                # will set current text to italic
                cursor.clearSelection()
                self.text_input.setTextCursor(cursor)
                # but then reset font to normal for new text written after
                self.text_input.setFontItalic(True)
                self.italic_action.setChecked(True)
                # currently above always sets to italic and not toggling depending on what current is (selection may be mixed)
        else:
            self.text_input.setFontItalic(True)
            self.italic_action.setChecked(True)

    # method to get the statistics that will be disaplayed in stats dialog
    def stats_method(self):
        split_text = self.text_input.toPlainText().split(" ")
        word_count = len([i for i in split_text if len(i) > 0])
        verb_count = 0
        noun_count = 0
        adj_count = 0 
        adv_count = 0
        char_count = len(self.text_input.toPlainText())

        verb_tag_start = "VB"
        noun_tag_start = "NN"
        adjective_tag_start = "JJ"
        adverb_tag_start = "RB"

        for word, tag in nltk.pos_tag(split_text):
            if tag.startswith((verb_tag_start, noun_tag_start, adjective_tag_start, adverb_tag_start)):
                if tag.startswith(verb_tag_start):
                    verb_count += 1
                elif tag.startswith(noun_tag_start):
                    noun_count +=1 
                elif tag.startswith(adjective_tag_start):
                    adj_count += 1
                else:
                    adv_count += 1

        stats_dialog = StatsDialog([word_count, char_count, verb_count, noun_count, adj_count, adv_count])
        stats_dialog.exec()

    # closing the main window
    def exit_method(self):
        qtw.qApp.quit()

    # method to save file, calls save as if file is not already saved, otherwise overwrites current filename
    def save_method(self):
        if not self.filename:
            self.save_as_method()
        else:
            text = self.text_input.toPlainText()
            with open(self.filename + '.txt', 'w') as file:
                file.write(text)

    # save as method, opens file explorer starting at current directory and gets input on file name
    def save_as_method(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(self, 'Save file', '', 'Text files (*.txt)')
        self.filename = filename
        if len(filename) > 0:
            self.setWindowTitle('{} - Text Editor'.format(self.filename))
            text = self.text_input.toPlainText()
            with open(self.filename, 'w') as file:
                file.write(text)

    # loading file using qt filedialog, reads text and inserts that text into the central text edit widget
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

    # method to create a new file, checks for unsaved changes and warns user giving ability to save if unsaved changes
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

    # method to toggle whether text wraps at end of line or not
    def wrap_text_method(self):
        current_wrap = self.text_input.lineWrapMode()
        # enum corresponding to default mode WidgetWidth
        if current_wrap == 1:
            self.text_input.setLineWrapMode(qtw.QTextEdit.NoWrap)
        else:
            self.text_input.setLineWrapMode(qtw.QTextEdit.WidgetWidth)

    # method used to check if there are unsaved changes
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

    # resetting rpoperties for use when creating a new file
    def reset_properties(self):
        self.verbs = []
        self.nouns = []
        self.adjs = []
        self.adverbs = []

        self.filename = None
        self.setWindowTitle("Untitled - Text Editor")
        self.setup_highlighter()
        self.setCentralWidget(self.text_input)

    # method to execute the customise dialog and apply changes from it once it is closed/changes are applied from dialog
    def customise_menu_method(self):
        customise_menu = CustomiseDialog(self.mode)
        # customise_menu.exec()
        if customise_menu.exec_():
            self.update_font(customise_menu.font_size, customise_menu.font_family)
            self.update_highlight_colours(customise_menu.verb_colour, customise_menu.noun_colour, customise_menu.adverb_colour, customise_menu.adj_colour, customise_menu.comment_colour)
            self.update_mode(customise_menu.mode)

    # method to toggle between light and dark mode
    def update_mode(self, mode):
        self.mode = mode
        if mode == "light":
            self.setStyleSheet("QTextEdit {background-color: rgb(255, 255, 255); color: black}")
        else:
            self.setStyleSheet("QTextEdit {background-color: rgb(30, 30, 30); color: white}")

    # method to update font (size and family) across the existing text edit
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

    # updating colours that each part of speech is highlighted with
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

    # method to comment out text with keyboard shortcut
    # moves to start of line, adds comment char and moves back
    def comment_shortcut(self):
        # using cursor positions and inserting text, getting current cursor info
        current_cursor = self.text_input.textCursor()
        current_cursor_pos = current_cursor.position()
        current_y = current_cursor.columnNumber()

        # move backward to start of line with columnnumber
        current_cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, current_y)
        # think have to reassign after each move of cursor?
        self.text_input.setTextCursor(current_cursor)
        char_cursor = self.text_input.textCursor()
        char_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        first_char = char_cursor.selectedText()
        # if not already comment, comment
        if first_char != "#":
            self.text_input.insertPlainText('# ')
            # and reset to original position plus 2 for hashtag and space
            current_cursor.setPosition(current_cursor_pos + 2)
            self.text_input.setTextCursor(current_cursor)
        # else comment
        else:
            # char delta variable will track how far from cursor start position to move back (2 if # and space, 1 if just #)
            char_delta = 2
            # selecting first two chars of line
            current_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            current_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            # deselecting second char if it's not a space
            if current_cursor.selectedText()[-1] != " ":
                current_cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                char_delta -= 1
            # deleting selected text and resetting cursor connected to editor
            current_cursor.removeSelectedText()
            current_cursor.setPosition(current_cursor_pos - char_delta)
            self.text_input.setTextCursor(current_cursor)

    # worker thread for part of speech tagging in background
    def start_worker_thread(self):
        # starting worker thread and triggering method when it finishes
        self.worker = WorkerThread(self.text_input.toPlainText())
        self.worker.start()
        self.worker.finished.connect(self.when_worker_finished)
        # catching the returned signal from worker thread and passing to another method
        self.worker.return_value.connect(self.handle_pos_returned)

    # restarts thread so it runs continuously
    def when_worker_finished(self):
        self.start_worker_thread()

    # reassigning values of part of speech lists after worker thread has processed text and returned them
    def handle_pos_returned(self, value):
        self.verbs = value.get("verbs")
        self.nouns = value.get("nouns")
        self.adjs = value.get("adjs")
        self.adverbs = value.get("adverbs")

    # defining formatting conditions for highlighting
    # mostly based on word being in part of speech tagged list with some regex based formatting
    def setup_highlighter(self):
        # disconnecting highlighter from text input/document to refresh formatting conditions
        self.highlighter.setDocument(None)

        self.define_conditions()

        # creating the textedit box and connecting the highlighter to that box
        self.text_input = QTextEdit(self, lineWrapMode=qtw.QTextEdit.WidgetWidth)
        self.text_input.setFont(QFont(self.font_family, self.font_size))
        self.highlighter.setDocument(self.text_input.document())

    # defining conditions for when text will be highlighted
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