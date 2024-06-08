from PyQt5.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt5.QtWidgets import QPushButton, QWidget, QLineEdit, QComboBox, QPlainTextEdit, QLabel
from operations.databaseOperations import DatabaseOperations

class Ui_AdminForm(QWidget):
    def setupUi(self, Form, userId):
        self.userId = userId
        if Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(543, 505)

        self.NamesBox = QComboBox(Form)
        self.NamesBox.setObjectName(u"NamesBox")
        self.NamesBox.setGeometry(QRect(260, 140, 201, 51))
        self.RoleEdit = QLineEdit(Form)
        self.RoleEdit.setObjectName(u"RoleEdit")
        self.RoleEdit.setEnabled(False)
        self.RoleEdit.setGeometry(QRect(260, 220, 201, 41))
        self.NewRoleEdit = QComboBox(Form)
        self.NewRoleEdit.setObjectName(u"NewRoleEdit")
        self.NewRoleEdit.setEnabled(True)
        self.NewRoleEdit.setGeometry(QRect(260, 290, 201, 41))
        self.DeleteUserButton = QPushButton(Form)
        self.DeleteUserButton.setObjectName(u"DeleteUserButton")
        self.DeleteUserButton.setGeometry(QRect(30, 370, 151, 61))
        self.UpdateRoleButton = QPushButton(Form)
        self.UpdateRoleButton.setObjectName(u"UpdateRoleButton")
        self.UpdateRoleButton.setGeometry(QRect(200, 370, 151, 61))
        self.ExpirePasswordButton = QPushButton(Form)
        self.ExpirePasswordButton.setObjectName(u"ExpirePasswordButton")
        self.ExpirePasswordButton.setGeometry(QRect(360, 370, 151, 61))
        self.operationResult = QPlainTextEdit(Form)
        self.operationResult.setObjectName(u"operationResult")
        self.operationResult.setEnabled(False)
        self.operationResult.setGeometry(QRect(30, 30, 471, 91))
        self.userLabel = QLabel(Form)
        self.userLabel.setObjectName(u"userLabel")
        self.userLabel.setGeometry(QRect(30, 150, 141, 31))

        self.currentRoleLabel = QLabel(Form)
        self.currentRoleLabel.setObjectName(u"currentRoleLabel")
        self.currentRoleLabel.setGeometry(QRect(30, 220, 141, 31))
        
        self.newRoleLabel = QLabel(Form)
        self.newRoleLabel.setObjectName(u"newRoleLabel")
        self.newRoleLabel.setGeometry(QRect(30, 290, 141, 31))

        self.dataProvider = DatabaseOperations()
        self.NamesBox.addItems(self.dataProvider.getUserNames(self.userId))
        self.NewRoleEdit.addItems(self.dataProvider.getRoleNames())
        self.RoleEdit.setText(self.dataProvider.getRoleName(self.NamesBox.currentText()))

        self.NamesBox.currentIndexChanged.connect(self.getUserData)
        self.DeleteUserButton.clicked.connect(self.deleteUser)
        self.ExpirePasswordButton.clicked.connect(self.expirePassword)
        self.UpdateRoleButton.clicked.connect(self.updateRole)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.RoleEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Role", None))
        self.NewRoleEdit.setPlaceholderText(QCoreApplication.translate("Form", u"New Role", None))
        self.DeleteUserButton.setText(QCoreApplication.translate("Form", u"Delete user", None))
        self.UpdateRoleButton.setText(QCoreApplication.translate("Form", u"Update Role", None))
        self.ExpirePasswordButton.setText(QCoreApplication.translate("Form", u"Expire password", None))

        self.operationResult.setPlainText("")
        self.userLabel.setText(QCoreApplication.translate("Form", u"User", None))
        self.currentRoleLabel.setText(QCoreApplication.translate("Form", u"Current role", None))
        self.newRoleLabel.setText(QCoreApplication.translate("Form", u"New role", None))
    # retranslateUi

    def getUserData(self):
        self.RoleEdit.setText(self.dataProvider.getRoleName(self.NamesBox.currentText()))

    def deleteUser(self):
        result = self.dataProvider.deleteUser(self.NamesBox.currentText(), self.userId)
        if not result:
            self.NamesBox.removeItem(self.NamesBox.currentIndex())
            self.operationResult.setPlainText("User deleted successfully")
        else:
            self.operationResult.setPlainText("Cannot delete another admin user")

    def expirePassword(self):
        self.dataProvider.expirePassword(self.NamesBox.currentText())
        self.operationResult.setPlainText("Password expired!")

    def updateRole(self):
        self.dataProvider.updateRole(self.NamesBox.currentText(), self.NewRoleEdit.currentText())
        self.RoleEdit.setText(self.dataProvider.getRoleName(self.NamesBox.currentText()))
        self.operationResult.setPlainText("Role updated")
