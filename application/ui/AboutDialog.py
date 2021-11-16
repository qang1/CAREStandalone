from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ui.ui_about import Ui_Dialog
from main import __version__

class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent=parent)
        self.ui = Ui_Dialog()
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint
            )
        self.ui.setupUi(self)
        self.ui.label_version.setText(__version__)
        
