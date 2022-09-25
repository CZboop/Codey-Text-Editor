import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QSyntaxHighlighter, QTextCharFormat, QIcon, QKeySequence, QTextCursor, QKeyEvent
import nltk
import sys

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
        # get all the words from the input, pos tag and assign to list depending on which one they are?
        all_words = set(self.text.split())
        # the big parts of speech for now (start of tag to be more broad, may be tagged with multiple longer versions)
        verb_tag_start = "VB"
        noun_tag_start = "NN"
        adjective_tag_start = "JJ"
        adverb_tag_start = "RB"

        # tagging and adding to list based on tags
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
        
        # returning all words categorised within single dict
        return result_dict