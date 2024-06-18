import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
import numpy as np
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split, GridSearchCV
import xgboost as xgb


X_train = pd.read_csv('../DATA/X_train.csv', parse_dates=['reportts'])
y_train = pd.read_csv('../DATA/y_train.csv', parse_dates=['reportts'])

class AircraftModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def get_train_dataset(self, X_train, y_train):
        df = X_train.merge(y_train, on=['acnum', 'pos', 'reportts'])
        cols = ['egt', 'n1a', 'n2a', 'nf', 'ff', 'mn', 't2', 'tat', 'oat', 'alt',
                'p2e', 'wai', 'nai', 'prv', 'hpv', 'xf', 'egtm']
        dataset = df[cols]
        return dataset

    def get_dataset(self, X_test):
        cols = ['egt', 'n1a', 'n2a', 'nf', 'ff', 'mn', 't2', 'tat', 'oat', 'alt',
                'p2e', 'wai', 'nai', 'prv', 'hpv', 'xf']
        dataset = X_test[cols]
        return dataset

    def percent_missing(self, df):
        percent_nan = (df.isnull().sum() / len(df)) * 100
        return percent_nan[percent_nan > 0].sort_values()

    def clear_data(self, df):
        percent_miss = self.percent_missing(df)
        columns_to_drop = percent_miss[percent_miss > 95].index
        df = df.drop(columns=columns_to_drop)
        columns_to_fill = percent_miss[(percent_miss > 0) & (percent_miss <= 5)].index
        for column in columns_to_fill:
            df[column].fillna(df[column].median(), inplace=True)
        return df

    def add_features(self, df):
        
        df['egt_ff'] = df['egt'] * df['ff']
        df['n1a_n2a'] = df['n1a'] * df['n2a']

        
        df['mean'] = df.mean(axis=1)
        df['std'] = df.std(axis=1)

        return df

    def train_model(self, df):
        df = self.add_features(df)
        valid_data = df.drop('egtm', axis=1)
        scaled_data = self.scaler.fit_transform(valid_data)
        X = scaled_data
        y = df['egtm']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
      
        model = xgb.XGBRegressor()
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1],
            'max_depth': [3, 4, 5],
            'subsample': [0.8, 0.9, 1.0],
            'alpha': [0, 0.1, 0.5, 1],  
            'lambda': [1, 1.5, 2]  
        }
        grid_model = GridSearchCV(estimator=model, param_grid=param_grid,
                                  scoring='neg_mean_squared_error', cv=5, error_score='raise')
        grid_model.fit(X_train, y_train)
        self.model = grid_model.best_estimator_
        predictions = self.model.predict(X_test)
        
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mape_score = mean_absolute_percentage_error(y_test, predictions)
        r2score = r2_score(y_test, predictions)
        
        metrics = {'MAE': mae, 'RMSE': rmse, 'MAPE': mape_score, 'R2 Score': r2score}
        return metrics

    def predict(self, df):
        df_prepared = self.get_dataset(df)
        df_cleaned = self.clear_data(df_prepared)
        df_features = self.add_features(df_cleaned)

        if self.model:
            scaled_X_test = self.scaler.transform(df_features)
            predictions = self.model.predict(scaled_X_test)
            predictions = pd.DataFrame({'predict': predictions})
            predictions.to_csv('predict.csv', index=False)
            return predictions
        else:
            raise ValueError("No model trained yet")


# air = AircraftModel()
df = air.get_train_dataset(X_train, y_train)
df = air.clear_data(df)
print(df.head())
# metrics = air.train_model(df)
# print(metrics)
