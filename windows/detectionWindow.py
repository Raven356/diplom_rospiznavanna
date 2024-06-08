from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QPushButton, QLabel, QWidget, QComboBox, QMenuBar, QStatusBar, QFileDialog, QApplication
from windows.ui_statisticsWindow import Ui_StatisticsWindow
from windows.adminForm import Ui_AdminForm
from operations.databaseOperations import DatabaseOperations
import cv2
from operations.videoWorker import VideoWorker

class Ui_DetectionWindow(QWidget):
    def setupUi(self, MainWindow, userId, isAdmin = False):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(958, 529)
        MainWindow.setStyleSheet(u"background-color: rgb(8, 8, 8);")

        self.userId = userId
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.videoPlayer = QLabel(self.centralwidget)
        self.videoPlayer.setObjectName(u"videoPlayer")
        self.videoPlayer.setGeometry(QtCore.QRect(30, 10, 901, 381))
        self.videoPlayer.setStyleSheet(u"background-color: rgb(0, 0, 75);")

        self.chooseFileButton = QPushButton(self.centralwidget)
        self.chooseFileButton.setObjectName(u"chooseFileButton")
        self.chooseFileButton.setGeometry(QtCore.QRect(590, 420, 161, 51))
        self.chooseFileButton.setStyleSheet(u"background-color: rgb(255, 255, 255); border-radius: 8px; font: 10pt \"Tilt Neon\";")

        icon = QtGui.QIcon()
        icon.addFile(u"images/Opened Folder.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.chooseFileButton.setIcon(icon)
        self.chooseFileButton.setIconSize(QtCore.QSize(36, 36))
        self.videoName = QLabel(self.centralwidget)
        self.videoName.setObjectName(u"videoName")
        self.videoName.setGeometry(QtCore.QRect(410, 430, 151, 32))
        self.videoName.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.locationBox = QComboBox(self.centralwidget)
        self.locationBox.setObjectName(u"locationBox")
        self.locationBox.setGeometry(QtCore.QRect(780, 430, 161, 32))
        self.locationBox.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.statisticsButton = QPushButton(self.centralwidget)
        self.statisticsButton.setObjectName(u"statisticsButton")
        self.statisticsButton.setGeometry(QtCore.QRect(20, 420, 171, 51))
        self.statisticsButton.clicked.connect(self.openStatisticsWindow)
        self.statisticsButton.setStyleSheet(u"background-color: rgb(255, 255, 255); border-radius: 8px; font: 10pt \"Tilt Neon\";")

        icon1 = QtGui.QIcon()
        icon1.addFile(u"images/Graph Report.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.statisticsButton.setIcon(icon1)
        self.statisticsButton.setIconSize(QtCore.QSize(36, 36))

        self.adminButton = QPushButton(self.centralwidget)
        self.adminButton.setObjectName(u"adminButton")
        self.adminButton.setEnabled(True)
        self.adminButton.setGeometry(QtCore.QRect(210, 420, 171, 51))
        self.adminButton.setStyleSheet(u"background-color: rgb(255, 255, 255); border-radius: 8px; font: 10pt \"Tilt Neon\";")
        self.adminButton.setIcon(icon1)
        self.adminButton.setIconSize(QtCore.QSize(36, 36))
        self.adminButton.setVisible(isAdmin)
        if isAdmin:
            self.adminButton.clicked.connect(self.openAdminForm)

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QtCore.QRect(0, 0, 958, 26))
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statisticsWindow = None
        self.adminForm = None

        self.chooseFileButton.clicked.connect(self.openFileDialog)

        self.capture = cv2.VideoCapture()
        self.videoWorker = VideoWorker()
        self.videoWorker.setup(userId)

        self.dataProvider = DatabaseOperations()
        self.locationBox.currentIndexChanged.connect(self.changedLocation)
        self.locationBox.addItems(self.dataProvider.getLocations()) 
        

        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def changedLocation(self):
        if self.locationBox.currentText() == "local":
            self.capture.release()
            self.capture = cv2.VideoCapture()
            self.chooseFileButton.setVisible(True)
        else:
            self.chooseFileButton.setVisible(False)
            self.capture = cv2.VideoCapture(0)
            self.playVideo()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.capture.release()
        return super().closeEvent(a0)
    
    def openAdminForm(self):
        self.adminForm = Ui_AdminForm()
        self.adminForm.setupUi(self.adminForm, self.userId)
        self.adminForm.show()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", u"AccidentDetection", None))
        self.videoPlayer.setText("")
        self.chooseFileButton.setText(QtCore.QCoreApplication.translate("MainWindow", u"Choose file", None))
        self.videoName.setText("")
        self.statisticsButton.setText(QtCore.QCoreApplication.translate("MainWindow", u"Go to statistics", None))
        self.adminButton.setText(QtCore.QCoreApplication.translate("MainWindow", u"Go to admin form", None))

    def openStatisticsWindow(self):
        self.statisticsWindow = Ui_StatisticsWindow()
        self.statisticsWindow.setupUi(self.statisticsWindow)
        self.statisticsWindow.show()

    def openFileDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self.centralwidget, "Choose Video File", "", "Video Files (*.mp4 *.avi *.mkv *.mpeg *.mpg *.mov)")
        if fileName:
            self.videoName.setText(fileName)
            self.playVideo(fileName)

    def playVideo(self, fileName = None):
        if fileName:
            self.capture.open(fileName)
        while self.capture.isOpened():
            ret, frame = self.capture.read()
            frame = self.videoWorker.detectAccidents(frame, self.locationBox.currentText())
            if ret:
                frame = cv2.resize(frame, (self.videoPlayer.width(), self.videoPlayer.height()))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                h, w, ch = frame.shape
                bytesPerLine = ch * w

                image = QtGui.QImage(frame.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(image)
                self.videoPlayer.setPixmap(pixmap)
                QApplication.processEvents()
            else:
                break
        self.capture.release()
