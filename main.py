from windows.mainWindow import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
main = Ui_MainWindow()
main.setupUi(main)
main.show()
app.exec()