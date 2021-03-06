"""MainWindow

Returns:
    [type]: [description]
"""

# Standard library imports
from os.path import isfile, join
import csv
import os
import logging

# Third party imports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QHeaderView, QMessageBox
from PyQt5.QtCore import QSettings
from PyQt5.QtSql import QSqlQuery
import matplotlib.pyplot as plt

# Local application imports
from threads.worker import Worker
from threads.PostProcessor import PostProcessor
from ui.ui_main import Ui_MainWindow
from ui.AboutDialog import AboutDialog
from ui.SettingsDialog import SettingsDialog
from ui.pbar import PopUpProgressBar
from ui.stacked_pbar import StackedProgressBar


# Get the logger specified in the file
logger = logging.getLogger(__name__)

# set mpl figure font size and print current keras backend
plt.rcParams.update({'font.size': 12})

class MainWindow(QMainWindow):
    def __init__(self,db):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.about = AboutDialog(self)
        self.setsDlg = SettingsDialog(self)
        self.pbar = PopUpProgressBar(self)
        self.settings = self.setsDlg.settings
        self._connectSignals()
        self.db = db
        self._setTableHeader()
        self.ui.PO_tabWidget.setTabVisible(8,False)
        self.ui.PO_tabWidget.setTabVisible(9,False)

    
    def _setTableHeader(self):
        labels = ['Ers\n(cmH\u2082O/L)','Rrs\n(cmH\u2082Os/L)','PEEP\n(cmH\u2082O)','PIP\n(cmH\u2082O)','Vₜ\n(mL)','PIP-PEEP\n(cmH\u2082O)']
        for i in range(len(labels)):
            self.ui.tableWidget.horizontalHeaderItem(i).setText(labels[i])
            self.ui.tableWidget_2.horizontalHeaderItem(i).setText(labels[i])

    def _openFileNameDialog(self):
        self.ui.btn_openFDialog.setEnabled(False)
        self.ui.btn_export.setEnabled(False)
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"Locate raw data file to analyze...", "","Text Files (*.txt)", options=options)
        if fileName:
            self.fname = fileName
            self._listFileDetails(fileName)
            self.start_thread()
        else:
            self.ui.btn_openFDialog.setEnabled(True)  # Re-enable choose btn if user cancel on file selection dialog

    
    def _openFileDirectory(self):

        dirSelected = str(QFileDialog.getExistingDirectory(self, "Locate directory to analyze...",str(QSettings().value('DEFAULT_DIR'))))
        if dirSelected != "":
            QSettings().setValue('DEFAULT_DIR',dirSelected)
            self.ui.lineEdit_dir.setText(dirSelected)
            logger.info(f'Directory selected: {dirSelected}')
            self.dirSelected = dirSelected
            self.ui.btn_startBatchPros.setEnabled(True)

    def _startBatchPros(self):
        # get all files in dirSelected
        files = [f for f in os.listdir(self.dirSelected) if isfile(join(self.dirSelected, f))]
        files_filtered = [f for f in files if f.endswith('.txt')]
        files_filtered = [f for f in files_filtered if f.startswith('patient')]
        files_filtered = [f for f in files_filtered if os.path.getsize(join(self.dirSelected, f)) > 0]
        
        logger.info(f'files sanitised: {files_filtered}')

        # if fileList is not empty
        if len(files_filtered) != 0:
            self.postP = PostProcessor(fname=files_filtered,dirSelected=self.dirSelected,db=self.db,ui=self.ui)
            self.postP_thread = QtCore.QThread()
            self.postP.moveToThread(self.postP_thread)
            self.postP_thread.started.connect(self.postP.run)
            self.postP_thread.start()
            self.postP.open_pbar.connect(self._openStackedPbar)
            self.postP.hide_pbar.connect(self._hideStackedPbar)
            self.postP.update_subpbar.connect(self._updateStackedPbar)
            self.postP.update_mainpbar.connect(self._updateMainStackedPbar)
            self.postP.processResMulti.connect(self._processRes)
            self.postP.finished.connect(self.postP_thread.quit)
            self.ui.btn_startBatchPros.setEnabled(False)
        else:
            logger.error('Cannot open folder. Number of files in folder is zero.')
            QMessageBox.critical(None, ("Cannot open folder"),
                                   ("Unable to read files from folder.\n"
                                    "Please ensure folder selected only containes correctly formatted data. "
                                    "Only text files are allowed. "
                                    "Please refer to the CARENet documentation for more information.\n\n"
                                    "Click Cancel to exit."),
                    QMessageBox.Cancel)

    def _processRes(self,res):
        # update ui 
        logger.info('_processRes(): Processing completed.')
        self.ui.statusBar.showMessage("Processing completed.")
        self.ui.btn_PO_reset.setEnabled(True)
        self.ui.btn_PO_export.setEnabled(True)
        self.ui.label_PO_p_no.setText(res['p_no'])
        self.ui.label_PO_date.setText(res['date'])
        if self.settings.value('resolution') == '30mins':
            hours_cnt = int(len(res['hours'])/2)
        else:
            hours_cnt = int(len(res['hours']))
        self.ui.label_t_hours.setText(str(hours_cnt))
        self.ui.label_PO_bCount.setText(str(sum(res['b_count'])))

        # resize table widget (can't be done on thread for some reasons)
        self.ui.tableWidget_2.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def _listFileDetails(self,fullFileName):
        fname = fullFileName.split('/')[-1].replace('.txt','')
        self.ui.label_pat_no.setText(fname.split('_')[1])
        self.ui.label_date.setText(fname.split('_')[2])
        self.ui.label_hour.setText(fname.split('_')[3])
        self.hour = fname.split('_')[3]
    
    def _resetScreen(self):
        self.ui.graphWidget.canvas.ax.cla()
        self.ui.boxGraphWidget.canvas.ax1.cla()
        self.ui.boxGraphWidget.canvas.ax2.cla()
        self.ui.boxGraphWidget.canvas.ax3.cla()
        self.ui.boxGraphWidget.canvas.ax4.cla()
        self.ui.boxGraphWidget.canvas.ax5.cla()
        self.ui.boxGraphWidget.canvas.ax6.cla()
        self.ui.pieGraphWidget.canvas.ax.cla()
        self.ui.AMBoxWidget.canvas.ax.cla()
        self.ui.graphWidget.canvas.draw()
        self.ui.boxGraphWidget.canvas.draw()
        self.ui.pieGraphWidget.canvas.draw()
        self.ui.AMBoxWidget.canvas.draw()
        self.ui.tableWidget.clearContents()
        self.ui.statusBar.showMessage("Screen refreshed")
        self.ui.btn_openFDialog.setEnabled(True)
        self.ui.btn_reset.setEnabled(False)
        self.ui.btn_export.setEnabled(False)
        self.ui.label_AI.setText('')
        self.ui.label_breath_no.setText('')
        self.ui.label_date.setText('')
        self.ui.label_hour.setText('')
        self.ui.label_pat_no.setText('')
        self.ui.norm_breath_label.setText('')
        self.ui.asyn_breath_label.setText('')
        self.ui.total_breath_label.setText('')
        self.ui.ai_breath_label.setText('')

    def _resetPO(self):
        # Clear plots
        plots = [self.ui.poErsWidget.canvas, self.ui.poRrsWidget.canvas, self.ui.poPIPWidget.canvas,
                self.ui.poPEEPWidget.canvas, self.ui.poVtWidget.canvas, self.ui.poDpWidget.canvas,
                self.ui.poAIWidget.canvas, self.ui.poAMWidget.canvas, self.ui.poAMWidget_2.canvas,
                self.ui.poAMWidget_3.canvas]
        for i in range(len(plots)):
            plots[i].ax.cla()
            plots[i].draw()
     
        self.ui.label_PO_p_no.setText('')
        self.ui.label_PO_date.setText('')
        self.ui.label_t_hours.setText('')
        self.ui.label_PO_bCount.setText('')
        self.ui.label_PO_AI.setText('')
        self.ui.lineEdit_dir.setText('')
        self.ui.tableWidget_2.clearContents()
        self.ui.statusBar.showMessage("Screen refreshed")
        # self.ui.btn_startBatchPros.setEnabled(True)
        self.ui.btn_PO_export.setEnabled(False)
        self.ui.btn_PO_reset.setEnabled(False)

        
    def _connectSignals(self):
        """Connect signals and slots."""
        # Action tab
        self.ui.actionAbout.triggered.connect(self.about.show)
        self.ui.actionSettings.triggered.connect(self.setsDlg.show)

        # First tab
        self.ui.btn_openFDialog.clicked.connect(self._openFileNameDialog)
        self.ui.btn_reset.clicked.connect(self._resetScreen)
        self.ui.btn_export.clicked.connect(self._exportRes)
        # Second tab
        self.ui.btn_openDirDialog.clicked.connect(self._openFileDirectory)
        self.ui.btn_startBatchPros.clicked.connect(self._startBatchPros)
        self.ui.btn_PO_reset.clicked.connect(self._resetPO)
        self.ui.btn_PO_export.clicked.connect(self._exportPO)


    def _exportPO(self):
        files = [f for f in os.listdir(self.dirSelected) if isfile(join(self.dirSelected, f))]
        files_sanitised = [f for f in files if f.endswith('.txt')]
        first_file = files_sanitised[0]
        fname = first_file.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        # name, _ = QFileDialog.getSaveFileName(self, 'Save File', f'{self.dirSelected}/{date}',"Comma Seperated values (*.csv)")
        name = f'{self.dirSelected}/{date}.csv'
        logger.info(f'User selected export csv filename: {name}')
        if name != "":
            query = QSqlQuery(self.db)
            query.exec(f"""SELECT p_no, date, hour, b_count,
                            Ers_min,   Ers_max,  Ers_q5,  Ers_q25,  Ers_q50,  Ers_q75,  Ers_q95,
                            Rrs_min,   Rrs_max,  Rrs_q5,  Rrs_q25,  Rrs_q50,  Rrs_q75,  Rrs_q95,
                            PEEP_min,  PEEP_max, PEEP_q5, PEEP_q25, PEEP_q50, PEEP_q75, PEEP_q95,
                            PIP_min,   PIP_max,  PIP_q5,  PIP_q25,  PIP_q50,  PIP_q75,  PIP_q95,
                            TV_min,    TV_max,   TV_q5,   TV_q25,   TV_q50,   TV_q75,   TV_q95,
                            DP_min,    DP_max,   DP_q5,   DP_q25,   DP_q50,   DP_q75,   DP_q95,
                            AI_Norm_cnt, AI_Asyn_cnt, AI_Index  FROM results
                            WHERE p_no='{p_no}' AND date='{date}';
                            """)
                
            try:
                with open(name, mode='w', newline='') as csvfile:
                    w = csv.writer(csvfile)
                    # write header
                    w.writerow((
                        'Patient No.','Record Date','Record Hour','Breath Count',
                        'Ers_min', 'Ers_max','Ers_q5','Ers_q25','Ers_q50','Ers_q75','Ers_q95',
                        'Rrs_min', 'Rrs_max','Rrs_q5','Rrs_q25','Rrs_q50','Rrs_q75','Rrs_q95',
                        'PEEP_min', 'PEEP_max','PEEP_q5','PEEP_q25','PEEP_q50','PEEP_q75','PEEP_q95',
                        'PIP_min', 'PIP_max','PIP_q5','PIP_q25','PIP_q50','PIP_q75','PIP_q95',
                        'TV_min', 'TV_max','TV_q5','TV_q25','TV_q50','TV_q75','TV_q95',
                        'DP_min', 'DP_max','DP_q5','DP_q25','DP_q50','DP_q75','DP_q95',
                        'AI_Norm_cnt', 'AI_Asyn_cnt', 'AI_index'
                        ))
                    while query.next():
                        # Write file
                        listsTmpData = []
                        for column in range(49):
                            listsTmpData.append(str(query.value(column)))
                        w.writerow(listsTmpData)
                # Notify user export done
                self.ui.statusBar.showMessage("Data exported to: "+ name )
                # QMessageBox.information(None, ("Data exported"),
                #                     ("Data exported to: \n"+ name),
                #         QMessageBox.Ok)
            except PermissionError as e:
                # Notify user export failed
                QMessageBox.warning(None, ("Cannot write file"),
                                ('Error writing file: \n' + str(e)),
                QMessageBox.Cancel)

    def _exportRes(self):
        fname = self.fname.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])
        name, _ = QFileDialog.getSaveFileName(self, 'Save File', date,"Comma Seperated values (*.csv)")
        logger.info(f'User selected export csv filename: {name}')
        if name != "":
            query = QSqlQuery(self.db)
            query.exec(f"""SELECT p_no, date, hour, b_count,
                            Ers_min,   Ers_max,  Ers_q5,  Ers_q25,  Ers_q50,  Ers_q75,  Ers_q95,
                            Rrs_min,   Rrs_max,  Rrs_q5,  Rrs_q25,  Rrs_q50,  Rrs_q75,  Rrs_q95,
                            PEEP_min,  PEEP_max, PEEP_q5, PEEP_q25, PEEP_q50, PEEP_q75, PEEP_q95,
                            PIP_min,   PIP_max,  PIP_q5,  PIP_q25,  PIP_q50,  PIP_q75,  PIP_q95,
                            TV_min,    TV_max,   TV_q5,   TV_q25,   TV_q50,   TV_q75,   TV_q95,
                            DP_min,    DP_max,   DP_q5,   DP_q25,   DP_q50,   DP_q75,   DP_q95  FROM results
                            WHERE p_no='{p_no}' AND date='{date}' AND hour='{hour}';
                            """)
            # if query.exec_():
            #     print("DB entry retrieved successful")
            # else:
            #     print("Error: ", query.lastError().text())
                
            try:
                with open(name, mode='w', newline='') as csvfile:
                    w = csv.writer(csvfile)
                    # write header
                    w.writerow((
                        'Patient No.','Record Date','Record Hour','Breath Count',
                        'Ers_min', 'Ers_max','Ers_q5','Ers_q25','Ers_q50','Ers_q75','Ers_q95',
                        'Rrs_min', 'Rrs_max','Rrs_q5','Rrs_q25','Rrs_q50','Rrs_q75','Rrs_q95',
                        'PEEP_min', 'PEEP_max','PEEP_q5','PEEP_q25','PEEP_q50','PEEP_q75','PEEP_q95',
                        'PIP_min', 'PIP_max','PIP_q5','PIP_q25','PIP_q50','PIP_q75','PIP_q95',
                        'TV_min', 'TV_max','TV_q5','TV_q25','TV_q50','TV_q75','TV_q95',
                        'DP_min', 'DP_max','DP_q5','DP_q25','DP_q50','DP_q75','DP_q95'
                        ))
                    while query.next():
                        # Write file
                        listsTmpData = []
                        for column in range(46):
                            listsTmpData.append(str(query.value(column)))
                        w.writerow(listsTmpData)
                # Notify user export done
                self.ui.statusBar.showMessage("Data exported to: "+ name )
                QMessageBox.information(None, ("Data exported"),
                                    ("Data exported to: \n"+ name),
                        QMessageBox.Ok)
            except PermissionError as e:
                # Notify user export failed
                QMessageBox.warning(None, ("Cannot write file"),
                                ('Error writing file: \n' + str(e)),
                QMessageBox.Cancel)
            
        
    def _updateUI(self):
        """ Update UI and status after calculation done"""
        # Update UI and status
        self.ui.btn_reset.setEnabled(True)
        self.ui.btn_export.setEnabled(True)
        self.ui.statusBar.showMessage(f"Processing Completed ")
        
        # Resize table headers. Can't be done in thread(unknown reason)
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Hide the progress bar
        self.pbar.hide()
        
    def _openPbar(self):
        self.pbar.show()

    def _updatePbar(self,value,text):
        # logger.info(f'Pbar: {value},{text}')
        self.pbar.on_count_changed(value)
        self.pbar.on_text_changed(text)

    def _hidePbar(self):
        self.pbar.hide()

    def _openStackedPbar(self):
        self.spbar = StackedProgressBar(self)
        self.spbar.show()

    def _updateStackedPbar(self,value,text):
        # logger.info(f'Sub Pbar: {value},{text}')
        self.spbar.on_count_changed(value)
        self.spbar.on_text_changed(text)

    def _updateMainStackedPbar(self,value,text):
        logger.info(f'Main Pbar: {value},{text}')
        self.spbar.on_main_count_changed(value)
        self.spbar.on_main_text_changed(text)

    def _hideStackedPbar(self):
        self.spbar.hide()

    def start_thread(self,**kwargs):
        self.ui.statusBar.showMessage("Processing Data")
        self.worker = Worker(fname=self.fname,db=self.db,ui=self.ui)
        self.worker_thread = QtCore.QThread()
        self.worker.setObjectName('Worker')
        self.worker_thread.setObjectName('WorkerThread')
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.printDebug.connect(self._printDebug)
        self.worker.writeTable.connect(self._writeTable)
        self.worker.open_pbar.connect(self._openPbar)
        self.worker.update_pbar.connect(self._updatePbar)
        self.worker.update_UI.connect(self._updateUI)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.done.connect(self.stop_thread)
        self.worker_thread.start()
        logger.info('Worker thread started')

    def stop_thread(self):
        self.worker_thread.requestInterruption()
        if self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
            logger.info('qthread stopped')
        else:
            logger.info('worker has already exited.')

    def _printDebug(self, debug, b_count):
         # Display debug logs
        txt = ''
        for r in debug['rejected']:
            txt += f'BS {r[0]}: {r[1]}\n' 
        self.ui.plainTextEdit.setPlainText(txt)
        sum_b_counter = f"Summary:\n========================\nNumber of breath analysed: {debug['b_counter'][0]}\nFailed VT check: {debug['b_counter'][1]}\n"\
                        f"Failed Rrs check: {debug['b_counter'][2]}\nFailed Ers check: {debug['b_counter'][3]}\nFailed len(P=Q) check: {debug['b_counter'][4]}\n"\
                        f"Failed len(P) check: {debug['b_counter'][5]}\nTotal number of breath: {b_count}\n========================"
        self.ui.plainTextEdit_2.setPlainText(sum_b_counter)

    def _writeTable(self,res):
        """ Display info on first table """
        params = ['Ers','Rrs','PEEP','PIP','TV','DP']
        font = QtGui.QFont()
        font.setPointSize(12)
        for i in range(len(params)):
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(res[params[i]]['q5']))
            self.ui.tableWidget.setItem(0, i, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(res[params[i]]['q50']) + '\n [ ' +  str(res[params[i]]['q25']) + ' - ' + str(res[params[i]]['q75']) + ' ] ')
            self.ui.tableWidget.setItem(1, i, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(res[params[i]]['q95']))
            self.ui.tableWidget.setItem(2, i, item)










if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())