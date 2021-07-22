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
from utils.AI import get_current_model, AIpredict, load_Recon_Model, recon

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
        self.open_pbar.emit()
        self.updateStatus()
        no_results, sum_results = [], []
        
        # For each file in directory, fetch data from db if exists.
        # If not, append filename to no_results list to process.
        for f in self.fname:
            try:
                dObj = self.fetchDb(f)
                sum_results.append(dObj)
            except:
                no_results.append(f)

        # If there is filename not exist in db, calc resp mechanics,
        # followed by breath prediction and reconstruction. Finaly,
        # Save results individually in db.
        if len(no_results) != 0:
            new_results = []
            for f in no_results:
                dObj = self.fun(f)
                new_results.append(dObj)
            new_results = self._get_prediction(new_results)
            new_results = self._get_recon(new_results)
            self.saveResults(new_results)
            
            # insert new results to sum results and sort by hour
            sum_results.extend(new_results)
            sum_results = sorted(sum_results, key=lambda k: k['hour'])

        # Plot in 30 minutes to increase trend detail
        chopHalf = self.settings.value('resolution') == '30mins'
        if chopHalf == True:
            logging.info(f'Plot resolution (30mins): {chopHalf}')
            sum_results = self.calcHalf(sum_results)

        # Finalize, process, and display data
        self.handle_result(sum_results)

    
    def updateStatus(self):
        perCmpl = round(self.cnt/self.total*100,2)
        self.update_mainpbar.emit(perCmpl,f"Total: Processing file {self.cnt}/{self.total}")
        self.cnt += 1
        logger.info(f"Processing file {self.cnt}/{self.total}")

    def updateBarStatus(self,cnt,total):
        perCmpl = round(cnt/total*100,2)
        self.update_mainpbar.emit(perCmpl,f"Total: Processing file {cnt}/{total}")
        logger.info(f"Processing file {cnt}/{total}")

    def fetchDb(self,f):
        _, p_no, date, hour = f.replace('.txt','').split('_')
        logger.info(f'DB lookup.Params - p_no: {p_no}; date: {date}; hour: {hour}')
        query = QSqlQuery(self.db)
        query.exec(f"""SELECT p, q, Ers_raw, Rrs_raw, b_count, b_type,
                        PEEP_raw, PIP_raw, TV_raw, DP_raw, AM_raw  FROM results 
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
            AM_raw = json.loads(query.value(10))
            logger.info('DB entry found. Breath count: %s', b_count)

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
                'b_count': b_count,
                'b_type': b_type,
                'AImag': AM_raw
            }
            return dObj
        else:
            logger.warning(f'No db found. DEBUG: query.next() false')
            logger.warning(f'{self.db.lastError().text()}')
            raise Exception

    def calcHalf(self,input_results):
        """
        Seperates incoming dictionary of 1 hour input results
        to 30 minutes interval. Splits half by breath count.
            
        *Assume there is complete number of breath in an hour.

        Args:
            input_results (list): list of dictionaries [{'01-00-00'},{02-00-00},...]

        Returns:
            sum_results: list of output results [{'01-00-00'},{01-30-00},...]
        """
        sum_results = []
        for i in input_results:
            # Split into half
            middle_index = i['b_count']//2

            # First half    
            Firsthalf_dObj = {
                'p_no': i['p_no'],
                'date': i['date'],
                'hour': i['hour'],
                'Ers': i['Ers'][:middle_index],
                'Rrs': i['Rrs'][:middle_index],
                'PEEP': i['PEEP'][:middle_index],
                'PIP': i['PIP'][:middle_index],
                'TV': i['TV'][:middle_index],
                'DP': i['DP'][:middle_index],
                'b_type': i['b_type'][:middle_index],
                'AImag': i['AImag'][:middle_index],
                'b_count': i['b_count']
            }
            sum_results.append(Firsthalf_dObj)

            # Second half    
            hour_half = f'{i["hour"].split("-")[0]}-30-00' # 01-30-00

            Secondhalf_dObj = {
                'p_no': i['p_no'],
                'date': i['date'],
                'hour': hour_half,
                'Ers': i['Ers'][middle_index:],
                'Rrs': i['Rrs'][middle_index:],
                'PEEP': i['PEEP'][middle_index:],
                'PIP': i['PIP'][middle_index:],
                'TV': i['TV'][middle_index:],
                'DP': i['DP'][middle_index:],
                'b_type': i['b_type'][middle_index:],
                'AImag': i['AImag'][middle_index:],
                'b_count': i['b_count']
            }

            sum_results.append(Secondhalf_dObj)
        return sum_results

    def fun(self,arg):
        self.update_subpbar.emit(10,f"Processing file {arg}")
        path = self.dirSelected + '/' + arg
        _, p_no, date, hour = arg.replace('.txt','').split('_')
        try:
            # Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A = self.fetchDb(p_no,date,hour)
            1/0
        except:
            logger.info(f'Calculating results... {arg}')
            self.update_subpbar.emit(20,f"Calculating results... {arg}")
            f = open(path, "r")
            pressure, flow, b_type = [], [], []
            P, Q, Ers_A, Rrs_A, PEEP_A, PIP_A, TV_A, DP_A = [], [], [], [], [], [], [], []
            P_A, Q_A = [], []
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
                            P_A.append(pressure)
                            Q_A.append(flow)
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
            # self.saveDb(P, Q, Ers_A, Rrs_A, b_count, b_type, PEEP_A, PIP_A, TV_A, DP_A, arg)
            
        dObj = {
            'p_no': p_no,
            'date': date,
            'hour': hour,
            'P': P,
            'Q': Q,
            'pressure': P_A,
            'flow': Q_A,
            'Ers': Ers_A,
            'Rrs': Rrs_A,
            'PEEP': PEEP_A,
            'PIP': PIP_A,
            'TV': TV_A,
            'DP': DP_A,
            'b_count': b_count
        }

        self.updateStatus()
        
        return dObj

   
    def _get_prediction(self,sum_results):

        logger.info(f'Loading model...')
        self.update_subpbar.emit(40,f'Loading model...')
        model_name, self.PClassiModel = get_current_model()
        total_cnt = len(sum_results)
        for cnt, dObj in enumerate(sum_results):
            
            b_type = []
            logger.info(f'Starting breath prediction...{dObj["hour"]}')
            self.update_subpbar.emit(40,f'Predicting breath ...{dObj["hour"]}')
            self.updateBarStatus(cnt,total_cnt)
            logger.info(len(dObj["pressure"]))
            for p in dObj["pressure"]:
                b_type.append(AIpredict(p, self.PClassiModel))
            sum_results[cnt]["b_type"] = b_type
                    
            logger.info('Breath prediction completed.')
        # except Exception as e:
            # logger.error(f'{e}')
        return sum_results

    def _get_recon(self,sum_results):

        logger.info(f'Loading recon model...')
        self.update_subpbar.emit(50,f'Loading recon model...')
        reconModel = load_Recon_Model()
        total_cnt = len(sum_results)

        for cnt, dObj in enumerate(sum_results):
            AImag = []
            self.updateBarStatus(cnt,total_cnt)
            logger.info(f'Starting breath recon ...{dObj["hour"]}')
            self.update_subpbar.emit(60,f'Starting breath recon ...{dObj["hour"]}')

            for idx, p in enumerate(dObj["pressure"]):
                flow = dObj["pressure"][idx]
                AImag.append(recon(flow, p, reconModel))
            dObj["AImag"] = AImag
            
        logger.info('Breath recon prediction completed.')
        self.update_subpbar.emit(100,f'Processing complete. Populating result...')
        return sum_results

    def saveResults(self,sum_results):
        for results in sum_results:
            P = results['P']
            Q = results['Q']
            Ers = results['Ers']
            Rrs = results['Rrs']
            b_count = results['b_count']
            b_type = results['b_type']
            PEEP = results['PEEP']
            PIP = results['PIP']
            TV = results['TV']
            DP = results['DP']
            AImag = results['AImag']
            p_no = results['p_no']
            date = results['date']
            hour = results['hour']
            self.saveDb(P, Q, Ers, Rrs, b_count, b_type, PEEP, PIP, TV, DP, AImag, p_no, date, hour)

    def saveDb(self, P, Q, Ers, Rrs, b_count, b_type, PEEP, PIP, TV, DP, AImag, p_no, date, hour):
        
        dObj = _calcQuartiles(Ers, Rrs, PEEP, PIP, TV, DP)

        # Encoding python object to json
        p = json.dumps(P)
        q = json.dumps(Q)
        Ers_raw = json.dumps(Ers)
        Rrs_raw = json.dumps(Rrs)
        PEEP_raw = json.dumps(PEEP)
        PIP_raw = json.dumps(PIP)
        TV_raw = json.dumps(TV)
        DP_raw = json.dumps(DP)
        AM_raw = json.dumps(AImag)
        b_type_encoded = json.dumps(b_type)

        Norm_cnt = b_type.count('Normal')
        Asyn_cnt = b_type.count('Asyn')
        AI_index = round(Asyn_cnt/(Asyn_cnt+Norm_cnt)*100,2)

        query = QSqlQuery(self.db)
        query.prepare(f"""INSERT INTO results (p_no, date, hour, p, q, b_count, b_type,
                        Ers_raw, Rrs_raw, PEEP_raw, PIP_raw, TV_raw, DP_raw, AM_raw,
                        Ers_q5,  Rrs_q5,  PEEP_q5,  PIP_q5,  TV_q5,  DP_q5,
                        Ers_q25, Rrs_q25, PEEP_q25, PIP_q25, TV_q25, DP_q25,
                        Ers_q50, Rrs_q50, PEEP_q50, PIP_q50, TV_q50, DP_q50,
                        Ers_q75, Rrs_q75, PEEP_q75, PIP_q75, TV_q75, DP_q75,
                        Ers_q95, Rrs_q95, PEEP_q95, PIP_q95, TV_q95, DP_q95,
                        Ers_min, Rrs_min, PEEP_min, PIP_min, TV_min, DP_min,
                        Ers_max, Rrs_max, PEEP_max, PIP_max, TV_max, DP_max,
                        AI_Norm_cnt, AI_Asyn_cnt, AI_Index) 
                        VALUES (:p_no, :date, :hour, :p, :q, :b_count, :b_type,
                        :Ers_raw, :Rrs_raw, :PEEP_raw, :PIP_raw, :TV_raw, :DP_raw, :AM_raw,
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
        query.bindValue(":b_type", b_type_encoded)
        query.bindValue(":Ers_raw", Ers_raw)
        query.bindValue(":Rrs_raw", Rrs_raw)
        query.bindValue(":PEEP_raw", PEEP_raw)
        query.bindValue(":PIP_raw", PIP_raw)
        query.bindValue(":TV_raw", TV_raw)
        query.bindValue(":DP_raw", DP_raw)
        query.bindValue(":AM_raw", AM_raw)
        
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
            dObj (list): [description]

        Returns:
            result [dict]: [description]
        """
        sum_hour, sum_Ers, sum_Rrs, sum_PEEP, sum_PIP, sum_TV, sum_DP, sum_BC, sum_AI, sum_mag = [],[],[],[],[],[],[],[],[],[]
        E, R, PEEP_A, PIP_A, TV_A, DP_A = [],[],[],[],[],[]
        for arg in dObj:
            sum_hour.append(arg['hour'])
            sum_Ers.append(arg['Ers'])
            sum_Rrs.append(arg['Rrs'])
            sum_PEEP.append(arg['PEEP'])
            sum_PIP.append(arg['PIP'])
            sum_TV.append(arg['TV'])
            sum_DP.append(arg['DP'])
            sum_BC.append(arg['b_count'])
            sum_AI.append(arg['b_type'])
            sum_mag.append(arg['AImag'])

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
            'b_count': sum(sum_BC),
            'Ers': {},
            'Rrs': {},
            'PEEP': {},
            'PIP': {},
            'TV': {},
            'DP': {},
            'b_type': sum_AI,
            'AImag': {'raw':sum_mag}
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
                self.ui.poPEEPWidget.canvas,self.ui.poVtWidget.canvas,self.ui.poDpWidget.canvas,
                self.ui.poAMWidget.canvas]
        y_labels = [r'$cmH_2O/l$',r'$cmH_2Os/l$',r'$cmH_2O$',r'$cmH_2O$','ml',r'$cmH_2O$','%']
        xaxis = [res['hours'][i][0:5].replace('-','') for i in range(len(res['hours']))]
        params = ['Ers','Rrs','PEEP','PIP','TV','DP','AImag']

        if len(xaxis) > 12:
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

        if len(xaxis) > 12:
            rot_angle = 45
        else:
            rot_angle = 0
        
        self.ui.poAIWidget.canvas.ax.bar(x=xaxis, height=Norm_perc, width=0.35, label='Normal')
        bars = self.ui.poAIWidget.canvas.ax.bar(x=xaxis, height=Asyn_perc, width=0.35, bottom=Norm_perc, label='Asynchrony')
        self.ui.poAIWidget.canvas.ax.set_xlabel('Hour (24-hour notation)')
        self.ui.poAIWidget.canvas.ax.set_ylabel('Asynchrony Index (%)')
        self.ui.poAIWidget.canvas.ax.set_ylim([0,110])
        self.ui.poAIWidget.canvas.ax.legend(loc=1)
        self.ui.poAIWidget.canvas.ax.set_xticklabels(xaxis, rotation = rot_angle)
        self.ui.poAIWidget.canvas.draw()
        self.ui.poAIWidget.canvas.fig.set_size_inches(14,4)
        self.ui.poAIWidget.canvas.fig.savefig(f'{self.dirSelected}/AI.png', dpi=300)

        for idx, bar in enumerate(bars):
            self._update_annot(bar,Asyn_perc[idx])

    def _update_annot(self,bar,val):
        x = bar.get_x()+bar.get_width()/2.
        y = bar.get_y()+bar.get_height()
        text = "AI: {:.2g}".format( val )
        annot = self.ui.poAIWidget.canvas.ax.annotate(text, xy=(x,y), xytext=(-20,2),textcoords="offset points")

