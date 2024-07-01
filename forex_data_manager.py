import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


DB_NAME = 'rates'
DATA_KEY = 'historical_data'

load_dotenv()

class ForexDataManager:
    '''
    Reads/writes exchange rate data to MongoDB
    '''
    def __init__(self):
        uri = os.getenv('MONGO_URI')
        self.client = MongoClient(uri, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)           
        try:
            self.client.admin.command('ping')
        except Exception as e:
            print(e)
    
    def add_fx_data(self, currency_pair, company_data):
        db = self.client[DB_NAME]
        historical_data = db[DATA_KEY]

        query = {'currency_pair': currency_pair}

        if historical_data.count_documents(query) == 0:
            res = historical_data.insert_one(company_data)
        else:
            res = historical_data.update_one(query, {'$set': company_data})
        return res
    
    def query_data(self, query):
        db = self.client[DB_NAME]
        companies_data = db[DATA_KEY]

        return companies_data.find(query)
    
    def query_historical_rates(self, currency_pair):
        db = self.client[DB_NAME]
        companies_data = db[DATA_KEY]

        query = {'currency_pair': currency_pair}

        res = companies_data.find(query)

        rates_90_days = res
        daily_avgs = {}

        for i, document in enumerate(rates_90_days):
            if i > 0:
                raise Exception(f'ERROR: duplicate key {currency_pair} in database')
            all_rates = document['rates']

            sorted_keys = sorted(all_rates.keys(), reverse=True)
            for i in range(90):
                daily_avgs[sorted_keys[i]] = all_rates[sorted_keys[i]]
        
        return daily_avgs
    
    def get_all_data(self):
        db = self.client[DB_NAME]
        companies_data = db[DATA_KEY]
        return companies_data.find()

    def add_one_entry(self, currency_pair, date, value):
        db = self.client[DB_NAME]
        historical_data = db[DATA_KEY]

        query = {'currency_pair': currency_pair}
        res = historical_data.update_one(query, {'$set': {f'rates.{date}': value}})
        return res
