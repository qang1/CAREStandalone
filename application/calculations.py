# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 11:06:47 2021

@author: ngqin
"""

import numpy as np
from scipy import integrate
import math

class Elastance():

    
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