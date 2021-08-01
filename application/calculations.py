# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 11:06:47 2021

@author: ngqin
"""

import numpy as np
from scipy import integrate
import math

class Elastance():


    def calcRespMechanics(self,path):
        """Responsible for opening text file, extracting breath number,
            splitting pressure and flow data, data filtering, and combine
            all metrics together.

        Args:
            path (string): file path

        Returns:
            P, Q, P_A, Q_A, Ers_A, Rrs_A, b_count, PEEP_A, PIP_A, TV_A, DP_A, b_num_all
        """
        pressure, flow, b_num_all, b_len, b_check = [], [], [], [], []
        P, Q, Ers_A, Rrs_A, P_A, Q_A, PEEP_A, PIP_A, TV_A, DP_A = [],[],[],[],[],[],[],[],[],[]
        b_count = 0
        with open(path, "r") as f:
            for line in f:
                if ("BS," in line) == True:
                    b_num = self._extractBNum(line)
                elif ("BE" in line) == True:
                    if (len(pressure) >= 50) and (len(pressure) == len(flow)):
                        E, R, PEEP, PIP, TidalVolume, _, _ = self.get_r(pressure, flow, True) # calculate respiratory parameter 
                    
                        if (abs(E)<100) & (abs(R)<100) & (TidalVolume<1):
                            b_count += 1
                            b_len.append(len(pressure))
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
                            b_num_all.append(b_num)
                        else:
                            pass
                    else:
                        pass
                    pressure, flow = [], [] # reset temp list
                else:
                    if line != '': # Filter out empty lines
                        section = line.split(',') # 2.34, 5.78 -> ['2.34','5.78']
                        try:
                            p_split = float(section[1])
                            q_split = float(section[0])
                                
                            if abs(p_split) <= 100 and abs(q_split) <= 1000:
                                if len(pressure) > 1:
                                    if abs(p_split-pressure[-1]) <= 50 and abs(q_split-flow[-1]) <= 50:
                                        pressure.append(round(p_split,1))
                                        flow.append(round(q_split,1))
                                else:
                                    pressure.append(round(p_split,1))
                                    flow.append(round(q_split,1))
                        except:
                            pass
        return P, Q, P_A, Q_A, Ers_A, Rrs_A, b_count, PEEP_A, PIP_A, TV_A, DP_A, b_num_all, b_len
    
    def _get_V(self,Q):
        b_points = np.size(Q)
        Time = list(np.linspace(0, (b_points-1)*0.02, b_points))
        return integrate.cumtrapz(Q, x=Time, initial=0)


    def _seperate_breath(self,temp_pressure,temp_flow):
        # add 5 data points in future so that will avoid the 1st digit as negative
        Fth = 5
        flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1] <= 0)
        flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]

        while (len(flow_inspi) <= 10):
            # print(len(flow_head))
            # add 5 data points in future so that will avoid the 1st digit as negative
            flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1] <= 0)
            flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]
            Fth = Fth + 1

        # add 5 data points in future so that will avoid the 1st digit as negative
        flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1] <= 0)
        flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]

        flow_expi = temp_flow[flow_inspi_loc_ends+1+Fth::]
        flow_expi_loc_starts = np.argmin(flow_expi)
        flow_expi = flow_expi[flow_expi_loc_starts::]

        # % Pressure Inspiration and expiration
        pressure_inspi = temp_pressure[0:flow_inspi_loc_ends+Fth]
        pressure_expi = temp_pressure[flow_inspi_loc_ends+1+Fth::]
        # pressure_expi_T = pressure_expi[flow_expi_loc_starts::]

        return flow_inspi,flow_expi,pressure_inspi,pressure_expi


    def get_r(self,P,Q,useIM):
        temp_flow = np.array(Q)/60
        temp_pressure = P

        # get maximum pressure pip
        PIP = max(temp_pressure)

        flow_inspi,flow_expi,pressure_inspi,pressure_expi = self._seperate_breath(temp_pressure,temp_flow)
        

        b_points = np.size(pressure_inspi)
        Time = list(np.linspace(0, (b_points-1)*0.02, b_points))

        expi_b_points = np.size(flow_expi)
        expi_Time = list(np.linspace(0, (expi_b_points-1)*0.02, expi_b_points))

        b_points_total = np.size(temp_pressure)
        total_time = list(np.linspace(0, (b_points_total-1)*0.02, b_points_total))
        
        # get PEEP
        # PEEP = np.array(pressure_inspi[0]) #use first inspi point as peep
        PEEP_non_array = math.floor(min(pressure_expi))
        PEEP = np.array(PEEP_non_array)  # use expi min as peep
        
        V = integrate.cumtrapz(flow_inspi, x=Time, initial=0)
        V_expi = integrate.cumtrapz(flow_expi, x=expi_Time, initial=0)
        V_total = integrate.cumtrapz(temp_flow, x=total_time, initial=0)+0.000001

        if useIM:
            # Using Integral method, reintegrate to reduce noise
            int_V = integrate.cumtrapz(V, x=Time, initial=0)
            int_Q = integrate.cumtrapz(flow_inspi, x=Time, initial=0)
            int_B = integrate.cumtrapz(pressure_inspi-PEEP, x=Time, initial=0)

            # Constructing Ax=B to obtain Ers and R
            A = np.vstack((int_V, int_Q)).T  # Transpose
            B = int_B
        else:
            # Constructing Ax=B to obtain Ers and R
            A = np.vstack((V, flow_inspi)).T  # Transpose
            B = pressure_inspi-PEEP
        
        # from scipy.optimize import nnls
        # Ers, Rrs, = nnls(A, B)[0]

        # linear algebra method to return least square solution
        Ers, Rrs, = np.linalg.lstsq(A, B, rcond=-1)[0]

        # round Ers, Rrs to one decimal point
        Ers = np.around(Ers,1)
        Rrs = np.around(Rrs,1)

        TidalVolume = max(V)
        # PEEP_non_array = pressure_inspi[0]
        # PEEP_non_array = min(pressure_expi)
        # Round to nearest 0.5 reso
        # PEEP_non_array = round(PEEP_non_array * 2) / 2
        IE = len(flow_expi)/len(flow_inspi)
        VE = abs(min(V_expi))

        # Limit Rrs to zero, remove negative value
        if Rrs < 0:
            Rrs = 0

        return Ers, Rrs, PEEP_non_array, PIP, TidalVolume, IE, VE

    def _extractBNum(self,line):
        # Gets current breath number for debug, Returns 0000 when failed.
        try:
            b_num = [int(s) for s in line.replace(',\n','').split(':') if s.isdigit()][0]
        except:
            try:
                b_num = [int(s) for s in line.replace(',\r\n','').split(':') if s.isdigit()][0]
            except:
                try:
                    b_num = [int(s) for s in line.replace(',','').split(':') if s.isdigit()][0]
                except:
                    b_num = 0000
        return b_num

def _calcQuartiles(E, R, PEEP_A, PIP_A, TV_A, DP_A):
    """ Calc quartiles """
    TV_A = [int(x) for x in TV_A]
    params = ['Ers','Rrs','PEEP','PIP','TV','DP']
    paramsVal = [E, R, PEEP_A, PIP_A, TV_A, DP_A]
    rounding = [1,1,1,1,0,1]
    dObj = {
        'Ers':{},
        'Rrs':{},
        'PEEP':{},
        'PIP':{},
        'TV':{},
        'DP':{},
    }
    for i in range(len(params)):
        dObj[params[i]]['q5'],dObj[params[i]]['q25'],dObj[params[i]]['q50'],dObj[params[i]]['q75'],dObj[params[i]]['q95'] = np.around(np.nanquantile(paramsVal[i],[.05,.25,.50,.75,.95]),rounding[i])
        dObj[params[i]]['min'] = round(min(paramsVal[i]),rounding[i])
        dObj[params[i]]['max'] = round(max(paramsVal[i]),rounding[i])
    # chg to int to rmv rounding digit
    # dObj['TV']['q5'],dObj['TV']['q25'],dObj['TV']['q50'],dObj['TV']['q75'],dObj['TV']['q95'] = dObj['TV']['q5'].astype(int) ,dObj['TV']['q25'].astype(int) ,dObj['TV']['q50'].astype(int) ,dObj['TV']['q75'].astype(int) ,dObj['TV']['q95'].astype(int)
    
    return dObj



