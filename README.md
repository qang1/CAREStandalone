# CARE_One

CARE_One is a open-source scientific software tool for mechanical ventilation patient respiratory waveform data analysis. 

It is designed to calculate respiratory mechanics of patients undergoing mechanical ventilation based on ventilator's respiratory waveform data. 

The following patient ventilatory variables were analysed: 
1. Respiratory system elastance (E<sub>rs</sub>)
2. Respiratory system resistance (R<sub>rs</sub>)
3. Positive-end-expiratory-pressure (PEEP)
4. Peak inspiratory pressure (PIP)
5. Tidal Volume (V<sub>T</sub>)
6. Asynchrony Index (AI)
7. Asynchrony Magnitude (M<sub>Asyn</sub>) 

Currently CARE_One only supports data output from Purittan Bennet 840/980 (PB-840, PB-980) ventilators, but we welcome contributions to support addition of other ventilators as well.

# Installation

The easiest way to install and run CARE_One is to download the executable file at the [Releases section](https://github.com/qang1/CAREStandalone/releases).

For a detailed guide to installing CARE_One, please refer to our [installation instructions]().


Other installation option is to compile the program from source code. To setup project environment you are strongly recommended to use the [Anaconda](https://www.anaconda.com/download/) `conda` package and environment manager.

To create new environment using `environment.yml`:

    conda env create -f environment.yml
    
Or using `requirements.txt` file:
    
    conda create --name <env_name> --file requirements.txt

# License
CARE_One is Copyright (C) 2021 CARE Trial and contributors. It is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).