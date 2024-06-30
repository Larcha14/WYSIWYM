from joblib import load, dump
from begin_to_import import AircraftModel
import pandas as pd

data = pd.read_csv('../DATA/X_test.csv')
model = load('model.joblib')
predictions = model.predict(data,'VQ-BDU')
pos = 2
for df in predictions:
    df.to_csv(f'predict_VQ-BDU_pos_{pos}.csv', index=False)
    pos -= 1
    
#(f'predict_{aircraft}_pos_{pos}.csv', index=False)
