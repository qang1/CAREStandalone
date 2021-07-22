import os
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
from scipy.interpolate import interp1d
import numpy as np
import random
import logging
from pathlib import Path
from scipy import trapz

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
    # print(f': {magAB}')

    # plt.figure()
    # plt.plot(temp)
    # plt.plot(reconstructed)
    # plt.savefig(f'fig/{cnt}.png')

    
    return magAB