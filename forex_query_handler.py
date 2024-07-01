from datetime import datetime, timedelta

from forex_data_manager import ForexDataManager
from forex_scraper import ForexScraper
from forecasting_model import ForexForecast
from utils import get_most_recent_business_day


class ForexQueryHandler:
    '''
    Connects the API with: 
        - MondoDB 
        - Web scraper 
        - Forecasting model
    '''
    def __init__(self):
        self.data_manager = ForexDataManager()
        self.scraper = ForexScraper()

    def get_current_rate(self, from_currency, to_currency):
        return self.scraper.scrape(to_currency, from_currency)

    def get_historical_rates(self, from_currency, to_currency):
        inverse = False
        if to_currency < from_currency:
            inverse = True
            to_currency, from_currency = from_currency, to_currency

        curr_pair = f'{from_currency}/{to_currency}'

        daily_avgs = self.data_manager.query_historical_rates(curr_pair)

        yesterday = datetime.now().date() - timedelta(days=1)

        recent_bus_day = get_most_recent_business_day(yesterday)
        recent_bus_day = recent_bus_day.strftime('%Y-%m-%d')

        if recent_bus_day not in daily_avgs.keys():
            self.scraper.scrape_all_symbols()
            daily_avgs = self.data_manager.query_historical_rates(curr_pair)

        if inverse:
            for date in daily_avgs:
                daily_avgs[date] = 1/daily_avgs[date]
        
        return daily_avgs
    
    def get_rate_for_date(self, from_currency, to_currency, date=None):
        inverse = False
        if to_currency < from_currency:
            inverse = True
            to_currency, from_currency = from_currency, to_currency

        if date == None:
            date = datetime.now().strftime('%Y-%m-%d')

        curr_pair = f'{from_currency}/{to_currency}'
        historical_rates = self.data_manager.query_data({'currency_pair': curr_pair})

        avg_rate = None
        
        for i, document in enumerate(historical_rates):
            if i > 0:
                raise Exception(f'ERROR: duplicate key {curr_pair} in database')
            avg_rate = document['rates'][date]

        if avg_rate == None:
            Exception(f'ERROR: No current rate found for {curr_pair}')
        
        if inverse:
            return 1/avg_rate
        return avg_rate

    def get_fx_forecast(self, from_currency, to_currency, historical_rates):
        forecaster = ForexForecast()
        return forecaster.get_fx_forecast(historical_rates)
