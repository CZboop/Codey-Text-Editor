from components import MainWindow

import PyQt5.QtWidgets as qtw
import sys

if __name__=="__main__":
    app = qtw.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()