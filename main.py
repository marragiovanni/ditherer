import os, sys
from pathlib import Path
from window import MainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

BASE_DIR = Path(__file__).resolve().parent 
ICON_PATH = str(BASE_DIR / "ICON.png") 

if __name__ == "__main__": 
    app = QApplication(sys.argv)    
    app_icon = QIcon()
    app_icon.addFile(ICON_PATH, QSize(180, 180))
    app.setWindowIcon(app_icon)
    window = MainWindow()
    window.show()
    
    app.exec()
