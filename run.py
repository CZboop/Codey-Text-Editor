from main_window import MainWindow
from customise_dialog import CustomiseDialog
from text_edit import QTextEdit
from worker_thread import WorkerThread
from highlighter import SyntaxHighlighter

import PyQt5.QtWidgets as qtw
import sys

if __name__=="__main__":
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()