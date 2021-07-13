# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_settings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayoutWidget = QtWidgets.QWidget(SettingsDialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 371, 221))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plotRes30min = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.plotRes30min.setObjectName("plotRes30min")
        self.horizontalLayout.addWidget(self.plotRes30min)
        self.plotRes1hour = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.plotRes1hour.setObjectName("plotRes1hour")
        self.horizontalLayout.addWidget(self.plotRes1hour)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Settings"))
        self.label.setToolTip(_translate("SettingsDialog", "Select time resolution for daily overview plots"))
        self.label.setText(_translate("SettingsDialog", "Plot Resolution"))
        self.plotRes30min.setText(_translate("SettingsDialog", "30 minutes"))
        self.plotRes1hour.setText(_translate("SettingsDialog", "1 hour"))

