HYPERPARAMS = {
    'learning_rate': 0.001, 
    'batch_size': 512, 
    'num_lstm_layers': 3, 
    'num_lstm_units': 100, 
    'dropout_rate': 0.2, 
    'weight_decay': 0.0, 
    'model_architecture': 'lstm'
}

CURRENCIES = [
    'CAD',
    'CNY',
    'GBP',
    'HKD',
    'JPY',
    'KRW',
    'TWD',
    'USD',
]

NUM_FORECASTED_DAYS = 14