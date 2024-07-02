import sys
import os
import pandas as pd
from joblib import load
from begin_to_import import AircraftModel

def main(file_path, output_dir, aircraft, linkname, created_at_str):
    
    model = load(os.path.join('app', 'models', 'model.joblib'))

    data = pd.read_csv(file_path)
    os.makedirs(output_dir, exist_ok=True)

    positions = data['pos'].unique()

    for pos in positions:
        pred_for_pos = model.predict(data[data['pos'] == pos], aircraft)
        
        for i, df in enumerate(pred_for_pos):
            output_file = os.path.join(output_dir, f'{linkname}-{aircraft}-{created_at_str}-pos{pos}.csv')
            df.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python example_import.py <file_path> <output_dir> <aircraft> <linkname>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2]
    aircraft = sys.argv[3]
    linkname = sys.argv[4]
    created_at_str = sys.argv[5]
    main(file_path, output_dir, aircraft, linkname, created_at_str)
