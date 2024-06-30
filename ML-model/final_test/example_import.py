from joblib import load
from begin_to_import import AircraftModel
import pandas as pd

data = pd.read_csv('../DATA/X_test.csv')
model = load('model.joblib')
aircraft = 'VQ-BGU'
predictions = model.predict(data, aircraft)

positions = data['pos'].unique()

for pos in positions:
    
    pred_for_pos = model.predict(data[data['pos'] == pos], aircraft)
    
    for i, df in enumerate(pred_for_pos):
        df.to_csv(f'predict_{aircraft}_pos_{pos}_part_{i+1}.csv', index=False)
