import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QSize, Qt

import sys

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        width, height = 1500, 1000

        self.setWindowTitle("Text Editor")
        self.setMinimumSize(width, height)

        text_input = qtw.QTextEdit(self, lineWrapMode=qtw.QTextEdit.FixedColumnWidth, lineWrapColumnOrWidth=100)
        self.setCentralWidget(text_input)

app = qtw.QApplication(sys.argv)

window = MainWindow()
window.show()

if __name__=="__main__":
    app.exec()
