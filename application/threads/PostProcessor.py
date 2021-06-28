# Standard library imports
from multiprocessing.pool import ThreadPool
import time
import json
import os

# Third party imports
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSql import  QSqlQuery
import numpy as np
import logging

# Local application imports
from calculations import Elastance, _calcQuartiles
from utils.AI import get_current_model, predict

# Get the logger specified in the file
logger = logging.getLogger(__name__)

class PostProcessor(QtCore.QObject):
    finished = pyqtSignal()
    results = pyqtSignal(object)
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

    def run(self):
        sum_results = []
        self.open_pbar.emit()
        self.updateStatus()
        # pool = ThreadPool(2)
        # pool.map_async(self.fun, self.fname, callback=self.handle_result)
        for f in self.fname:
            dObj = self.fun(f)
            sum_results.append(dObj)
        self.handle_result(sum_results)


    
    def updateStatus(self):
        self.cnt += 1
        perCmpl = round(self.cnt/self.total*100,2)
        self.update_mainpbar.emit(perCmpl,f"Total: Processing file {self.cnt}/{self.total}")
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
        p_no = arg.replace('.txt','').split('_')[1]
        date = arg.replace('.txt','').split('_')[2]
        hour = arg.replace('.txt','').split('_')[-1]
        try:
            Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A = self.fetchDb(p_no,date,hour)
        except:
            logger.info(f'Calculating results... {arg}')
            self.update_subpbar.emit(20,f"Calculating results... {arg}")
            f = open(path, "r")
            pressure, flow = [], []
            P, Q, Ers, Rrs, PEEP_A, PIP_A, TV_A, DP_A = [], [], [], [], [], [], [], []
            b_type = []
            b_count = 0
            for line in f:
                if ("BS," in line) == True:
                    pass
                elif ("BE" in line) == True:
                    b_count += 1
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
            self.saveDb(P, Q, Ers, Rrs, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, arg)
            
        dObj = {
            'p_no': p_no,
            'date': date,
            'hour': hour,
            'Ers': Ers,
            'Rrs': Rrs,
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
        query.bindValue(":TV_min", dObj['TV']['min'])
        query.bindValue(":DP_min", dObj['DP']['min'])
        
        query.bindValue(":Ers_max", float(dObj['Ers']['max']))
        query.bindValue(":Rrs_max", float(dObj['Rrs']['max']))
        query.bindValue(":PEEP_max", dObj['PEEP']['max'])
        query.bindValue(":PIP_max", dObj['PIP']['max'])
        query.bindValue(":TV_max", dObj['TV']['max'])
        query.bindValue(":DP_max", dObj['DP']['max'])
        if query.exec_():
            logger.info("DB entry query successful")
        else:
            logger.error("Error: ", query.lastError().text())

    def handle_result(self,r_hourly):
        logger.info('PostProcessor.handle_result(): task finished')
        r_dialy = self.combine_allday_breath(r_hourly)
        self.populate_table(r_dialy)
        self.results.emit(r_dialy)
        self.ui.btn_PO_export.setEnabled(True)
        self.hide_pbar.emit()
        self.finished.emit()

    def combine_allday_breath(self,r_hourly):
        sum_hour, sum_Ers, sum_Rrs, sum_PEEP, sum_PIP, sum_TV, sum_DP, sum_BC, sum_FBC, sum_AI = [],[],[],[],[],[],[],[],[],[]
        E, R, PEEP_A, PIP_A, TV_A, DP_A, AI_A = [],[],[],[],[],[],[]
        for arg in r_hourly:
            sum_hour.append(arg['hour'])
            sum_Ers.append(arg['Ers'])
            sum_Rrs.append(arg['Rrs'])
            sum_PEEP.append(arg['PEEP'])
            sum_PIP.append(arg['PIP'])
            sum_TV.append(arg['TV'])
            sum_DP.append(arg['DP'])
            sum_AI.append(arg['b_type'])
            sum_BC.append(arg['b_cnt'])
            E.extend(arg['Ers'])
            R.extend(arg['Rrs'])
            PEEP_A.extend(arg['PEEP'])
            PIP_A.extend(arg['PIP'])
            TV_A.extend(arg['TV'])
            DP_A.extend(arg['DP'])
        result = {
            'p_no': r_hourly[0]['p_no'],
            'date': r_hourly[0]['date'],
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
        result['TV']['q5'],result['TV']['q25'],result['TV']['q50'],result['TV']['q75'],result['TV']['q95'] = result['TV']['q5'].astype(int) ,result['TV']['q25'].astype(int) ,result['TV']['q50'].astype(int) ,result['TV']['q75'].astype(int) ,result['TV']['q95'].astype(int)
        
        return result

    def populate_table(self,r_dialy):
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
        


    # def fetchDbData(self):
    #     sum_hour, sum_Ers, sum_Rrs, sum_PEEP, sum_PIP, sum_TV, sum_DP, sum_BC, sum_FBC, sum_AI = [],[],[],[],[],[],[],[],[],[]
    #     fname = self.fname[0].replace('.txt','')
    #     p_no = str(fname.split('_')[1])
    #     date = str(fname.split('_')[2])
    #     hour = str(fname.split('_')[3])
    #     query = QSqlQuery(f"""SELECT hour, Ers_raw, Rrs_raw, b_count, b_type,
    #                     PEEP_raw, PIP_raw, TV_raw, DP_raw  FROM results 
    #                     WHERE p_no='{p_no}' AND date='{date}';
    #                     """)
    #     query.exec_()
        
    #     while query.next():
    #         sum_hour.append(query.value(0))
    #         sum_Ers.append(json.loads(query.value(1)))
    #         sum_Rrs.append(json.loads(query.value(2)))
    #         sum_BC.append(query.value(3))
    #         sum_AI.append(json.loads(query.value(4)))
    #         sum_PEEP.append(json.loads(query.value(5)))
    #         sum_PIP.append(json.loads(query.value(6)))
    #         sum_TV.append(json.loads(query.value(7)))
    #         sum_DP.append(json.loads(query.value(8)))
    #     result = {
    #         'p_no': p_no,
    #         'date': date,
    #         'b_cnt': sum(sum_BC),
    #         'b_type': sum_AI,
    #         'hours': sum_hour,
    #         'Ers': sum_Ers,
    #         'Rrs': sum_Rrs,
    #         'PEEP': sum_PEEP,
    #         'PIP': sum_PIP,
    #         'TV': sum_TV,
    #         'DP': sum_TV
    #     }
    #     print("DB entry retrieved successful")
    #     return result