import os
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
from scipy.interpolate import interp1d
import numpy as np
import random
import logging
import json
from PyQt5.QtSql import  QSqlQuery
from pathlib import Path
from scipy import trapz

from calculations import _calcQuartiles

# Get the logger specified in the file
logger = logging.getLogger(__name__)

base_path = os.path.abspath(os.path.dirname(__file__))


def get_current_model():
    """ Load model """
    logger.info('Now Loading The Trained Model.')
    model_name = 'CNNPressureClassificataion.hdf5'
    PClassiModel = load_model(os.path.join(base_path,'..\src',model_name))
    logger.info('Classification Model loaded successfully.')
    return model_name, PClassiModel
    
def AIpredict(input_data, PClassiModel):
    seed_value = 7
    random.seed(seed_value)
    np.random.seed(seed_value)
    data_size = 150
    input_data = np.array(input_data) # convert into array
    input_data = (input_data - min(input_data))/max(input_data - min(input_data)) #normalise data
    
    x = np.arange(0,(input_data).size)
    new_x = np.arange(0,input_data.size-1,input_data.size/data_size) 
    input_data = np.transpose(interp1d(x,input_data)(new_x))
    input_data = input_data.reshape(len(input_data),1)
    input_data = pad_sequences(np.transpose(input_data),maxlen=data_size,dtype= 'float64',padding='post', truncating='post', value = (input_data)[-1])
    preprocessed_data = input_data.reshape(data_size)
    
    Preds = PClassiModel.predict(preprocessed_data.reshape(1,150,1)) # this line classifies the type of breathing cycle
    out = np.argmax(Preds)
    
    if out == 0: # Normal
        return('Normal')
    elif out == 1: # Asyn
        return('Asyn')
    elif out == 2: #noise
        return('Normal')
    else: 
        return('Normal')

def norma_resample(input_data, data_size):
    input_data = np.array(input_data) # convert into array
    input_data = (input_data - min(input_data))/max(input_data - min(input_data))
    x = np.arange(0,(input_data).size)
    new_x = np.arange(0,input_data.size-1,input_data.size/data_size)
    input_data = np.transpose(interp1d(x,input_data.reshape(len(input_data)))(new_x))
    input_data = input_data.reshape(len(input_data),1)
    input_data = pad_sequences(np.transpose(input_data),maxlen=data_size,dtype= 'float64',padding='post', truncating='post', value = (input_data)[-1])
    immatrix_p = input_data.reshape(data_size)
    return immatrix_p

def load_Recon_Model():
    model_name = 'best_model1.hdf5'
    ReconModel = load_model(os.path.join(base_path,'..\src',model_name))
    return ReconModel

def recon(flow,temp_pressure,ReconModel):
    """Predict Asynchrony magnitude using pressure reconstruction

    Args:
        flow (list): flow
        temp_pressure (list): pressure list
        ReconModel ([type]): reconstruction trained model

    Returns:
        magAI: Asynchrony magnitude
    """
    random.seed(7)
    np.random.seed(7)
    temp_flow = np.array(flow)/60
    Fth = 5

    flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1]<= 0) # add 5 data points in future so that will avoid the 1st digit as negative
    flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]
    
    while (len(flow_inspi) <= 10):
        #print(len(flow_head))
        flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1]<= 0) # add 5 data points in future so that will avoid the 1st digit as negative
        flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]
        Fth = Fth +1
    
    flow_inspi_loc_ends = np.argmax(temp_flow[1+Fth:-1]<= 0) # add 5 data points in future so that will avoid the 1st digit as negative
    flow_inspi = temp_flow[0:flow_inspi_loc_ends+Fth]
    
    flow_expi = temp_flow[flow_inspi_loc_ends+1+Fth::]
    flow_expi_loc_starts = np.argmin(flow_expi)
    flow_expi = flow_expi[flow_expi_loc_starts::]
    
    #% Pressure Inspiration and expiration
    pressure_inspi = temp_pressure[0:flow_inspi_loc_ends+Fth]
    
    temp = norma_resample(pressure_inspi,64)
    
    reconstructed = ReconModel.predict(temp.reshape(1,64,1))
    reconstructed = reconstructed.reshape(64) # Normalized output (0-1)

    Error = max((temp.reshape(64,) - reconstructed.reshape(64,)))
    reconstructed = reconstructed +Error
    max_recon = max(reconstructed)
    reconstructed = reconstructed/max_recon # to normalize
    normalized_AB = temp.reshape(64,)/max_recon
    VI = 1 - (abs(trapz(reconstructed) - trapz(normalized_AB)))/trapz(reconstructed) # VI metric
    magAB = (abs(trapz(reconstructed) - trapz(normalized_AB)))/trapz(reconstructed) *100 #Magnitude of AB
    magAB = np.around(magAB,2)
    
    if not np.isnan(magAB):
        return magAB
    else:
        return np.nan

def saveDb(db, P, Q, Ers, Rrs, b_count, b_type, PEEP, PIP, TV, DP, AImag, b_num_all, b_len, p_no, date, hour):
        
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
    b_num_all = json.dumps(b_num_all)
    b_len = json.dumps(b_len)

    Norm_cnt = b_type.count('Normal')
    Asyn_cnt = b_type.count('Asyn')
    AI_index = round(Asyn_cnt/(Asyn_cnt+Norm_cnt)*100,2)

    query = QSqlQuery(db)
    query.prepare(f"""INSERT INTO results (p_no, date, hour, p, q, b_count, b_type, b_num_all, b_len,
                    Ers_raw, Rrs_raw, PEEP_raw, PIP_raw, TV_raw, DP_raw, AM_raw,
                    Ers_q5,  Rrs_q5,  PEEP_q5,  PIP_q5,  TV_q5,  DP_q5,
                    Ers_q25, Rrs_q25, PEEP_q25, PIP_q25, TV_q25, DP_q25,
                    Ers_q50, Rrs_q50, PEEP_q50, PIP_q50, TV_q50, DP_q50,
                    Ers_q75, Rrs_q75, PEEP_q75, PIP_q75, TV_q75, DP_q75,
                    Ers_q95, Rrs_q95, PEEP_q95, PIP_q95, TV_q95, DP_q95,
                    Ers_min, Rrs_min, PEEP_min, PIP_min, TV_min, DP_min,
                    Ers_max, Rrs_max, PEEP_max, PIP_max, TV_max, DP_max,
                    AI_Norm_cnt, AI_Asyn_cnt, AI_Index) 
                    VALUES (:p_no, :date, :hour, :p, :q, :b_count, :b_type, :b_num_all, :b_len,
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
    query.bindValue(":b_num_all", b_num_all)
    query.bindValue(":b_len", b_len)
    
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