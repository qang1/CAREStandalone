# Standard library imports
from multiprocessing.pool import ThreadPool
import statistics
import time
import json
import os

# Third party imports
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QSettings
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSql import  QSqlQuery
import numpy as np
import logging
from keras import backend as K

# Local application imports
from calculations import Elastance, _calcQuartiles
from utils.AI import get_current_model, predict

# Get the logger specified in the file
logger = logging.getLogger(__name__)

class PostProcessor(QtCore.QObject):
    finished = pyqtSignal()
    processResMulti = pyqtSignal(object)
    open_pbar = pyqtSignal()
    hide_pbar = pyqtSignal()
    update_subpbar = pyqtSignal(int,str)
    update_mainpbar = pyqtSignal(int,str)

    def __init__(self,fname,dirSelected,db,ui):
        super(PostProcessor, self).__init__()
        self.fname = fname
        self.dirSelected = dirSelected
        self.db = db
        self.ui = ui
        self.total = len(fname)
        self.cnt = 0
        self.settings = QSettings()

    def run(self):
        sum_results = []
        self.open_pbar.emit()
        self.updateStatus()
        # Uncomment below to use threading (Not working correctly currently)
        # pool = ThreadPool(2)
        # pool.map_async(self.fun, self.fname, callback=self.handle_result)
        chopHalf = self.settings.value('resolution') == '30mins'
        logging.info(f'Plot resolution (30mins): {chopHalf}')
        # chopHalf = True
        if chopHalf == True:
            for arg in self.fname:
                _, p_no, date, hour = arg.replace('.txt','').split('_')
                path = f'{self.dirSelected}/{arg}'
                f = open(path, "r")
                pressure, flow, b_type = [], [], []
                P, Q, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A = [], [], [], [], [], [], [], []
                b_count = 0
                try:
                    Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A = self.fetchDb(p_no,date,hour)
                except:
                    for line in f:
                        if ("BS," in line) == True:
                            pass
                        elif ("BE" in line) == True:
                            b_count += 1
                            if (len(pressure) != 0) and (len(flow) != 0) and (len(pressure) >= 50) and (len(pressure) == len(flow)):
                                E, R, PEEP, PIP, TidalVolume, _, _ = Elastance().get_r(pressure, flow, True) # calculate respiratory parameter 
                                if (abs(E)<100) & (abs(R)<100) & (TidalVolume<1):
                                    for i in range(len(pressure)):
                                        Ers_A.append(E)
                                        Rrs_A.append(R)
                                    P.extend(pressure)
                                    Q.extend(flow)
                                    PEEP_A.append(round(PEEP,1))
                                    PIP_A.append(round(PIP,1))
                                    TV_A.append(round(TidalVolume*1000))
                                    DP_A.append(round(PIP-PEEP,1))
                            pressure, flow = [], [] # reset temp list
                        else:
                            section = line.split(',')
                            try:
                                p_split = float(section[1])
                                q_split = float(section[0])
                                pressure.append(round(p_split,1))
                                flow.append(round(q_split,1))
                            except:
                                pass
                    
                    # get prediction
                    b_type = self._get_prediction(path,b_count)

                    # Save results into db
                    self.saveDb(P, Q, Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, arg)


                # Split into half
                middle_index = b_count//2

                # First half    
                dObj = {
                    'p_no': p_no,
                    'date': date,
                    'hour': hour,
                    'Ers': Ers_A[:middle_index],
                    'Rrs': Rrs_A[:middle_index],
                    'PEEP': PEEP_A[:middle_index],
                    'PIP': PIP_A[:middle_index],
                    'TV': TV_A[:middle_index],
                    'DP': DP_A[:middle_index],
                    'b_type': b_type[:middle_index],
                    'b_cnt': b_count
                }
                sum_results.append(dObj)

                # Second half    
                hour_half = f'{hour.split("-")[0]}-30-00' # 01-30-00

                dObj = {
                    'p_no': p_no,
                    'date': date,
                    'hour': hour_half,
                    'Ers': Ers_A[middle_index:],
                    'Rrs': Rrs_A[middle_index:],
                    'PEEP': PEEP_A[middle_index:],
                    'PIP': PIP_A[middle_index:],
                    'TV': TV_A[middle_index:],
                    'DP': DP_A[middle_index:],
                    'b_type': b_type[middle_index:],
                    'b_cnt': b_count-middle_index
                }

                sum_results.append(dObj)
                self.updateStatus()
                
        else:
            for f in self.fname:
                dObj = self.fun(f)
                sum_results.append(dObj)
        self.handle_result(sum_results)


    
    def updateStatus(self):
        perCmpl = round(self.cnt/self.total*100,2)
        self.update_mainpbar.emit(perCmpl,f"Total: Processing file {self.cnt}/{self.total}")
        self.cnt += 1
        logger.info(f"Processing file {self.cnt}/{self.total}")

    def fetchDb(self,p_no,date,hour):
        
        logger.info(f'DB lookup.Params - p_no: {p_no}; date: {date}; hour: {hour}')
        query = QSqlQuery(self.db)
        query.exec(f"""SELECT p, q, Ers_raw, Rrs_raw, b_count, b_type,
                        PEEP_raw, PIP_raw, TV_raw, DP_raw  FROM results 
                        WHERE p_no='{p_no}' AND date='{date}' AND hour='{hour}';
                        """)
        if query.next():
            query.first()
            logger.warning(f' DEBUG: first() true')
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
            logger.info('DB entry found. Breath count: %s', b_count)
            return Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A
        else:
            logger.warning(f'No db found. DEBUG: query.next() false')
            logger.warning(f'{self.db.lastError().text()}')
            raise Exception

    def fun(self,arg):
        self.update_subpbar.emit(10,f"Processing file {arg}")
        path = self.dirSelected + '/' + arg
        _, p_no, date, hour = arg.replace('.txt','').split('_')
        try:
            Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A = self.fetchDb(p_no,date,hour)
        except:
            logger.info(f'Calculating results... {arg}')
            self.update_subpbar.emit(20,f"Calculating results... {arg}")
            f = open(path, "r")
            pressure, flow, b_type = [], [], []
            P, Q, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A = [], [], [], [], [], [], [], []
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
                                Ers_A.append(E)
                                Rrs_A.append(R)
                            P.extend(pressure)
                            Q.extend(flow)
                            PEEP_A.append(round(PEEP,1))
                            PIP_A.append(round(PIP,1))
                            TV_A.append(round(TidalVolume*1000))
                            DP_A.append(round(PIP-PEEP,1))
                    pressure, flow = [], [] # reset temp list
                else:
                    section = line.split(',')
                    try:
                        p_split = float(section[1])
                        q_split = float(section[0])
                        pressure.append(round(p_split,1))
                        flow.append(round(q_split,1))
                    except:
                        pass
            logger.info('Calculation completed')
            self.update_subpbar.emit(30,f"Calculation completed... {arg}")
            b_type = self._get_prediction(path,b_count)
            self.saveDb(P, Q, Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, arg)
            
        dObj = {
            'p_no': p_no,
            'date': date,
            'hour': hour,
            'Ers': Ers_A,
            'Rrs': Rrs_A,
            'PEEP': PEEP_A,
            'PIP': PIP_A,
            'TV': TV_A,
            'DP': DP_A,
            'b_type': b_type,
            'b_cnt': b_count
        }

        self.updateStatus()
        
        return dObj

   

    def _get_prediction(self,path,b_count):
        b_type, pressure = [], []
        now_count = 0

        logger.info(f'Loading model...{path}')
        self.update_subpbar.emit(40,f'Loading model...{path}')
        K.clear_session()
        model_name, self.PClassiModel = get_current_model()
        logger.info(f'Starting breath prediction...{path}')
        self.update_subpbar.emit(40,f'Starting breath prediction...{path}')
        try:
            f = open(path, "r")
            for line in f:
                if ("BS," in line) == True:
                    now_count += 1
                    progress = int((now_count/b_count)*100)
                    self.update_subpbar.emit(progress,'Predicting breath ...')
                elif ("BE" in line) == True:
                    if len(pressure) != 0:
                        b_type.append(predict(pressure, self.PClassiModel))
                    pressure = [] # reset pressure list
                else:
                    section = line.split(',')
                    try:
                        p_split = float(section[1])
                        pressure.append(round(p_split,1))
                    except:
                        pass
            logger.info('Breath prediction completed.')
        except Exception as e:
            logger.error(f'{e}')
        return b_type

    

    def saveDb(self, P, Q, E, R, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, arg):
        fname = arg.replace('.txt','')
        p_no = str(fname.split('_')[1])
        date = str(fname.split('_')[2])
        hour = str(fname.split('_')[3])
        dObj = _calcQuartiles(E, R, PEEP_A, PIP_A, TV_A, DP_A)
        p = json.dumps(P)
        q = json.dumps(Q)
        e = json.dumps(E)
        r = json.dumps(R)
        PEEP_raw = json.dumps(PEEP_A)
        PIP_raw = json.dumps(PIP_A)
        TV_raw = json.dumps(TV_A)
        DP_raw = json.dumps(DP_A)

        Norm_cnt = b_type.count('Normal')
        Asyn_cnt = b_type.count('Asyn')
        AI_index = round(Asyn_cnt/(Asyn_cnt+Norm_cnt)*100,2)
        b_type = json.dumps(b_type)

        query = QSqlQuery(self.db)
        query.prepare(f"""INSERT INTO results (p_no, date, hour, p, q, b_count, b_type,
                        Ers_raw, Rrs_raw, PEEP_raw, PIP_raw, TV_raw, DP_raw,
                        Ers_q5,  Rrs_q5,  PEEP_q5,  PIP_q5,  TV_q5,  DP_q5,
                        Ers_q25, Rrs_q25, PEEP_q25, PIP_q25, TV_q25, DP_q25,
                        Ers_q50, Rrs_q50, PEEP_q50, PIP_q50, TV_q50, DP_q50,
                        Ers_q75, Rrs_q75, PEEP_q75, PIP_q75, TV_q75, DP_q75,
                        Ers_q95, Rrs_q95, PEEP_q95, PIP_q95, TV_q95, DP_q95,
                        Ers_min, Rrs_min, PEEP_min, PIP_min, TV_min, DP_min,
                        Ers_max, Rrs_max, PEEP_max, PIP_max, TV_max, DP_max,
                        AI_Norm_cnt, AI_Asyn_cnt, AI_Index) 
                        VALUES (:p_no, :date, :hour, :p, :q, :b_count, :b_type,
                        :Ers_raw, :Rrs_raw, :PEEP_raw, :PIP_raw, :TV_raw, :DP_raw, 
                        :Ers_q5,  :Rrs_q5,  :PEEP_q5,  :PIP_q5,  :TV_q5,  :DP_q5,
                        :Ers_q25, :Rrs_q25, :PEEP_q25, :PIP_q25, :TV_q25, :DP_q25,
                        :Ers_q50, :Rrs_q50, :PEEP_q50, :PIP_q50, :TV_q50, :DP_q50,
                        :Ers_q75, :Rrs_q75, :PEEP_q75, :PIP_q75, :TV_q75, :DP_q75,
                        :Ers_q95, :Rrs_q95, :PEEP_q95, :PIP_q95, :TV_q95, :DP_q95,
                        :Ers_min, :Rrs_min, :PEEP_min, :PIP_min, :TV_min, :DP_min,
                        :Ers_max, :Rrs_max, :PEEP_max, :PIP_max, :TV_max, :DP_max,
                        :AI_Norm_cnt, :AI_Asyn_cnt, :AI_Index)""")
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
        query.bindValue(":TV_min", dObj['TV']['min'])
        query.bindValue(":DP_min", dObj['DP']['min'])
        
        query.bindValue(":Ers_max", float(dObj['Ers']['max']))
        query.bindValue(":Rrs_max", float(dObj['Rrs']['max']))
        query.bindValue(":PEEP_max", dObj['PEEP']['max'])
        query.bindValue(":PIP_max", dObj['PIP']['max'])
        query.bindValue(":TV_max", dObj['TV']['max'])
        query.bindValue(":DP_max", dObj['DP']['max'])

        query.bindValue(":AI_Norm_cnt", Norm_cnt)
        query.bindValue(":AI_Asyn_cnt", Asyn_cnt)
        query.bindValue(":AI_Index", AI_index)
        if query.exec_():
            logger.info("DB entry query successful")
        else:
            logger.error(f"Error: {query.lastError().text()}")

    def handle_result(self,sum_results):
        """Handles post processing of results after calculation

        Args:
            sum_results ([type]): [description]
        """
        logger.info('PostProcessor.handle_result(): task finished')
        r_dialy = self.combine_allday_breath(sum_results)
        self.populate_table(r_dialy)            # Populate results summary table
        self.plotBox(r_dialy)                   # Plot boxplot of resp mechanics
        self.plotAIBar(r_dialy)                 # Plot barchart of Asynchrony analysis
        self.processResMulti.emit(r_dialy)      # Send signal to mainwindow to update UI
        self.hide_pbar.emit()                   # Hide progress bar
        self.finished.emit()                    # End thread

    def combine_allday_breath(self,dObj):
        """Combine multiple hours into all day list

        Args:
            dObj ([type]): [description]

        Returns:
            [type]: [description]
        """
        sum_hour, sum_Ers, sum_Rrs, sum_PEEP, sum_PIP, sum_TV, sum_DP, sum_BC, sum_AI = [],[],[],[],[],[],[],[],[]
        E, R, PEEP_A, PIP_A, TV_A, DP_A = [],[],[],[],[],[]
        for arg in dObj:
            sum_hour.append(arg['hour'])
            sum_Ers.append(arg['Ers'])
            sum_Rrs.append(arg['Rrs'])
            sum_PEEP.append(arg['PEEP'])
            sum_PIP.append(arg['PIP'])
            sum_TV.append(arg['TV'])
            sum_DP.append(arg['DP'])
            sum_BC.append(arg['b_cnt'])
            sum_AI.append(arg['b_type'])

            E.extend(arg['Ers'])
            R.extend(arg['Rrs'])
            PEEP_A.extend(arg['PEEP'])
            PIP_A.extend(arg['PIP'])
            TV_A.extend(arg['TV'])
            DP_A.extend(arg['DP'])
        result = {
            'p_no': dObj[0]['p_no'],
            'date': dObj[0]['date'],
            'hours': sum_hour,
            'b_cnt': sum(sum_BC),
            'Ers': {},
            'Rrs': {},
            'PEEP': {},
            'PIP': {},
            'TV': {},
            'DP': {},
            'b_type': sum_AI
        }
        
        params = ['Ers','Rrs','PEEP','PIP','TV','DP']
        paramsVal = [E, R, PEEP_A, PIP_A, TV_A, DP_A]
        paramsRaw = [sum_Ers, sum_Rrs, sum_PEEP, sum_PIP, sum_TV, sum_DP]
        rounding = [1,1,1,1,0,1]
        for i in range(len(params)):
            result[params[i]]['q5'],result[params[i]]['q25'],result[params[i]]['q50'],result[params[i]]['q75'],result[params[i]]['q95'] = np.around(np.nanquantile(paramsVal[i],[.05,.25,.50,.75,.95]),rounding[i])
            result[params[i]]['min'] = min(paramsVal[i])
            result[params[i]]['max'] = max(paramsVal[i])
            result[params[i]]['raw'] = paramsRaw[i]
        for j in ['q5','q25','q50','q75','q95']:
            result['TV'][j] = result['TV'][j].astype(int)     
        # result['TV']['q5'],result['TV']['q25'],result['TV']['q50'],result['TV']['q75'],result['TV']['q95'] = result['TV']['q5'].astype(int) ,result['TV']['q25'].astype(int) ,result['TV']['q50'].astype(int) ,result['TV']['q75'].astype(int) ,result['TV']['q95'].astype(int)
        
        return result

    def populate_table(self,r_dialy):
        """Populate results summary table

        Args:
            r_dialy ([type]): [description]
        """
        params = ['Ers','Rrs','PEEP','PIP','TV','DP']
        font = QtGui.QFont()
        font.setPointSize(12)
        for i in range(len(params)):
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(r_dialy[params[i]]['q5']))
            self.ui.tableWidget_2.setItem(0, i, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(r_dialy[params[i]]['q50']) + '\n [ ' +  str(r_dialy[params[i]]['q25']) + ' - ' + str(r_dialy[params[i]]['q75']) + ' ] ')
            self.ui.tableWidget_2.setItem(1, i, item)
            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            item.setText(str(r_dialy[params[i]]['q95']))
            self.ui.tableWidget_2.setItem(2, i, item)
        
    def plotBox(self,res):
        """Plot boxplot of resp mechanics

        Args:
            res ([type]): [description]
        """
        # define lists for mpl plots
        plots = [self.ui.poErsWidget.canvas,self.ui.poRrsWidget.canvas,self.ui.poPIPWidget.canvas,
            self.ui.poPEEPWidget.canvas,self.ui.poVtWidget.canvas,self.ui.poDpWidget.canvas]
        y_labels = [r'$cmH_2O/l$',r'$cmH_2Os/l$',r'$cmH_2O$',r'$cmH_2O$','ml',r'$cmH_2O$']
        xaxis = [res['hours'][i][0:5].replace('-','') for i in range(len(res['hours']))]
        params = ['Ers','Rrs','PEEP','PIP','TV','DP']

        if len(xaxis) > 10:
            rot_angle = 45
        else:
            rot_angle = 0

        # setup and draw plots in for loop
        for i in range(len(plots)):
            plots[i].ax.set_xlabel('Hour (24-hour notation)')
            plots[i].ax.set_ylabel(y_labels[i])
            plots[i].ax.boxplot(res[params[i]]['raw'],labels=xaxis, showfliers=False)
            plots[i].ax.set_xticklabels(xaxis, rotation = rot_angle)
            plots[i].draw()

        for i in range(len(plots)):
            plots[i].fig.set_size_inches(14,4)
            plots[i].fig.savefig(f'{self.dirSelected}/{params[i]}.png', dpi=300)



    def plotAIBar(self,res):
        """Plot barchart of Asynchrony analysis

        Args:
            res ([type]): [description]
        """
        xaxis = [res['hours'][i][0:5] for i in range(len(res['hours']))]
        b_types = res['b_type']
        Asyn, Norm, Asyn_perc, Norm_perc, Total = [],[],[],[],[]
        for b in b_types:
            Asyn.append(b.count('Asyn'))
            Norm.append(b.count('Normal'))
            Total.append(b.count('Asyn')+b.count('Normal'))
            try:
                Asyn_perc.append(b.count('Asyn')/(b.count('Asyn')+b.count('Normal'))*100)
                Norm_perc.append(b.count('Normal')/(b.count('Asyn')+b.count('Normal'))*100)
            except:
                Asyn_perc.append(0)
                Norm_perc.append(0)
        self.ui.label_PO_AI.setText(str(round(statistics.median(Asyn_perc),2)) + " %")

        if len(xaxis) > 10:
            rot_angle = 45
        else:
            rot_angle = 0
        
        self.ui.poAIWidget.canvas.ax.bar(x=xaxis, height=Norm_perc, width=0.35, label='Normal')
        self.ui.poAIWidget.canvas.ax.bar(x=xaxis, height=Asyn_perc, width=0.35, bottom=Norm_perc, label='Asynchrony')
        self.ui.poAIWidget.canvas.ax.set_xlabel('Hour (24-hour notation)')
        self.ui.poAIWidget.canvas.ax.set_ylabel('Asynchrony Index (%)')
        self.ui.poAIWidget.canvas.ax.legend()
        self.ui.poAIWidget.canvas.ax.set_xticklabels(xaxis, rotation = rot_angle)
        self.ui.poAIWidget.canvas.draw()
        self.ui.poAIWidget.canvas.fig.set_size_inches(14,4)
        self.ui.poAIWidget.canvas.fig.savefig(f'{self.dirSelected}/AI.png', dpi=300)

