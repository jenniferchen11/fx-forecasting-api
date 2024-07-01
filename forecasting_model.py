import copy
import json
import os

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from constants import NUM_FORECASTED_DAYS
from dotenv import load_dotenv
from pandas.tseries.offsets import BDay


load_dotenv()

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
DIRECTORY = os.getenv('ROOT_DIR')

class LSTM(nn.Module):
    '''
    PyTorch long short-term memory model with a single fully-connected layer
    '''
    def __init__(self, input_num_feats, hidden_size, num_layers=1, device='cpu'):
        '''
        Parameters:
            input_num_feats (int): The number of input features
            hidden_size (int): The number of features in the hidden state
            num_layers (int): The number of recurrent layers
            device (str): The device to run the model
        '''
        super(LSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        # add lstm layers
        self.lstm = nn.LSTM(
            input_num_feats,
            hidden_size,
            num_layers,
            batch_first=True)
        # add fully-connected linear layer
        self.fc = nn.Linear(hidden_size, input_num_feats)
        self.device = device

    def forward(self, x):
      # hidden state
      h0 = torch.zeros(self.num_layers, x.shape[0], self.hidden_size).to(self.device)
      #initial cell state
      c0 = torch.zeros(self.num_layers, x.shape[0], self.hidden_size).to(self.device)
      out, _ = self.lstm(x, (h0, c0))
      # filter out everything except the last timestep’s output
      out = self.fc(out[:, -1, :])
      return out


class ForexForecast:
    '''
    Class for forecasting foreign exchange rates using LSTM model
    
    Attributes:
        model_path (str): Path to the model weights
        model (LSTM): The instantiated LSTM model loaded with saved weights
    '''
    def __init__(self):
        self.model_path = f'{DIRECTORY}/trained_models/model_weights.pt'
        self.model = self.__instantiate_model_w_weights(self.model_path)
    
    def __instantiate_model_w_weights(self, model_path):
        metadata_fpath = f'{DIRECTORY}/constants/hyperparameters.json'
        f = open(metadata_fpath)
        metadata= json.load(f)

        num_cols = 1
        num_lstm_units = metadata['num_lstm_units']
        num_lstm_layers = metadata['num_lstm_layers']

        model = LSTM(num_cols, num_lstm_units, num_lstm_layers, DEVICE)
        model.to(DEVICE)
        model.load_state_dict(torch.load(model_path, map_location=torch.device(DEVICE)), assign=True)
        return model


    def __forecast_future_sequence(self, num_forecasted_days, input_data, lookback):
        prediction_list = input_data[-lookback:]
        prediction_list = prediction_list.reshape((lookback, 1))

        with torch.no_grad():
            for _ in range(num_forecasted_days):
                x = copy.deepcopy(prediction_list[-(lookback):])
                x = x.reshape((1, lookback, 1))
                x = torch.from_numpy(x)
                x = x.to(torch.float32).to(DEVICE)
                output = self.model(x)
                prediction_list = np.append(prediction_list, output.cpu().numpy(), axis=0)
            prediction_list = prediction_list[lookback:]
        return prediction_list

    def __date_forecasts(self, predictions, historical_rates, num_forecasted_days):
        historical_dates = sorted(historical_rates.keys())
        latest = historical_dates[-1]
        predictions = predictions.ravel().tolist()
        today = pd.to_datetime('today') + pd.Timedelta(days=1)

        future_dates = pd.date_range(start=today, periods=num_forecasted_days, freq=BDay()).tolist()

        preds_with_dates = {}
        for i, pred in enumerate(predictions):
            future_date = future_dates[i]
            future_date = future_date.strftime('%Y-%m-%d')
            preds_with_dates[future_date] = pred
        
        preds_with_dates[latest] = historical_rates[latest]
        return preds_with_dates


    def __format_input_data(self, historical_rates):
        input_data = [historical_rates[k] for k in sorted(historical_rates.keys())]
        lookback = len(input_data)
        input_data = np.array(input_data)
        return input_data, lookback


    def get_fx_forecast(self, historical_rates):
        input_data, lookback = self.__format_input_data(historical_rates)
        
        predictions = self.__forecast_future_sequence(NUM_FORECASTED_DAYS, input_data, lookback)
        formatted_predictions = self.__date_forecasts(predictions, historical_rates, NUM_FORECASTED_DAYS)
        return formatted_predictions
