from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error, r2_score
import numpy as np
import pandas as pd

X_train = pd.read_csv('../DATA/X_train.csv')
y_train = pd.read_csv('../DATA/y_train.csv')
class AircraftModel:
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.df = {}

    def get_train_dataset(self, X_train, y_train):
        df = X_train.merge(y_train, on=['acnum', 'pos', 'reportts'])
        cols = ['egt', 'n1a', 'n2a', 'nf', 'ff', 'mn', 't2', 'tat', 'oat', 'alt',
                'p2e', 'wai', 'nai', 'prv', 'hpv', 'xf', 'acnum', 'egtm', 'pos']
        dataset = df[cols]
        return dataset
    
    def get_dataset(self, X_test):
        cols = ['egt', 'n1a', 'n2a', 'nf', 'ff', 'mn', 't2', 'tat', 'oat', 'alt',
                'p2e', 'wai', 'nai', 'prv', 'hpv', 'xf', 'acnum', 'reportts', 'pos']
        dataset = X_test[cols]
        for acnum in dataset['acnum'].unique():
            df = dataset[dataset['acnum'] == acnum]
            self.df[acnum] = df
        dataset = dataset.drop('reportts', axis=1)
        return dataset

    def add_features(self, df):
        df['egt_ff'] = df['egt'] * df['ff']
        df['n1a_n2a'] = df['n1a'] * df['n2a']
        
        df['egt_diff_tat'] = df['egt'] - df['tat']
        df['n1a_diff_nf'] = df['n1a'] - df['nf']
        
        df['log_egt'] = np.log(df['egt'] + 1)
        df['log_ff'] = np.log(df['ff'] + 1)
        
        df['n1a_squared'] = df['n1a'] ** 2
        df['n2a_squared'] = df['n2a'] ** 2
        
        return df

    
    def train_model(self, df):
        metrics = {}
        for acnum in df['acnum'].unique():
            model_df = df[df['acnum'] == acnum]
            model_df = self.add_features(model_df)
            valid_data = model_df.drop('acnum', axis=1)
            
            scaled_data = self.scaler.fit_transform(valid_data.drop(['egtm'], axis=1))
            X_train, X_test, y_train, y_test = train_test_split(scaled_data, valid_data['egtm'], test_size=0.15)

            if acnum == 'VQ-BGU':
                model = GradientBoostingRegressor()
                param_grid = {
                    'n_estimators': [300, 400],
                    'learning_rate': [0.01, 0.1, 0.5],
                    'max_depth': [7, 10, 13],
                    'alpha': [0.1, 0.5, 0.9]
                }
                grid_model = GridSearchCV(estimator=model, param_grid=param_grid,
                                          scoring='neg_mean_squared_error', cv=5, error_score='raise')
                grid_model.fit(X_train, y_train)
                self.models[acnum] = grid_model.best_estimator_
            else:
                model = SVR()
                param_grid = {'C': [0.1, 1, 10, 100,105], 'gamma': [ 0.01, 0.015, 0.009], 'epsilon': [ 0.2, 0.5, 0.55, 0.6]}
                grid_model = GridSearchCV(estimator=model, param_grid=param_grid,
                                          scoring='neg_mean_squared_error', cv=5, error_score='raise')
                grid_model.fit(X_train, y_train)
                self.models[acnum] = grid_model.best_estimator_
            
            predictions = self.models[acnum].predict(X_test)
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape_score = mean_absolute_percentage_error(y_test, predictions)
            r2score = r2_score(y_test, predictions)
            
            metrics[acnum] = {'MAE': mae, 'RMSE': rmse, 'MAPE': mape_score, 'R2 Score': r2score}
        
        return metrics
    
    def predict(self, df, aircraft):
        df_prepared = self.get_dataset(df)
        df_cleaned = self.clear_data(df_prepared)
        df_cleaned = self.emission_processing(df_cleaned)
        df_cleaned = self.add_features(df_cleaned)
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
        predictions = results[aircraft]
        predictions = pd.DataFrame({'Predict': predictions})
        predictions = pd.concat([self.df[aircraft], predictions], axis=1)
        predictions.to_csv(f'predict_{aircraft} pos1.csv', index=False)
        predictions.to_csv(f'predict_{aircraft} pos2.csv', index=False)
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

    def emission_processing(self, df):
        limits = pd.read_excel('../DATA/PW1100 Parameters.xlsx', sheet_name='Cruise Report<01>', engine='openpyxl')
        limit_dict = {}


        for _, row in limits.iterrows():
            feature = row['alias']
            min_val = row['Min']
            max_val = row['Max']
            limit_dict[feature] = (min_val, max_val)

        for feature, (min_val, max_val) in limit_dict.items():
            if feature in df.columns:
                df.loc[df[feature] < min_val, feature] = min_val
                df.loc[df[feature] > max_val, feature] = max_val

        return df

# air = AircraftModel()
# df = air.get_train_dataset(X_train, y_train)
# df = air.clear_data(df)
# metrics = air.train_model(df)
# print(metrics)

        
