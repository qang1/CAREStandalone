from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QPushButton, QVBoxLayout
if __name__ == '__main__':
    from ui_settings import Ui_SettingsDialog
else:
    from ui.ui_settings import Ui_SettingsDialog

from PyQt5.QtWidgets import QApplication, QWidget, QDialog
import sys
import logging

# Get the logger specified in the file
logger = logging.getLogger(__name__)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setWindowTitle("Widget")
        layout = QVBoxLayout(self)
        btn1 = QPushButton("Open Settings")
        # btn1.setText('btn')
        layout.addWidget(btn1)
        btn1.clicked.connect(self.show_about_dialog)

    

    def show_about_dialog(self):
        sd = SettingsDialog(self)
        sd.show()
        if sd.settings.value('resolution') == '30mins':
            sd.ui.radioButton.setChecked(True)

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent=parent)
        self.ui = Ui_SettingsDialog()
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint
            )
        self.ui.setupUi(self)
        # self.settings = QSettings("My Organization", "My Application")
        self.settings = QSettings()
        # self.settings.value('saveDB',True, type=bool)
        self.initUI()

    def initUI(self):
        # Initialize UI with saved settings from QSettings 
        if self.settings.value('resolution') == '30mins':
            self.ui.plotRes30min.setChecked(True)
        elif self.settings.value('resolution') == '1hour':
            self.ui.plotRes1hour.setChecked(True)

        if self.settings.value('saveDB', True, type=bool) == True:
            self.ui.saveDBTrue.setChecked(True)
        else:
            self.ui.saveDBFalse.setChecked(True)
        
        
    def saveSettings(self,key,value):
        self.settings.setValue(key,value)
    
    def accept(self):
        
        if self.ui.plotRes30min.isChecked():
            logger.info(f'Plot resolution set: 30mins')
            self.settings.setValue('resolution','30mins')
        else:
            logger.info(f'Plot resolution set: 1hour')
            self.settings.setValue('resolution','1hour')

        if self.ui.saveDBTrue.isChecked():
            logger.info(f'Save DB set: True')
            self.settings.setValue('saveDB',True)
        else:
            logger.info(f'Save DB set: False')
            self.settings.setValue('saveDB',False)
        self.close()

# Tests
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
        
