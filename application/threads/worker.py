# Standard library imports
# from application.calculations import calcRespMechanics, _calcQuartiles
import logging
import json

# Third party imports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMessageBox, QHeaderView
from PyQt5 import QtCore
import numpy as np

# Local application imports
from calculations import Elastance, _calcQuartiles
from utils.AI import get_current_model, AIpredict, load_Recon_Model, recon, saveDb

from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from keras import backend as K

# Get the logger specified in the file
logger = logging.getLogger(__name__)
logger.info('Thread module imported')

class Worker(QtCore.QObject):
    finished    = pyqtSignal()
    done        = pyqtSignal()
    open_pbar   = pyqtSignal()
    update_pbar = pyqtSignal(int,str)
    update_UI   = pyqtSignal()
    status      = pyqtSignal(int)
    run_token   = True

    def __init__(self,fname,db,ui):
        super(Worker, self).__init__()
        self.fname = fname
        self.db = db
        self.ui = ui
        self.hour = self.fname.split('/')[-1].replace('.txt','').split('_')[3]
        self.model_name = None

    def _get_prediction(self, pressure, b_count):
        
        self.update_pbar.emit(60,'Starting breath prediction...')
        now_count = 0
        b_type = []
        
        logger.info(f'Loading prediction model...')
        self.update_pbar.emit(70,f'Loading prediction model...')
        K.clear_session() # Clear keras backend last session to prevent crash
        self.model_name, self.PClassiModel = get_current_model()

        for p in pressure:
            now_count += 1
            progress = int((now_count/b_count)*100)
            self.update_pbar.emit(progress,'Predicting breath ...')
            try:
                b_type.append(AIpredict(p, self.PClassiModel))
            except:
                b_type.append(200)

        logger.info('Breath recon prediction completed.')
        
        return b_type

    def _get_recon(self,pressure,flow):

        AImag = []
        logger.info(f'Loading recon model...')
        self.update_pbar.emit(70,f'Loading recon model...')
        reconModel = load_Recon_Model()

        logger.info(f'Starting breath recon ...')
        self.update_pbar.emit(80,f'Starting breath recon ...')

        for idx, p in enumerate(pressure):
            q = flow[idx]
            AImag.append(recon(q, p, reconModel))
        filtered_AImag = [a for a in AImag if not np.isnan(a)] 
        logger.info('Breath recon prediction completed.')
        return filtered_AImag

    def _calc_ER(self):
        self.update_pbar.emit(20,'Calculating respiratory mechanics...')
        logger.info('_calc_ER run')
        
        P, Q, P_A, Q_A, Ers_A, Rrs_A, b_count, PEEP_A, PIP_A, TV_A, DP_A, b_num_all, b_len = Elastance().calcRespMechanics(self.fname)
        b_type = self._get_prediction(P_A, b_count)
        AImag = self._get_recon(P_A, Q_A)
        
        self.update_pbar.emit(90,'Calculation complete. Processing data...')
        return P, Q, Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, AImag, b_num_all, b_len

    def run(self):

        logging.info('Running run thread in worker ...')
        logging.info(f'Current filename: {self.fname}')
        self.open_pbar.emit()
        fname = self.fname.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])

        try:
            P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, AImag, b_num_all, b_len = self.fetchDbData()
            self.update_pbar.emit(80,'Fetching data from database...')
        except Exception as e:
            logger.info(f'Initiating calculation...{e}')
            self.update_pbar.emit(10,'Initiating calculation...')
            self.update_pbar.emit(50,'Loading model ...')
            

            P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, AImag, b_num_all, b_len = self._calc_ER()
            saveDb(self.db, P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, AImag, b_num_all, b_len, p_no, date, hour)
        
        self.done.emit()
        self.update_pbar.emit(90,'Populating Graphics...')
        self.ui.label_breath_no.setText(str(b_count))

        # Plot line, box, pie chart; populate resp table
        self._plotData(P, Q, Ers, Rrs, PEEP_A, b_num_all, b_len)
        self._plotBoxPlot(P, Q, Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A, AImag)
        self._populateTable(_calcQuartiles(Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A))
        self._plotPie(b_type)
        self.update_pbar.emit(100,'Processing Done...')
        self.update_UI.emit()
        self.finished.emit()

    def _plotData(self,P, Q, E, R, PEEP_A, b_num_all, b_len):
        """Plot data from thread"""
        # format time x-axis
        formatter = DateFormatter('%H:%M:%S')
        x = [datetime.strptime(self.hour, "%H-%M-%S")]
        for i in range(1,len(P)):
            x.append(x[i-1]+ timedelta(milliseconds=20))

        import time
        start = time.process_time()

        # Extend plot params according to breath length for plotting
        Ers, PEEP = [], []
        for i in range(len(b_len)):
            Ers.extend([E[i] for x in range(b_len[i])])
            PEEP.extend([PEEP_A[i] for x in range(b_len[i])])
            
        logger.info(f'Time used to extend plot params: {time.process_time() - start}')

        # reshape reducing num of points to half
        group = 2
        try:
            x = np.array(x).reshape(-1, group).mean(axis=1)
            P = np.array(P).reshape(-1, group).mean(axis=1)
            Q = np.array(Q).reshape(-1, group).mean(axis=1)
            E = np.array(E).reshape(-1, group).mean(axis=1)
            R = np.array(R).reshape(-1, group).mean(axis=1)
            R = np.array(R).reshape(-1, group).mean(axis=1)
            PEEP = np.array(PEEP).reshape(-1, group).mean(axis=1)
        except:
            pass

        # plot lines
        line1, = self.ui.graphWidget.canvas.ax.plot(x, P, label='Pressure')
        line2, = self.ui.graphWidget.canvas.ax.plot(x, Q, label='Flow')
        line3, = self.ui.graphWidget.canvas.ax.plot(x, Ers, label='Ers')
        line4, = self.ui.graphWidget.canvas.ax.plot(x, PEEP, label='PEEP')
        self.ui.graphWidget.canvas.ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
        self.ui.graphWidget.canvas.ax.axhline(0, color='grey', linewidth=0.8)
        self.ui.graphWidget.canvas.ax.xaxis.set_major_formatter(formatter)
        leg = self.ui.graphWidget.canvas.ax.legend(fancybox=True, loc ="upper right")
        line4.set_visible(False)
        self.ui.graphWidget.canvas.draw()

        # configure legend to show/hide when clicked
        lines = [line1, line2, line3, line4]
        self.plot1lined = {}  # Will map legend lines to original lines.
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(True)  # Enable picking on the legend line.
            self.plot1lined[legline] = origline
        self.ui.graphWidget.canvas.mpl_connect('pick_event', self.on_pick)

        # annotate breath number (beta)
        if b_num_all != []:
            x_annotate = [datetime.strptime(self.hour, "%H-%M-%S")]
            
            for i in range(len(b_len)-1):
                x_annotate.append(x_annotate[i]+timedelta(milliseconds=20*b_len[i]))
            
            for i, x in enumerate(x_annotate):
                annot = self.ui.graphWidget.canvas.ax.annotate(b_num_all[i], xy=(x,1), xytext=(0,2),textcoords="offset points")
    
    def on_pick(self,event):
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legline = event.artist
        origline = self.plot1lined[legline]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        self.ui.graphWidget.canvas.draw()

    def _plotBoxPlot(self,P, Q, E, R, PEEP_A, PIP_A, TV_A, DP_A, AImag):
        """Plot data from thread"""
        box1 = self.ui.boxGraphWidget.canvas.ax1.boxplot( E, labels=['Ers'])
        box2 = self.ui.boxGraphWidget.canvas.ax2.boxplot( R, labels=['Rrs'])
        box3 = self.ui.boxGraphWidget.canvas.ax3.boxplot( PEEP_A, labels=['PEEP'])
        box4 = self.ui.boxGraphWidget.canvas.ax4.boxplot( PIP_A, labels=['PIP'])
        box5 = self.ui.boxGraphWidget.canvas.ax5.boxplot( TV_A, labels=[r'$V_t$'])
        box6 = self.ui.boxGraphWidget.canvas.ax6.boxplot( DP_A, labels=['PIP-PEEP'])
        box7 = self.ui.AMBoxWidget.canvas.ax.boxplot( AImag, labels=['Masyn'])
        self.ui.boxGraphWidget.canvas.draw()
        self.ui.AMBoxWidget.canvas.draw()

    def _populateTable(self,res):
        """ Display info on first table """
        params = ['Ers','Rrs','PEEP','PIP','TV','DP']
        font = QtGui.QFont()
        font.setPointSize(10)
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

    def _plotPie(self,b_type):
        
        Asyn = b_type.count('Asyn')
        Norm = b_type.count('Normal')
        Total = Asyn + Norm
        AIndex = round(Asyn/Total*100,2)

        self.ui.asyn_breath_label.setText(str(Asyn))
        self.ui.norm_breath_label.setText(str(Norm))
        self.ui.total_breath_label.setText(str(Total))
        self.ui.ai_breath_label.setText(str(AIndex) + " %")
        self.ui.label_AI.setText(str(AIndex) + " %")
        self.ui.pieGraphWidget.canvas.ax.title.set_text('Breath Condition Distribution')

        if Asyn == 0:
            data = [Norm]
            labels = ['Normal']
            self.ui.pieGraphWidget.canvas.ax.pie(data, labels=labels, autopct='%1.1f%%',colors=['#1f77b4'])
            # self.ui.pieGraphWidget.canvas.ax.legend(labels,fancybox=True, bbox_to_anchor=(0.85,1.025), loc="upper left")
        elif Norm == 0:
            data = [Asyn]
            labels = ['Asynchrony']
            self.ui.pieGraphWidget.canvas.ax.pie(data, labels=labels, autopct='%1.1f%%',colors=['tab:orange'])
            # self.ui.pieGraphWidget.canvas.ax.legend(labels,fancybox=True, bbox_to_anchor=(0.85,1.025), loc="upper left")
        else:
            data = [Asyn, Norm]
            labels = ['Asynchrony','Normal']
            self.ui.pieGraphWidget.canvas.ax.pie(data, labels=labels, autopct='%1.1f%%',colors=['tab:orange','#1f77b4'])
        labels = ['Asynchrony','Normal']
        self.ui.pieGraphWidget.canvas.ax.legend(labels,fancybox=True, bbox_to_anchor=(0.85,1.025), loc="upper left")
        self.ui.pieGraphWidget.canvas.draw()
        
    def fetchDbData(self):
        fname = self.fname.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])
        query = QSqlQuery(self.db)
        query.exec(f"""SELECT p, q, Ers_raw, Rrs_raw, b_count, b_type, b_num_all, b_len,
                        PEEP_raw, PIP_raw, TV_raw, DP_raw, AM_raw  FROM results 
                        WHERE p_no='{p_no}' AND date='{date}' AND hour='{hour}';
                        """)
        if query.next():
            query.first()
            P         = json.loads(query.value(0))
            Q         = json.loads(query.value(1))
            Ers       = json.loads(query.value(2))
            Rrs       = json.loads(query.value(3))
            b_count   = query.value(4)
            b_type    = json.loads(query.value(5))
            b_num_all = json.loads(query.value(6))
            b_len     = json.loads(query.value(7))
            PEEP_A    = json.loads(query.value(8))
            PIP_A     = json.loads(query.value(9))
            TV_A      = json.loads(query.value(10))
            DP_A      = json.loads(query.value(11))
            AImag     = json.loads(query.value(12))
            logger.info("DB entry retrieved successful")
            return P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, AImag, b_num_all, b_len
        else:
            raise Exception

    