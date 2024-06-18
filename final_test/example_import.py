# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
from joblib import load, dump
from begin_to_import import AircraftModel
import pandas as pd
data = pd.read_csv('../DATA/X_test.csv')
model = load('model.joblib')
predictions = model.predict(data)
