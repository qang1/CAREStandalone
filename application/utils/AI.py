import os
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
from scipy.interpolate import interp1d
import numpy as np
import random
import logging

# Get the logger specified in the file
logger = logging.getLogger(__name__)

def get_current_model():
    """ Load model """
    logger.info('Now Loading The Trained Model.')
    base_path = os.path.abspath(os.path.dirname(__file__))
    model_name = 'CNNPressureClassificataion.hdf5'
    PClassiModel = load_model(os.path.join(base_path,'..\src',model_name))
    logger.info('Classification Model loaded successfully.')
    return model_name, PClassiModel
    
def predict(input_data, PClassiModel):
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