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
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtSql import QSqlDatabase
import matplotlib.pyplot as plt
import matplotlib
# from keras import backend as K

#==============================================================================
# Setup Logging
#==============================================================================
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'logs/logging.conf')
logging.config.fileConfig(fname=log_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

#==============================================================================
# Local application imports
#==============================================================================
from ui.mainwindow import MainWindow
from models.query import createTable

# Setup imports
# set mpl figure font size and print current keras backend
matplotlib.use('Qt5Agg')
plt.rcParams.update({'font.size': 12})
# logger.info('Keras backend: '+K.backend())

__author__ = 'Qing Arn Ng'
# QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) # enable highdpi scaling
# sys.path.insert(1, '/application')

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
    logger.info('Program start up')
    app = QApplication(sys.argv)
    db = db_handle()
    createTable(db)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

