import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import sys

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