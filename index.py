from flask import Flask, jsonify, request
from flask_cors import CORS

from forex_query_handler import ForexQueryHandler

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    '''
    Root endpoint of the Flask server

    Returns:
        str: A message indicating the server has started
    '''
    return 'Flask server started'

@app.route('/api/get-forex-rates', methods=['GET'])
def get_forex_rates():
    '''
    Endpoint to get current and historical forex rates, with an optional forecast

    Parameters:
        from (str): The currency code to convert from
        to (str): The currency code to convert to
        performForecast (str): Whether to perform a forecast or not ("true" or "false")

    Returns:
        Response: JSON response containing historical rates, current rate, and optional forecast
    '''
    from_currency = request.args.get('from')
    to_currency = request.args.get('to')
    perform_prediction = request.args.get('performForecast')

    forex_handler = ForexQueryHandler()

    current_rate = forex_handler.get_current_rate(from_currency, to_currency)
    historical_rates = forex_handler.get_historical_rates(from_currency, to_currency)

    predicted_rates = {}
    if perform_prediction == 'true':
        predicted_rates = forex_handler.get_fx_forecast(from_currency, to_currency, historical_rates)

    res = {
        'historical_rates': historical_rates,
        'current_rate': current_rate,
        'predicted_rates': predicted_rates
    }
    return jsonify(res), 200


if __name__ == '__main__':
    app.run()
