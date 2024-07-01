
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from constants import CURRENCIES
from forex_data_manager import ForexDataManager
from utils import get_most_recent_business_day


class ForexScraper:
    '''
    Scrapes www.xe.com/currencyconverter for exchange rates
    '''
    def __init__(self):
        self.data_manager = ForexDataManager()
    
    def get_soup(self, link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            return None
    
    def scrape(self, to_cur, from_cur):
        link = f'https://www.xe.com/currencyconverter/convert/?Amount=1&From={from_cur}&To={to_cur}'
        soup = self.get_soup(link)

        fin_streamer = soup.find('p', class_='sc-295edd9f-1 jqMUXt')
        text_content = fin_streamer.text.split(' ')
        text_content = text_content[0]
        
        return float(text_content)

    def scrape_all_symbols(self):
        yesterday = datetime.now().date() - timedelta(days=1)
        yesterday = get_most_recent_business_day(yesterday)

        for i in range(1, len(CURRENCIES)):
            for j in range(i):
                rate = self.scrape(CURRENCIES[i], CURRENCIES[j])
                currency_pair = f'{CURRENCIES[j]}/{CURRENCIES[i]}'
                try:
                    self.data_manager.add_one_entry(currency_pair, yesterday, rate)
                except:
                    print(f'Failed to update rate for {CURRENCIES[j]}/{CURRENCIES[i]}')
