from PyQt5.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QWidget, QCheckBox
from windows.detectionWindow import Ui_DetectionWindow
from operations.databaseOperations import DatabaseOperations
import webbrowser

class Ui_RegisterForm(QWidget):
    def setupUi(self, Form, name):
        if Form.objectName():
            Form.setObjectName(u"Register Form")
        Form.resize(503, 428)
        self.loginEdit = QLineEdit(Form)
        self.loginEdit.setObjectName(u"loginEdit")
        self.loginEdit.setGeometry(QRect(140, 100, 231, 31))
        self.passwordEdit = QLineEdit(Form)
        self.passwordEdit.setObjectName(u"passwordEdit")
        self.passwordEdit.setGeometry(QRect(140, 160, 231, 31))
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.confirmPasswordEdit = QLineEdit(Form)
        self.confirmPasswordEdit.setObjectName(u"confirmPasswordEdit")
        self.confirmPasswordEdit.setGeometry(QRect(140, 220, 231, 31))
        self.confirmPasswordEdit.setEchoMode(QLineEdit.Password)
        self.registerButton = QPushButton(Form)
        self.registerButton.setObjectName(u"registerButton")
        self.registerButton.setGeometry(QRect(180, 330, 151, 51))
        self.expiredLabel = QLabel(Form)
        self.expiredLabel.setObjectName(u"expiredLabel")
        self.expiredLabel.setEnabled(True)
        self.expiredLabel.setGeometry(QRect(120, 20, 271, 51))
        self.expiredLabel.setVisible(False)
        self.mailCheckbox = QCheckBox(Form)
        self.mailCheckbox.setObjectName(u"mailCheckbox")
        self.mailCheckbox.setGeometry(QRect(220, 280, 81, 20))
        self.telegramCheckbox = QCheckBox(Form)
        self.telegramCheckbox.setObjectName(u"telegramCheckbox")
        self.telegramCheckbox.setGeometry(QRect(320, 280, 131, 21))
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 280, 201, 16))

        self.registerButton.clicked.connect(self.register)

        self.name = name
        self.retranslateUi(Form)
        self.databaseOperation = DatabaseOperations()

        if self.name != "":
            self.label.setVisible(False)
            self.mailCheckbox.setVisible(False)
            self.telegramCheckbox.setVisible(False)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        if self.name != "":
            self.loginEdit.setText(self.name)
            self.loginEdit.setEnabled(False)
            self.expiredLabel.setVisible(True)
            
        self.loginEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Login", None))
        self.passwordEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Password", None))
        self.confirmPasswordEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Confirm Password", None))
        self.registerButton.setText(QCoreApplication.translate("Form", u"Register", None))
        self.expiredLabel.setText(QCoreApplication.translate("Form", u"Your password is expired please update it", None))
        self.mailCheckbox.setText(QCoreApplication.translate("Form", u"Use mail", None))
        self.telegramCheckbox.setText(QCoreApplication.translate("Form", u"Use telegram bot", None))
        self.label.setText(QCoreApplication.translate("Form", u"Choose how to recieve information", None))

    def register(self):
        expr = True
        if (self.mailCheckbox.isVisible()):
            expr = self.mailCheckbox.isChecked() or self.telegramCheckbox.isChecked()
            
        if self.passwordEdit.text() == self.confirmPasswordEdit.text() and (expr):
            if self.name == "":
                result, userId, telegramCode = self.databaseOperation.register(self.loginEdit.text(), self.passwordEdit.text(),
                                                                 self.mailCheckbox.isChecked(), self.telegramCheckbox.isChecked())
                
                if telegramCode:
                    url = f"https://telegram.me/irm_diplom_bot?start={telegramCode}"
                    webbrowser.open(url)

                if result:
                    self.detectionWindow = Ui_DetectionWindow()
                    self.detectionWindow.setupUi(self.detectionWindow, userId)
                    self.detectionWindow.show()
                    self.close()
            else:
                userId = self.databaseOperation.updatePassword(self.loginEdit.text(), self.passwordEdit.text())
                self.detectionWindow = Ui_DetectionWindow()
                self.detectionWindow.setupUi(self.detectionWindow, userId)
                self.detectionWindow.show()
                self.close()
        else:
            self.expiredLabel.setText("Please check entered passwords and choose one of methods to get messages")