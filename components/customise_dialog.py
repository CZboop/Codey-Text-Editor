import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import sys

class CustomiseDialog(qtw.QDialog):
    # adding extra attributes to store info that will be sent back to gui mainwindow
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

        #calling methods to set up dialog window and populate with widgets
        self.window_setup()
        self.widget_setup()

    def window_setup(self):
        self.setWindowTitle("Customisation Menu")
        width, height = 750, 400
        self.setMinimumSize(width, height)

        pixmapi = qtw.QStyle.SP_DialogSaveButton
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

    # adding widgets for each thing that can be customised
    def widget_setup(self):
        self.layout = qtw.QVBoxLayout()

        # font size, label and spinbox to increase/decrease
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

        # portion of dialog for setting highlight colours
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

        # layout created at start of method now populated and here set it as the layout for this dialog
        self.setLayout(self.layout)

    # calling methods and closing once 'apply' button is clicked
    def submitclose(self):
        self.set_font_size()
        self.set_font_family()
        self.accept()

    # getting font size from widget and setting class attribute based on it
    def set_font_size(self):
        self.font_size = self.font_size_box.value()

    # getting font family from widget and setting class attribute based on it
    def set_font_family(self):
        self.font_family = str(self.font_dropdown.currentText())

    # getting part of speech and comment colours from widget and setting class attribute based on it
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

    # switching to opposite mode out of light and dark
    def switch_mode(self):
        self.button_text = "Switch to Dark Mode" if self.mode == "light" else "Switch to Light Mode"
        self.mode = "light" if self.mode == "dark" else "dark"
        self.update()
        self.show()