from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QComboBox, QDateEdit, QCheckBox
from operations.databaseOperations import DatabaseOperations
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PyQt5.QtGui import QPixmap, QImage
import numpy

class Ui_StatisticsWindow(QWidget):
    def setupUi(self, StatisticsWindow):
        if not StatisticsWindow.objectName():
            StatisticsWindow.setObjectName(u"StatisticsWindow")
        StatisticsWindow.resize(958, 800)
        StatisticsWindow.setStyleSheet(u"background-color: rgb(8, 8, 8);")
        self.statisticsView = QLabel(StatisticsWindow)
        self.statisticsView.setObjectName(u"statisticsView")
        self.statisticsView.setGeometry(QtCore.QRect(20, 20, 921, 600))
        self.statisticsView.setStyleSheet(u"background-color: rgb(0, 0, 75);")
        self.comboBox = QComboBox(StatisticsWindow)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QtCore.QRect(630, 630, 301, 61))
        self.comboBox.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.statisticsButton = QPushButton(StatisticsWindow)
        self.statisticsButton.setObjectName(u"statisticsButton")
        self.statisticsButton.setGeometry(QtCore.QRect(450, 630, 161, 61))
        self.statisticsButton.setStyleSheet(u"font: 10pt \"Tilt Neon\"; background-color: rgb(255, 255, 255); border-radius: 8px;")
        icon = QtGui.QIcon()
        icon.addFile(u"images/Graph Report Script.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.statisticsButton.setIcon(icon)
        self.statisticsButton.setIconSize(QtCore.QSize(36, 36))
        self.fromDate = QDateEdit(StatisticsWindow)
        self.fromDate.setObjectName(u"fromDate")
        self.fromDate.setGeometry(QtCore.QRect(70, 630, 110, 22))
        self.fromDate.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.toDate = QDateEdit(StatisticsWindow)
        self.toDate.setObjectName(u"toDate")
        self.toDate.setGeometry(QtCore.QRect(250, 630, 110, 22))
        self.toDate.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.label = QLabel(StatisticsWindow)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QtCore.QRect(10, 630, 55, 16))
        self.label.setStyleSheet(u"font: 10pt \"Tilt Neon\";color: rgb(255, 255, 255);")
        self.label_2 = QLabel(StatisticsWindow)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QtCore.QRect(210, 630, 35, 16))
        self.label_2.setStyleSheet(u"font: 10pt \"Tilt Neon\";color: rgb(255, 255, 255);")
        self.useDateCheckBox = QCheckBox(StatisticsWindow)
        self.useDateCheckBox.setObjectName(u"useDateCheckBox")
        self.useDateCheckBox.setGeometry(QtCore.QRect(460, 730, 81, 20))
        self.useDateCheckBox.setStyleSheet(u"color: rgb(255, 255, 255); font: 8pt \"Tilt Neon\";")
        self.useDateCheckBox.setChecked(True)
        
        statisticsOperations = ["accidents", "average time"]

        self.comboBox.addItems(statisticsOperations)

        self.retranslateUi(StatisticsWindow)

        self.useDateCheckBox.toggled.connect(self.hideData)
        self.statisticsButton.clicked.connect(self.getStatistics)
        QtCore.QMetaObject.connectSlotsByName(StatisticsWindow)
        self.databaseProvider = DatabaseOperations()

        self.locationCombobox = QComboBox(StatisticsWindow)
        self.locationCombobox.setObjectName(u"locationCombobox")
        self.locationCombobox.setGeometry(QtCore.QRect(630, 720, 301, 61))
        self.locationCombobox.setStyleSheet(u"background-color: rgb(255, 255, 255);")

        self.locationCombobox.addItems(self.databaseProvider.getLocations())

    def retranslateUi(self, StatisticsWindow):
        StatisticsWindow.setWindowTitle(QtCore.QCoreApplication.translate("StatisticsWindow", u"Statistics", None))
        self.statisticsView.setText("")
        self.statisticsButton.setText(QtCore.QCoreApplication.translate("StatisticsWindow", u"Get statistic", None))
        self.label.setText(QtCore.QCoreApplication.translate("StatisticsWindow", u"From", None))
        self.label_2.setText(QtCore.QCoreApplication.translate("StatisticsWindow", u"To", None))
        self.useDateCheckBox.setText(QtCore.QCoreApplication.translate("StatisticsWindow", u"Use date", None))
    
    def hideData(self):
        if not self.useDateCheckBox.isChecked():
            self.label.hide()
            self.fromDate.hide()
            self.toDate.hide()
            self.label_2.hide()
        else:
            self.label.show()
            self.fromDate.show()
            self.toDate.show()
            self.label_2.show()

    def getStatistics(self):
        fromDate = None 
        toDate = None

        if self.useDateCheckBox.isChecked():
            fromDate_str = self.fromDate.date().toString('yyyy-MM-dd')
            toDate_str = self.toDate.date().toString('yyyy-MM-dd')

            fromDate = datetime.strptime(fromDate_str, '%Y-%m-%d')
            toDate = datetime.strptime(toDate_str, '%Y-%m-%d')
        
        result = []

        if self.comboBox.currentIndex() == 0:
            result = self.databaseProvider.getAccidentsForLocation(self.locationCombobox.currentText(), fromDate, toDate)
        #elif self.comboBox.currentIndex() == 1:
            #result = self.databaseProvider.getFalsePositivesForLocation(self.locationCombobox.currentText(), fromDate, toDate)
        elif self.comboBox.currentIndex() == 1:
            result = self.databaseProvider.getIncidentTimeReactionStatistics(self.locationCombobox.currentText(), fromDate, toDate)
        
        dates = []
        counts = []
        sendByCol = []

        for row in result:
            date = row[0]
            count = row[1]

            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except:
                if self.comboBox.currentIndex() != 1:
                    print(f"Issue with date value: {date}. Skipping this entry.")
                    continue
                else:
                    sendBy = row[2]
                    sendByCol.append(sendBy)

            dates.append(date)
            counts.append(count)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, counts, marker='o')
        if self.comboBox.currentIndex() == 0:
            ax.set_title('Amount of Accidents by Dates')
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Accidents')
        #elif self.comboBox.currentIndex() == 1:
           # ax.set_title('Amount of False positives by Dates')
           # ax.set_xlabel('Date')
           # ax.set_ylabel('Number of Accidents')
        elif self.comboBox.currentIndex() == 1:
            info_0 = [dates[i] for i in range(len(dates)) if sendByCol[i] == 0]
            info_1 = [dates[i] for i in range(len(dates)) if sendByCol[i] == 1]

            # Create y-values with the same length as the filtered info lists
            y_values_0 = [counts[i] for i in range(len(dates)) if sendByCol[i] == 0]
            y_values_1 = [counts[i] for i in range(len(dates)) if sendByCol[i] == 1]

            # Plot info_0 and info_1 with their respective y-values
            ax.plot(info_0, y_values_0, marker='o', label='send by mail', color='blue')
            ax.plot(info_1, y_values_1, marker='o', label='send by telegram', color='red')
            
            # Plot a horizontal line with y-value set to 10 for all info points
            y_values_constant = numpy.full(len(dates), 10)
            ax.plot(dates, y_values_constant, marker='o')
            y_values = numpy.full_like(dates, 10)
            ax.plot(dates, y_values, marker='o')

        ax.legend()
        ax.grid(True)

        canvas = FigureCanvas(fig)
        canvas.draw()
        width, height = fig.get_size_inches() * fig.get_dpi()
        width, height = int(width), int(height)
        image = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        
        label_width = self.statisticsView.width()
        label_height = self.statisticsView.height()
        scale_factor = min(label_width / width, label_height / height)

        # Resize the image while maintaining its aspect ratio
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = image.scaled(new_width, new_height)

        # Convert the QImage to a QPixmap
        pixmap = QPixmap.fromImage(image)

        self.statisticsView.setPixmap(pixmap)
