# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1504, 883)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../iCloudDrive/FYP/Logo/clinical-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1501, 861))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.tabWidget.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet("QTabBar::tab { height: 35px;width:150px;font: 9.5pt \"MS Shell Dlg 2\";}")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label_1 = QtWidgets.QLabel(self.tab)
        self.label_1.setGeometry(QtCore.QRect(10, 30, 201, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_1.setFont(font)
        self.label_1.setObjectName("label_1")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(290, 10, 271, 221))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 30, 251, 181))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_pat_no = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_pat_no.setFont(font)
        self.label_pat_no.setText("")
        self.label_pat_no.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_pat_no.setObjectName("label_pat_no")
        self.gridLayout.addWidget(self.label_pat_no, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.label_date = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_date.setFont(font)
        self.label_date.setText("")
        self.label_date.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_date.setObjectName("label_date")
        self.gridLayout.addWidget(self.label_date, 1, 1, 1, 1)
        self.label_hour = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_hour.setFont(font)
        self.label_hour.setText("")
        self.label_hour.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_hour.setObjectName("label_hour")
        self.gridLayout.addWidget(self.label_hour, 2, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_14.setMinimumSize(QtCore.QSize(146, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 3, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.label_breath_no = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_breath_no.setFont(font)
        self.label_breath_no.setText("")
        self.label_breath_no.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_breath_no.setObjectName("label_breath_no")
        self.gridLayout.addWidget(self.label_breath_no, 3, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 4, 0, 1, 1)
        self.label_AI = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_AI.setFont(font)
        self.label_AI.setText("")
        self.label_AI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_AI.setObjectName("label_AI")
        self.gridLayout.addWidget(self.label_AI, 4, 1, 1, 1)
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tab)
        self.tabWidget_2.setGeometry(QtCore.QRect(0, 270, 1461, 521))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget_2.setFont(font)
        self.tabWidget_2.setStyleSheet("QTabBar::tab { height: 40px;width:210px;font: 12pt \"MS Shell Dlg 2\";}\n"
"")
        self.tabWidget_2.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setStyleSheet("")
        self.tab_3.setObjectName("tab_3")
        self.graphWidget = MplWidget(self.tab_3)
        self.graphWidget.setGeometry(QtCore.QRect(0, 10, 1451, 461))
        self.graphWidget.setObjectName("graphWidget")
        self.tabWidget_2.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setStyleSheet("")
        self.tab_4.setObjectName("tab_4")
        self.boxGraphWidget = MplWidget2(self.tab_4)
        self.boxGraphWidget.setGeometry(QtCore.QRect(0, 10, 1451, 461))
        self.boxGraphWidget.setObjectName("boxGraphWidget")
        self.tabWidget_2.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.pieGraphWidget = MplWidget4(self.tab_5)
        self.pieGraphWidget.setGeometry(QtCore.QRect(620, 10, 831, 461))
        self.pieGraphWidget.setObjectName("pieGraphWidget")
        self.label_2 = QtWidgets.QLabel(self.tab_5)
        self.label_2.setGeometry(QtCore.QRect(30, 30, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.tab_5)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(30, 70, 421, 291))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_12 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 4, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.norm_breath_label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.norm_breath_label.setFont(font)
        self.norm_breath_label.setText("")
        self.norm_breath_label.setObjectName("norm_breath_label")
        self.gridLayout_2.addWidget(self.norm_breath_label, 1, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 2, 0, 1, 1)
        self.asyn_breath_label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.asyn_breath_label.setFont(font)
        self.asyn_breath_label.setText("")
        self.asyn_breath_label.setObjectName("asyn_breath_label")
        self.gridLayout_2.addWidget(self.asyn_breath_label, 2, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 3, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)
        self.total_breath_label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.total_breath_label.setFont(font)
        self.total_breath_label.setText("")
        self.total_breath_label.setObjectName("total_breath_label")
        self.gridLayout_2.addWidget(self.total_breath_label, 3, 1, 1, 1)
        self.ai_breath_label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.ai_breath_label.setFont(font)
        self.ai_breath_label.setText("")
        self.ai_breath_label.setObjectName("ai_breath_label")
        self.gridLayout_2.addWidget(self.ai_breath_label, 4, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.tab_5)
        self.line.setGeometry(QtCore.QRect(30, 100, 431, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.line.setFont(font)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.tab_5)
        self.line_2.setGeometry(QtCore.QRect(30, 300, 431, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.tabWidget_2.addTab(self.tab_5, "")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_5.setGeometry(QtCore.QRect(570, 10, 921, 221))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_5.setFont(font)
        self.groupBox_5.setObjectName("groupBox_5")
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox_5)
        self.tableWidget.setGeometry(QtCore.QRect(10, 20, 901, 191))
        self.tableWidget.setStyleSheet("QHeaderView::section{Background-color:rgb(246,246,246);\n"
"                                   border-radius:1px;}\n"
"QTableWidget QTableCornerButton::section {Background-color:rgb(246,246,246);}")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(2, 1, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(128)
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.tab)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(10, 60, 271, 123))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.btn_reset = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btn_reset.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_reset.sizePolicy().hasHeightForWidth())
        self.btn_reset.setSizePolicy(sizePolicy)
        self.btn_reset.setBaseSize(QtCore.QSize(0, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(216, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(223, 164, 168))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(223, 164, 168))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(223, 164, 168))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.btn_reset.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setBold(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.btn_reset.setFont(font)
        self.btn_reset.setStyleSheet("QPushButton {\n"
"    background-color: rgb(216, 0, 0);\n"
"    color:white;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: rgb(216, 0, 0);\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    font-weight:normal;\n"
"    text-decoration:none;\n"
"   \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #dfa4a8;\n"
"    border-color: #dfa4a8;\n"
"    color:white;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#ff7357;\n"
"    border-radius:3px;\n"
"    border:1px solid #ff7357;\n"
"    border-color: #fc2e05;\n"
"    color: black;\n"
"}")
        self.btn_reset.setObjectName("btn_reset")
        self.gridLayout_3.addWidget(self.btn_reset, 2, 1, 1, 1)
        self.btn_export = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btn_export.setEnabled(False)
        self.btn_export.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_export.setFont(font)
        self.btn_export.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"   \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_export.setObjectName("btn_export")
        self.gridLayout_3.addWidget(self.btn_export, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 2)
        self.btn_start = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_start.sizePolicy().hasHeightForWidth())
        self.btn_start.setSizePolicy(sizePolicy)
        self.btn_start.setMinimumSize(QtCore.QSize(0, 35))
        self.btn_start.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_start.setFont(font)
        self.btn_start.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"   \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-radius:3px;\n"
"    border:1px solid #c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_start.setObjectName("btn_start")
        self.gridLayout_3.addWidget(self.btn_start, 0, 0, 1, 1)
        self.btn_openFDialog = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btn_openFDialog.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_openFDialog.sizePolicy().hasHeightForWidth())
        self.btn_openFDialog.setSizePolicy(sizePolicy)
        self.btn_openFDialog.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_openFDialog.setFont(font)
        self.btn_openFDialog.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"    \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-radius:3px;\n"
"    border:1px solid #c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_openFDialog.setObjectName("btn_openFDialog")
        self.gridLayout_3.addWidget(self.btn_openFDialog, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 271, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget_3 = QtWidgets.QTabWidget(self.tab_2)
        self.tabWidget_3.setGeometry(QtCore.QRect(10, 280, 1481, 531))
        self.tabWidget_3.setToolTip("")
        self.tabWidget_3.setStyleSheet("QTabBar::tab { height: 40px;width:150px;font: 12pt \"MS Shell Dlg 2\";}\n"
"")
        self.tabWidget_3.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget_3.setObjectName("tabWidget_3")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.poErsWidget = MplWidget3(self.tab_6)
        self.poErsWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poErsWidget.setObjectName("poErsWidget")
        self.tabWidget_3.addTab(self.tab_6, "")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.poRrsWidget = MplWidget3(self.tab_7)
        self.poRrsWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poRrsWidget.setObjectName("poRrsWidget")
        self.tabWidget_3.addTab(self.tab_7, "")
        self.tab_8 = QtWidgets.QWidget()
        self.tab_8.setObjectName("tab_8")
        self.poPEEPWidget = MplWidget3(self.tab_8)
        self.poPEEPWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poPEEPWidget.setObjectName("poPEEPWidget")
        self.tabWidget_3.addTab(self.tab_8, "")
        self.tab_9 = QtWidgets.QWidget()
        self.tab_9.setObjectName("tab_9")
        self.poPIPWidget = MplWidget3(self.tab_9)
        self.poPIPWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poPIPWidget.setObjectName("poPIPWidget")
        self.tabWidget_3.addTab(self.tab_9, "")
        self.tab_10 = QtWidgets.QWidget()
        self.tab_10.setObjectName("tab_10")
        self.poVtWidget = MplWidget3(self.tab_10)
        self.poVtWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poVtWidget.setObjectName("poVtWidget")
        self.tabWidget_3.addTab(self.tab_10, "")
        self.tab_11 = QtWidgets.QWidget()
        self.tab_11.setObjectName("tab_11")
        self.poDpWidget = MplWidget3(self.tab_11)
        self.poDpWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poDpWidget.setObjectName("poDpWidget")
        self.tabWidget_3.addTab(self.tab_11, "")
        self.tab_12 = QtWidgets.QWidget()
        self.tab_12.setObjectName("tab_12")
        self.poAIWidget = MplWidget3(self.tab_12)
        self.poAIWidget.setGeometry(QtCore.QRect(10, 10, 1461, 461))
        self.poAIWidget.setObjectName("poAIWidget")
        self.tabWidget_3.addTab(self.tab_12, "")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 100, 331, 161))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.groupBox_2)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 20, 311, 135))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.formLayout = QtWidgets.QFormLayout(self.gridLayoutWidget_3)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_PO_p_no = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_PO_p_no.setFont(font)
        self.label_PO_p_no.setText("")
        self.label_PO_p_no.setObjectName("label_PO_p_no")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_PO_p_no)
        self.label_17 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_17)
        self.label_PO_date = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_PO_date.setFont(font)
        self.label_PO_date.setText("")
        self.label_PO_date.setObjectName("label_PO_date")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_PO_date)
        self.label_18 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_18)
        self.label_t_hours = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_t_hours.setFont(font)
        self.label_t_hours.setText("")
        self.label_t_hours.setObjectName("label_t_hours")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_t_hours)
        self.label_19 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_19)
        self.label_PO_bCount = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_PO_bCount.setFont(font)
        self.label_PO_bCount.setText("")
        self.label_PO_bCount.setObjectName("label_PO_bCount")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_PO_bCount)
        self.label_23 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_23)
        self.label_PO_AI = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_PO_AI.setFont(font)
        self.label_PO_AI.setText("")
        self.label_PO_AI.setObjectName("label_PO_AI")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.label_PO_AI)
        self.label_15 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_15)
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 10, 561, 81))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setGeometry(QtCore.QRect(10, 20, 171, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.lineEdit_dir = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_dir.setGeometry(QtCore.QRect(10, 40, 401, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_dir.setFont(font)
        self.lineEdit_dir.setObjectName("lineEdit_dir")
        self.btn_openDirDialog = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_openDirDialog.setGeometry(QtCore.QRect(420, 40, 133, 33))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_openDirDialog.setFont(font)
        self.btn_openDirDialog.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"    \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-radius:3px;\n"
"    border:1px solid #c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_openDirDialog.setObjectName("btn_openDirDialog")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_4.setGeometry(QtCore.QRect(580, 10, 911, 251))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.groupBox_4)
        self.tableWidget_2.setGeometry(QtCore.QRect(10, 20, 891, 221))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableWidget_2.setFont(font)
        self.tableWidget_2.setAutoFillBackground(False)
        self.tableWidget_2.setStyleSheet("QHeaderView::section{Background-color:rgb(246,246,246);\n"
"                                   border-radius:1px;}\n"
"QTableWidget QTableCornerButton::section {Background-color:rgb(246,246,246);}")
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(6)
        self.tableWidget_2.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.tableWidget_2.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget_2.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(15)
        item.setFont(font)
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget_2.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget_2.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget_2.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget_2.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget_2.setItem(2, 1, item)
        self.tableWidget_2.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(126)
        self.tableWidget_2.horizontalHeader().setMinimumSectionSize(45)
        self.tableWidget_2.verticalHeader().setDefaultSectionSize(38)
        self.tableWidget_2.verticalHeader().setSortIndicatorShown(False)
        self.tableWidget_2.verticalHeader().setStretchLastSection(False)
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_6.setGeometry(QtCore.QRect(350, 100, 221, 161))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_6.setFont(font)
        self.groupBox_6.setObjectName("groupBox_6")
        self.btn_startBatchPros = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_startBatchPros.setEnabled(False)
        self.btn_startBatchPros.setGeometry(QtCore.QRect(10, 30, 201, 41))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_startBatchPros.setFont(font)
        self.btn_startBatchPros.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"    \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-radius:3px;\n"
"    border:1px solid #c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_startBatchPros.setObjectName("btn_startBatchPros")
        self.btn_PO_reset = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_PO_reset.setEnabled(False)
        self.btn_PO_reset.setGeometry(QtCore.QRect(10, 80, 101, 31))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_PO_reset.setFont(font)
        self.btn_PO_reset.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"    \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-radius:3px;\n"
"    border:1px solid #c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_PO_reset.setObjectName("btn_PO_reset")
        self.btn_PO_export = QtWidgets.QPushButton(self.groupBox_6)
        self.btn_PO_export.setEnabled(False)
        self.btn_PO_export.setGeometry(QtCore.QRect(120, 80, 91, 31))
        font = QtGui.QFont()
        font.setFamily("arial")
        font.setPointSize(-1)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.btn_PO_export.setFont(font)
        self.btn_PO_export.setStyleSheet("QPushButton {\n"
"    background-color: #e0e0e0;\n"
"    color:black;\n"
"    border-radius:3px;\n"
"    border:1px solid #faebeb;\n"
"    border-color: #969696;\n"
"    font-family:arial;\n"
"    font-size:16px;\n"
"    text-decoration:none;\n"
"    \n"
"}\n"
"QPushButton:disabled {\n"
"    background-color:#c7c7c7;\n"
"    border-radius:3px;\n"
"    border:1px solid #c7c7c7;\n"
"    border-color: #c7c7c7;\n"
"    color: #7d7d7d;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color:#d4e9fa;\n"
"    border-radius:3px;\n"
"    border:1px solid #d4e9fa;\n"
"    border-color: #003cff;\n"
"    color: black;\n"
"}")
        self.btn_PO_export.setObjectName("btn_PO_export")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1504, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.statusBar.setFont(font)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(0)
        self.actionExit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CARENet Standalone"))
        self.label_1.setText(_translate("MainWindow", "Input must be text file."))
        self.groupBox.setTitle(_translate("MainWindow", "Infomation"))
        self.label_4.setText(_translate("MainWindow", "Patient No:"))
        self.label_6.setText(_translate("MainWindow", "Date:"))
        self.label_14.setText(_translate("MainWindow", "Number of breath:"))
        self.label_8.setText(_translate("MainWindow", "Hour:"))
        self.label_10.setText(_translate("MainWindow", "Asynchrony Index:"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("MainWindow", "Line Plot"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("MainWindow", "Box-Whisker Plot"))
        self.label_2.setText(_translate("MainWindow", "Results:"))
        self.label_12.setText(_translate("MainWindow", "Asynchrony Index (AI):"))
        self.label_3.setText(_translate("MainWindow", "Breath type"))
        self.label_9.setText(_translate("MainWindow", "Asynchrony breath:"))
        self.label_11.setText(_translate("MainWindow", "Total:"))
        self.label_7.setText(_translate("MainWindow", "Normal breath:"))
        self.label_5.setText(_translate("MainWindow", "Count"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_5), _translate("MainWindow", "Asynchrony Analysis"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Respiratory Mechanics"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", " Min"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", " Median [IQR]"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", " Max"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Ers"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Rrs"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "PEEP"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "PIP"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "VT"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "PIP-PEEP"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.btn_reset.setText(_translate("MainWindow", "Reset"))
        self.btn_export.setText(_translate("MainWindow", "Export"))
        self.btn_start.setText(_translate("MainWindow", "Load Example"))
        self.btn_openFDialog.setText(_translate("MainWindow", "Choose File"))
        self.label.setText(_translate("MainWindow", "Start (Choose 1 of 2 options):"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Data History"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_6), _translate("MainWindow", "Ers"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_6), _translate("MainWindow", "Elastance"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_7), _translate("MainWindow", "Rrs"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_7), _translate("MainWindow", "Resistance"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_8), _translate("MainWindow", "PEEP"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_8), _translate("MainWindow", "Positive End-Expiratory Pressure"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_9), _translate("MainWindow", "PIP"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_9), _translate("MainWindow", "Peak Inspiratory Pressure"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_10), _translate("MainWindow", "Vt"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_10), _translate("MainWindow", "Tidal Volume"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_11), _translate("MainWindow", "PIP-PEEP"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_11), _translate("MainWindow", "Inspiratory Pressure Range"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_12), _translate("MainWindow", "AI"))
        self.tabWidget_3.setTabToolTip(self.tabWidget_3.indexOf(self.tab_12), _translate("MainWindow", "Asynchrony Index"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Information"))
        self.label_17.setText(_translate("MainWindow", "Date:"))
        self.label_18.setText(_translate("MainWindow", "Total hours:"))
        self.label_19.setText(_translate("MainWindow", "Breath count:"))
        self.label_23.setText(_translate("MainWindow", "Asynchrony Index:"))
        self.label_15.setText(_translate("MainWindow", "Patient:"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Open directory"))
        self.label_13.setText(_translate("MainWindow", "Locate date to analyse"))
        self.btn_openDirDialog.setText(_translate("MainWindow", "Choose Directory"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Respiratory Mechanics"))
        item = self.tableWidget_2.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", " Min"))
        item = self.tableWidget_2.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", " Median [IQR]"))
        item = self.tableWidget_2.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", " Max"))
        item = self.tableWidget_2.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Ers"))
        item = self.tableWidget_2.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Rrs"))
        item = self.tableWidget_2.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "PEEP"))
        item = self.tableWidget_2.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "PIP"))
        item = self.tableWidget_2.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "VT"))
        item = self.tableWidget_2.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "PIP-PEEP"))
        __sortingEnabled = self.tableWidget_2.isSortingEnabled()
        self.tableWidget_2.setSortingEnabled(False)
        self.tableWidget_2.setSortingEnabled(__sortingEnabled)
        self.groupBox_6.setTitle(_translate("MainWindow", "Controls"))
        self.btn_startBatchPros.setText(_translate("MainWindow", "Start"))
        self.btn_PO_reset.setText(_translate("MainWindow", "Reset"))
        self.btn_PO_export.setText(_translate("MainWindow", "Export"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Patient Overview"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))

from ui.mplwidget import MplWidget, MplWidget2, MplWidget3, MplWidget4
