from PySide6.QtWidgets import QApplication
from widget import Widget
import sys
import numpy as np


app = QApplication(sys.argv)

widget = Widget()
widget.show()

app.exec()