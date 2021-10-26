# =============================================================================
# Standard library imports
# =============================================================================
import os
import sys
import logging.config

#==============================================================================
# Set Environment variables
#==============================================================================
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ["KERAS_BACKEND"] = "tensorflow"

#==============================================================================
# Third-party imports
#==============================================================================
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen 
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt

#==============================================================================
# Setup Logging
#==============================================================================
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'logs/logging.conf')
logging.config.fileConfig(fname=log_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

#==============================================================================
# Setup System Variables
#==============================================================================
__author__ = 'Qing Arn Ng'
# QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) # enable highdpi scaling
# sys.path.insert(1, '/application')

def flashSplash():
    
    # Create and display the splash screen
    splash_pix = QPixmap('ui/splash.png')

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    # splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    # By default, SplashScreen will be in the center of the screen.
    # You can move it to a specific location if you want:
    # splash.move(10,10)

    splash.show()

    # Close SplashScreen after 2 seconds (2000 ms)
    # QTimer.singleShot(2000, splash.close)
    return splash

def db_handle():
    db = QSqlDatabase.addDatabase("QSQLITE", connectionName="dbb")
    db.setDatabaseName("data.sqlite")
    dbName = db.databaseName()
    conName = db.connectionName()
    if not db.open():
        logger.error("Unable to connect to the database")
        QMessageBox.critical(None, ("Cannot open database"),
                                   ("Unable to establish a database connection.\n"
                                    "This program needs SQLite support. Please read "
                                    "the Qt SQL driver documentation for information "
                                    "how to build it.\n\n"
                                    "Click Cancel to exit."),
                    QMessageBox.Cancel)
        sys.exit(1)
    return db


def main():
    app = QApplication(sys.argv)
    splash = flashSplash()
    logger.info('Program start up')
    app.setOrganizationName("CARENet")
    app.setOrganizationDomain("caresoft.live")
    app.setApplicationName("CARENet Standalone")
    db = db_handle()
    # ==============================================================================
    # Local application imports
    # ==============================================================================
    from ui.mainwindow import MainWindow
    from models.query import createTable
    createTable(db)
    window = MainWindow(db)
    window.setWindowIcon(QIcon('ui/logo.png'))
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

