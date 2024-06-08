from PyQt5.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt5.QtWidgets import QPushButton, QWidget, QMenuBar, QStatusBar, QLineEdit, QMainWindow, QTextEdit
from windows.detectionWindow import Ui_DetectionWindow
from windows.registerForm import Ui_RegisterForm
from operations.databaseOperations import DatabaseOperations

class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(404, 442)
        #MainWindow.setStyleSheet(u"background-color: rgb(8, 8, 8);")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.loginButton = QPushButton(self.centralwidget)
        self.loginButton.setObjectName(u"loginButton")
        self.loginButton.setGeometry(QRect(220, 290, 151, 51))
        
        self.registerButton = QPushButton(self.centralwidget)
        self.registerButton.setObjectName(u"registerButton")
        self.registerButton.setGeometry(QRect(30, 290, 151, 51))
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(90, 130, 231, 31))
        self.passwordEdit = QLineEdit(self.centralwidget)
        self.passwordEdit.setObjectName(u"passwordEdit")
        self.passwordEdit.setGeometry(QRect(90, 210, 231, 31))
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        self.operationalResult = QTextEdit(self.centralwidget)
        self.operationalResult.setObjectName(u"operationalResult")
        self.operationalResult.setEnabled(False)
        self.operationalResult.setGeometry(QRect(10, 10, 381, 101))

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 445, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.loginButton.clicked.connect(self.login)
        self.registerButton.clicked.connect(self.register)

        self.databaseOperation = DatabaseOperations()

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.loginButton.setText(QCoreApplication.translate("MainWindow", u"Login", None))
        self.registerButton.setText(QCoreApplication.translate("MainWindow", u"Register", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Login", None))
        self.passwordEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Password", None))
    # retranslateUi

    def login(self):
        result, isAdmin, userId, isPasswordExpired = self.databaseOperation.login(self.lineEdit.text(), self.passwordEdit.text())
        if result:
            if isPasswordExpired:
                self.initRegisterWindow(self.lineEdit.text())
                return
            
            self.detectionWindow = Ui_DetectionWindow()
            self.detectionWindow.setupUi(self.detectionWindow, userId, isAdmin)
            self.detectionWindow.show()
            self.close()
        else:
            self.operationalResult.setText("Credentials were wrong")

    def register(self):
        self.initRegisterWindow()

    def initRegisterWindow(self, name = ""):
        self.registerWindow = Ui_RegisterForm()
        self.registerWindow.setupUi(self.registerWindow, name)
        self.registerWindow.show()
        self.close()