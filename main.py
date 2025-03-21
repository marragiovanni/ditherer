import sys
from window import MainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


if __name__ == "__main__": 
    app = QApplication(sys.argv)
    app_icon = QIcon()
    app_icon.addFile('ICON.png', QSize(180, 180))
    app.setWindowIcon(app_icon)
    window = MainWindow()
    window.showFullScreen()
    window.show()
    
    app.exec()


