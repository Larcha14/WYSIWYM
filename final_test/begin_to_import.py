import pandas as pd
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
import numpy as np
from sklearn.preprocessing import StandardScaler
from joblib import dump,load
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor


# Прост запустим файл и модель обучена
X_train = pd.read_csv('X_train.csv', parse_dates=['reportts'])

y_train = pd.read_csv('y_train.csv', parse_dates=['reportts'])

X_test = pd.read_csv('X_test.csv',parse_dates=['reportts'])


class AircraftModel:

    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()

    def get_train_dataset(self, X_train, y_train):
        df = X_train.merge(y_train, on=['acnum', 'pos', 'reportts'])
        cols = ['egt', 'n1a', 'n2a', 'nf', 'ff', 'mn', 't2', 'tat', 'oat', 'alt',
                'p2e', 'wai', 'nai', 'prv', 'hpv', 'xf', 'acnum', 'egtm']
        dataset = df[cols]
        return dataset

    def get_dataset(self, X_test):
        cols = ['egt', 'n1a', 'n2a', 'nf', 'ff', 'mn', 't2', 'tat', 'oat', 'alt',
                'p2e', 'wai', 'nai', 'prv', 'hpv', 'xf', 'acnum']
        dataset = X_test[cols]
        return dataset

    def train_model(self, df):
        metrics = {}
        for acnum in df['acnum'].unique():
            model_df = df[df['acnum'] == acnum]
            valid_data = model_df.drop('acnum', axis=1)

            scaled_data = self.scaler.fit_transform(valid_data.drop(['egtm'], axis=1))
            X_train, X_test, y_train, y_test = train_test_split(scaled_data, valid_data['egtm'], test_size=0.2)

            if acnum == 'VQ-BGU':
                model = SVR()
                param_grid = {'C': [0.1, 1, 10, 100], 'gamma': [1, 0.1, 0.01, 0.001]}
                grid_model = GridSearchCV(estimator=model, param_grid=param_grid,
                                          scoring='neg_mean_squared_error', cv=5, error_score='raise')
                grid_model.fit(X_train, y_train)
                self.models[acnum] = grid_model.best_estimator_

            elif acnum == 'VQ-BDU':
                model = GradientBoostingRegressor()
                param_grid = {'n_estimators': [100, 200, 300],
                              'learning_rate': [0.01, 0.1, 0.5],
                              'max_depth': [3, 5, 7]}
                grid_model = GridSearchCV(estimator=model, param_grid=param_grid,
                                          scoring='neg_mean_squared_error', cv=5, error_score='raise')
                grid_model.fit(X_train, y_train)
                self.models[acnum] = grid_model.best_estimator_



            else:
                raise ValueError(f"No such aircraft {acnum}")

            predictions = self.models[acnum].predict(X_test)
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape_score = mean_absolute_percentage_error(y_test, predictions)
            r2score = r2_score(y_test, predictions)

            metrics[acnum] = {'MAE': mae, 'RMSE': rmse, 'MAPE': mape_score, 'R2 Score': r2score}

        return metrics

    def predict(self, df):
        df_prepared = self.get_dataset(df)
        df_cleaned = self.clear_data(df_prepared)

        results = {}
        for acnum in df_cleaned['acnum'].unique():
            model = self.models.get(acnum)
            if model:
                X_test = df_cleaned[df_cleaned['acnum'] == acnum].drop('acnum', axis=1)

                scaled_X_test = self.scaler.transform(X_test)

                predictions = model.predict(scaled_X_test)
                results[acnum] = predictions
            else:
                raise ValueError(f"No predictions stored for aircraft model {acnum}")
        return results

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


air = AircraftModel()

df = air.get_train_dataset(X_train, y_train)

df = air.clear_data(df)

air.train_model(df)
