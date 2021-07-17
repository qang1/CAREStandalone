# Standard library imports
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
from utils.AI import get_current_model, AIpredict

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

    def _get_prediction(self,b_count):
        b_type, pressure = [], []
        now_count = 0
        self.update_pbar.emit(60,'Starting breath prediction...')
        f = open(self.fname, "r")
        for line in f:
            if ("BS," in line) == True:
                now_count += 1
                progress = int((now_count/b_count)*100)
                self.update_pbar.emit(progress,'Predicting breath ...')
            elif ("BE" in line) == True:
                if len(pressure) != 0:
                    b_type.append(AIpredict(pressure, self.PClassiModel))
                pressure = [] # reset pressure list
            else:
                if line != '': # Filter out empty lines
                    section = line.split(',') # 2.34, 5.78 -> ['2.34','5.78']
                    try:
                        p_split = float(section[1])
                        pressure.append(round(p_split,1))
                    except:
                        pass
        
        return b_type

    def _calc_ER(self):
        f = open(self.fname, "r")
        self.update_pbar.emit(20,'Calculating respiratory mechanics...')
        pressure, flow = [], []
        P, Q, Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A = [],[],[],[],[],[],[],[]
        logger.info('_calc_ER run')
        b_count = 0
        for line in f:
            if ("BS," in line) == True:
                pass
            elif ("BE" in line) == True:
                b_count += 1
                if (len(pressure) != 0) and (len(flow) != 0) and (len(pressure) >= 50) and (len(pressure) == len(flow)):
                    E, R, PEEP, PIP, TidalVolume, _, _ = Elastance().get_r(pressure, flow, True) # calculate respiratory parameter 
                
                    if (abs(E)<100) & (abs(R)<100) & (TidalVolume<1):
                        for i in range(len(pressure)):
                            Ers.append(E)
                            Rrs.append(R)
                        P.extend(pressure)
                        Q.extend(flow)
                        PEEP_A.append(round(PEEP,1))
                        PIP_A.append(round(PIP,1))
                        TV_A.append(round(TidalVolume*1000))
                        DP_A.append(round(PIP-PEEP,1))
                pressure, flow = [], [] # reset temp list
            else:
                if line != '': # Filter out empty lines
                    section = line.split(',') # 2.34, 5.78 -> ['2.34','5.78']
                    try:
                        p_split = float(section[1])
                        q_split = float(section[0])
                        pressure.append(round(p_split,1))
                        flow.append(round(q_split,1))
                    except:
                        pass
        b_type = self._get_prediction(b_count)
        self.update_pbar.emit(80,'Calculation complete. Processing data...')
        return P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A

    def run(self):
        K.clear_session() # Clear keras backend last session to prevent crash
        self.update_pbar.emit(50,'Loading model ...')
        self.model_name, self.PClassiModel = get_current_model()

        logging.info('Running run thread in worker ...')
        self.open_pbar.emit()
        try:
            P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A = self.fetchDbData()
            self.update_pbar.emit(80,'Fetching data from database...')
        except Exception as e:
            logger.info('Initiating calculation...')
            self.update_pbar.emit(10,'Initiating calculation...')
            P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A = self._calc_ER()
            self.saveDb(P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A)
        
        self.done.emit()
        self.update_pbar.emit(90,'Populating Graphics...')
        self.ui.label_breath_no.setText(str(b_count))

        # Plot line, box, pie chart; populate resp table
        self._plotData(P,Q,Ers,Rrs)
        self._plotBoxPlot(P, Q, Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A)
        self._populateTable(_calcQuartiles(Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A))
        self._plotPie(b_type)
        self.update_pbar.emit(100,'Processing Done...')
        self.update_UI.emit()
        self.finished.emit()

    def _plotData(self,P, Q, E, R):
        """Plot data from thread"""
        # format time x-axis
        formatter = DateFormatter('%H:%M:%S')
        x = [datetime.strptime(self.hour, "%H-%M-%S")]
        for i in range(1,len(P)):
            x.append(x[i-1]+ timedelta(milliseconds=20))

        # reshape reducing num of points to half
        x, P, Q, E, R = self.reshape(x, P, Q, E, R) 

        # plot lines
        line1, = self.ui.graphWidget.canvas.ax.plot(x, P, label='Pressure')
        line2, = self.ui.graphWidget.canvas.ax.plot(x, Q, label='Flow')
        line3, = self.ui.graphWidget.canvas.ax.plot(x, E, label='Ers')
        self.ui.graphWidget.canvas.ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
        self.ui.graphWidget.canvas.ax.xaxis.set_major_formatter(formatter)
        leg = self.ui.graphWidget.canvas.ax.legend(fancybox=True, loc ="upper right")
        self.ui.graphWidget.canvas.draw()

        # configure legend to show/hide when clicked
        lines = [line1, line2, line3]
        self.plot1lined = {}  # Will map legend lines to original lines.
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(True)  # Enable picking on the legend line.
            self.plot1lined[legline] = origline
        self.ui.graphWidget.canvas.mpl_connect('pick_event', self.on_pick)
    
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

    def _plotBoxPlot(self,P, Q, E, R, PEEP_A, PIP_A, TV_A, DP_A):
        """Plot data from thread"""
        box1 = self.ui.boxGraphWidget.canvas.ax1.boxplot( E, labels=['Ers'])
        box2 = self.ui.boxGraphWidget.canvas.ax2.boxplot( R, labels=['Rrs'])
        box3 = self.ui.boxGraphWidget.canvas.ax3.boxplot( PEEP_A, labels=['PEEP'])
        box4 = self.ui.boxGraphWidget.canvas.ax4.boxplot( PIP_A, labels=['PIP'])
        box5 = self.ui.boxGraphWidget.canvas.ax5.boxplot( TV_A, labels=[r'$V_t$'])
        box6 = self.ui.boxGraphWidget.canvas.ax6.boxplot( DP_A, labels=['PIP-PEEP'])
        self.ui.boxGraphWidget.canvas.draw()

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
        self.ui.asyn_breath_label.setText(str(Asyn))
        self.ui.norm_breath_label.setText(str(Norm))
        self.ui.total_breath_label.setText(str(Total))
        self.ui.ai_breath_label.setText(str(AIndex) + " %")
        

    def reshape(self,x,P,Q,E,R):
        group = 2
        try:
            x = np.array(x).reshape(-1, group).mean(axis=1)
            P = np.array(P).reshape(-1, group).mean(axis=1)
            Q = np.array(Q).reshape(-1, group).mean(axis=1)
            E = np.array(E).reshape(-1, group).mean(axis=1)
            R = np.array(R).reshape(-1, group).mean(axis=1)
            return x, P , Q, E, R
        except:
            pass
        finally:
            return x, P , Q, E, R

    def fetchDbData(self):
        fname = self.fname.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])
        query = QSqlQuery(self.db)
        query.exec(f"""SELECT p, q, Ers_raw, Rrs_raw, b_count, b_type,
                         PEEP_raw, PIP_raw, TV_raw, DP_raw  FROM results 
                        WHERE p_no='{p_no}' AND date='{date}' AND hour='{hour}';
                        """)
        if query.next():
            query.first()
            P = json.loads(query.value(0))
            Q = json.loads(query.value(1))
            Ers = json.loads(query.value(2))
            Rrs = json.loads(query.value(3))
            b_count = query.value(4)
            b_type = json.loads(query.value(5))
            PEEP_A = json.loads(query.value(6))
            PIP_A = json.loads(query.value(7))
            TV_A = json.loads(query.value(8))
            DP_A = json.loads(query.value(9))
            print("DB entry retrieved successful")
            return P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A
        else:
            raise Exception

    def saveDb(self,P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A):
        fname = self.fname.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])
        p = json.dumps(P)
        q = json.dumps(Q)
        e = json.dumps(Ers)
        r = json.dumps(Rrs)
        PEEP_raw = json.dumps(PEEP_A)
        PIP_raw = json.dumps(PIP_A)
        TV_raw = json.dumps(TV_A)
        DP_raw = json.dumps(DP_A)
        b_type = json.dumps(b_type)
        dObj = _calcQuartiles(Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A)

        query = QSqlQuery(self.db)
        query.prepare(f"""INSERT INTO results (p_no, date, hour, p, q, b_count, b_type,
                        Ers_raw, Rrs_raw, PEEP_raw, PIP_raw, TV_raw, DP_raw,
                        Ers_q5,  Rrs_q5,  PEEP_q5,  PIP_q5,  TV_q5,  DP_q5,
                        Ers_q25, Rrs_q25, PEEP_q25, PIP_q25, TV_q25, DP_q25,
                        Ers_q50, Rrs_q50, PEEP_q50, PIP_q50, TV_q50, DP_q50,
                        Ers_q75, Rrs_q75, PEEP_q75, PIP_q75, TV_q75, DP_q75,
                        Ers_q95, Rrs_q95, PEEP_q95, PIP_q95, TV_q95, DP_q95,
                        Ers_min, Rrs_min, PEEP_min, PIP_min, TV_min, DP_min,
                        Ers_max, Rrs_max, PEEP_max, PIP_max, TV_max, DP_max) 
                        VALUES (:p_no, :date, :hour, :p, :q, :b_count, :b_type,
                        :Ers_raw, :Rrs_raw, :PEEP_raw, :PIP_raw, :TV_raw, :DP_raw, 
                        :Ers_q5,  :Rrs_q5,  :PEEP_q5,  :PIP_q5,  :TV_q5,  :DP_q5,
                        :Ers_q25, :Rrs_q25, :PEEP_q25, :PIP_q25, :TV_q25, :DP_q25,
                        :Ers_q50, :Rrs_q50, :PEEP_q50, :PIP_q50, :TV_q50, :DP_q50,
                        :Ers_q75, :Rrs_q75, :PEEP_q75, :PIP_q75, :TV_q75, :DP_q75,
                        :Ers_q95, :Rrs_q95, :PEEP_q95, :PIP_q95, :TV_q95, :DP_q95,
                        :Ers_min, :Rrs_min, :PEEP_min, :PIP_min, :TV_min, :DP_min,
                        :Ers_max, :Rrs_max, :PEEP_max, :PIP_max, :TV_max, :DP_max)""")
        query.bindValue(":p_no", p_no)
        query.bindValue(":date", date)
        query.bindValue(":hour", hour)
        query.bindValue(":p", p)
        query.bindValue(":q", q)
        query.bindValue(":b_count", b_count)
        query.bindValue(":b_type", b_type)
        query.bindValue(":Ers_raw", e)
        query.bindValue(":Rrs_raw", r)
        query.bindValue(":PEEP_raw", PEEP_raw)
        query.bindValue(":PIP_raw", PIP_raw)
        query.bindValue(":TV_raw", TV_raw)
        query.bindValue(":DP_raw", DP_raw)
        
        query.bindValue(":Ers_q5", float(dObj['Ers']['q5']))
        query.bindValue(":Rrs_q5", float(dObj['Rrs']['q5']))
        query.bindValue(":PEEP_q5", float(dObj['PEEP']['q5']))
        query.bindValue(":PIP_q5", float(dObj['PIP']['q5']))
        query.bindValue(":TV_q5", float(dObj['TV']['q5']))
        query.bindValue(":DP_q5", float(dObj['DP']['q5']))

        query.bindValue(":Ers_q25", float(dObj['Ers']['q25']))
        query.bindValue(":Rrs_q25", float(dObj['Rrs']['q25']))
        query.bindValue(":PEEP_q25", float(dObj['PEEP']['q25']))
        query.bindValue(":PIP_q25", float(dObj['PIP']['q25']))
        query.bindValue(":TV_q25", float(dObj['TV']['q25']))
        query.bindValue(":DP_q25", float(dObj['DP']['q25']))
        
        query.bindValue(":Ers_q50", float(dObj['Ers']['q50']))
        query.bindValue(":Rrs_q50", float(dObj['Rrs']['q50']))
        query.bindValue(":PEEP_q50", float(dObj['PEEP']['q50']))
        query.bindValue(":PIP_q50", float(dObj['PIP']['q50']))
        query.bindValue(":TV_q50", float(dObj['TV']['q50']))
        query.bindValue(":DP_q50", float(dObj['DP']['q50']))
        
        query.bindValue(":Ers_q75", float(dObj['Ers']['q75']))
        query.bindValue(":Rrs_q75", float(dObj['Rrs']['q75']))
        query.bindValue(":PEEP_q75", float(dObj['PEEP']['q75']))
        query.bindValue(":PIP_q75", float(dObj['PIP']['q75']))
        query.bindValue(":TV_q75", float(dObj['TV']['q75']))
        query.bindValue(":DP_q75", float(dObj['DP']['q75']))
        
        query.bindValue(":Ers_q95", float(dObj['Ers']['q95']))
        query.bindValue(":Rrs_q95", float(dObj['Rrs']['q95']))
        query.bindValue(":PEEP_q95", float(dObj['PEEP']['q95']))
        query.bindValue(":PIP_q95", float(dObj['PIP']['q95']))
        query.bindValue(":TV_q95", float(dObj['TV']['q95']))
        query.bindValue(":DP_q95", float(dObj['DP']['q95']))
        
        query.bindValue(":Ers_min", float(dObj['Ers']['min']))
        query.bindValue(":Rrs_min", float(dObj['Rrs']['min']))
        query.bindValue(":PEEP_min", dObj['PEEP']['min'])
        query.bindValue(":PIP_min", dObj['PIP']['min'])
        query.bindValue(":TV_min", 100)
        query.bindValue(":DP_min", dObj['DP']['min'])
        
        query.bindValue(":Ers_max", float(dObj['Ers']['max']))
        query.bindValue(":Rrs_max", float(dObj['Rrs']['max']))
        query.bindValue(":PEEP_max", dObj['PEEP']['max'])
        query.bindValue(":PIP_max", dObj['PIP']['max'])
        query.bindValue(":TV_max", dObj['TV']['max'])
        query.bindValue(":DP_max", dObj['DP']['max'])
        
        if query.exec_():
            print("DB entry query successful")
        else:
            print("Error: ", query.lastError().text())

   


    