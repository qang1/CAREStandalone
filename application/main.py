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
from PyQt5.QtCore import Qt, QThread

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
# sys.path.insert(1, '/application')



class ImportThread(QThread):
    '''Do import of main code within another thread.
    Main application runs when this is done
    '''

    def __init__(self,splash):
        QThread.__init__(self)
        self.splash = splash

    def run(self):
        """Local application pre-imports"""
        # ==============================================================================
        CAREApp.showSplashMsg(self,'Importing modules')
        from ui.mainwindow import MainWindow

        CAREApp.showSplashMsg(self,'Checking database')
        from models.query import createTable

        CAREApp.showSplashMsg(self,'Starting up')
        


class CAREApp(QApplication):

    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setOrganizationName("CARENet")
        self.setOrganizationDomain("caresoft.live")
        self.setApplicationName("CARENet Standalone")
        
        # enable highdpi scaling
        # self.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    def openMainWindow(self):
        """Open the main window with any loaded files."""
        from ui.mainwindow import MainWindow

        self.window = MainWindow(self.db)
        self.window.setWindowIcon(QIcon('ui/logo.png'))
        self.window.show()

    def startup(self):
        """Do startup."""
        logger.info('Program start up')

        # show the splash screen on normal start
        self.splash = self.makeSplash()
        
        # create thread to import large modules
        self.thread = ImportThread(self.splash)
        self.thread.finished.connect(self.slotStartApplication)
        self.thread.start()
        

    def slotStartApplication(self):
        """Start app, after modules imported."""
        from models.query import createTable

        self.db = self.db_handle()

        # standard start main window
        self.openMainWindow()

        # initialize/create db table entry
        createTable(self.db)

        # clear splash when startup done
        self.splash.finish(self.window)
        

    def makeSplash(self):
        """Create and display the splash screen"""
    
        splash_pix = QPixmap('ui/splash.png')

        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        # splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.setEnabled(False)

        # Set splash font size
        splash_font = splash.font()
        splash_font.setPixelSize(20)
        splash.setFont(splash_font)

        splash.showMessage("Initializing...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)

        splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        # QTimer.singleShot(2000, splash.close)
        return splash

    def showSplashMsg(self,msg):
        """Change text displayed on the splash screen"""
        self.splash.showMessage(msg +"...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)

    def db_handle(self):
        """Create and open database"""
        db = QSqlDatabase.addDatabase("QSQLITE", connectionName="dbb")
        db.setDatabaseName("CARETrialdata.sqlite")
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

def run():
    '''Run the main application.'''

    # start me up
    app = CAREApp()
    app.startup()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()


