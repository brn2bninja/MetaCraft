from PySide6.QtWidgets import QApplication
from widget import Widget
import sys
import os

try: 
    os.chdir(sys._MEIPASS)
except:
    os.chdir(os.getcwd())

app = QApplication(sys.argv)

widget = Widget()
widget.show()

app.exec()