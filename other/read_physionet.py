import wfdb, os, shutil
import numpy as np
import pandas as pd
from os import listdir
import biosppy
import json

dest_path = 'datasets/ecg-id'
base_path = 'ecgiddb'

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

this_dict = dict()

def find_R_peaks(signal, fs):
    ecg = biosppy.signals.ecg.ecg(signal=signal, sampling_rate=fs, show=False)
    return ecg['rpeaks']


# read a .dat file (fs=1000) and write a .csv file (fs=500)
def get_initial_csv(ecg_name, patient, file_path):  
    # ecg_name without extension
    print(file_path+'/'+patient+'/'+ecg_name)
    record = wfdb.rdsamp(base_path+'/'+patient+'/'+ecg_name, channels=[1])
    fs = record[1]['fs']
    temp = np.ndarray.flatten(record[0])
    record = np.asarray(record[0])
    record = record[0:len(record):2, :12]
    df = pd.DataFrame(record)
    # if not os.path.exists(file_path+'/preproc_csv/'+patient):
    #     os.makedirs(file_path+'/preproc_csv/'+patient)
    df.to_csv(file_path+'/preproc_csv/'+patient[-2:]+'s'+ecg_name+'.csv', index=False, header=False)

    return find_R_peaks(temp,fs)

temp = [f for f in os.listdir('ecgiddb') if f != 'preproc_csv']

if os.path.exists(dest_path+'/preproc_csv'):
    shutil.rmtree(dest_path+'/preproc_csv')
if not os.path.exists(dest_path+'/preproc_csv'):
    os.makedirs(dest_path+'/preproc_csv')

for f in temp:
    SamplePath = base_path+"/"+f
    files = set()
    filesList = list()
    for g in listdir(SamplePath):
        files.add(g.split('.')[0])
    for i in files:
        filesList.append(i)
    
    for rec in filesList:
        this_dict[f[-2:]+'s'+rec+'.csv'] = get_initial_csv(rec, f, dest_path)

with open(dest_path+'/r_peaks.json', 'w') as fp:
    json.dump(this_dict, fp, cls=NumpyEncoder)
