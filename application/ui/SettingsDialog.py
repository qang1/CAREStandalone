from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ui.ui_settings import Ui_SettingsDialog
from config import __version__

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
        
        
