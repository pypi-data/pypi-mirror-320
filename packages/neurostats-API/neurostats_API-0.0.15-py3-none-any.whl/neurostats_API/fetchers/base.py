import abc
from pymongo import MongoClient
import pandas as pd
import json
import pytz
from datetime import datetime, timedelta, date
from ..utils import StatsDateTime, StatsProcessor, YoY_Calculator
import yaml

class StatsFetcher:
    def __init__(self, ticker, db_client):
        self.ticker = ticker
        self.db = db_client["company"]  # Replace with your database name
        self.collection = self.db["twse_stats"]

        self.timezone = pytz.timezone("Asia/Taipei")

        self.target_metric_dict = {
            'value': ['value'],
            'value_and_percentage': ['value', 'percentage'],
            'percentage': ['percentage'],
            'grand_total': ['grand_total'],
            'grand_total_values': ['grand_total', 'grand_total_percentage'],
            'grand_total_percentage': ['grand_total_percentage'],
            'growth': [f'YoY_{i}' for i in [1, 3, 5, 10]],
            'grand_total_growth': [f"YoY_{i}" for i in [1, 3, 5, 10]]
        }


    def prepare_query(self):
        return [
            {
                "$match": {
                    "ticker": self.ticker,
                }
            },
        ]

    def collect_data(self, start_date, end_date):
        pipeline = self.prepare_query()

        fetched_data = list(self.collection.aggregate(pipeline))

        return fetched_data[0]

    def str_to_datetime(self, date_str):
        year, month, day = [int(num) for num in date_str.split("-")]

        date = datetime.strptime(date_str, "%Y-%m-%d")
        date = self.timezone.localize(date)

        season = (month - 1) // 3 + 1

        return StatsDateTime(date, year, month, day, season)

class BaseTEJFetcher(abc.ABC):
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    @abc.abstractmethod
    def get(self):
        pass
    
    def get_latest_data_time(self, ticker):
        latest_data = self.collection.find_one(
            {"ticker": ticker},
            {"last_update": 1, "_id" : 0}
        )

        try:
            latest_date = latest_data['last_update']["latest_data_date"]
        except Exception as e:
            latest_date = None
        
        return latest_date

    def cal_YoY(self, data_dict: dict, start_year: int, end_year: int):
        year_shifts = [1,3,5,10]
        return_dict = {}
        for year in range(start_year, end_year+1):
            year_data = data_dict[str(year)]
            year_keys = list(year_data.keys())
            for key in year_keys:
                if (key in 'season'):
                    continue

                if (isinstance(year_data[key], (int, float))):
                    temp_dict = {"value": year_data[key]}

                    for shift in year_shifts:
                        this_value = year_data[key]
                        try:
                            past_year = str(year - shift)
                            last_value = data_dict[past_year][key]['value']
                            temp_dict[f"YoY_{shift}"] = YoY_Calculator.cal_growth(
                                this_value, last_value, delta = shift
                            )
                        except Exception as e:
                            temp_dict[f"YoY_{shift}"] = None
                        
                    year_data[key] = temp_dict

                else:
                    year_data.pop(key)
            
            return_dict[year] = year_data
        
        
        return return_dict
    
    def cal_QoQ(self, data_dict):
        return_dict = {}
        for i, time_index in enumerate(data_dict.keys()):
            year, season = time_index.split("Q")
            year = int(year)
            season = int(season)
            if (season == 1):
                last_year = year - 1
                last_season = 4
            else:
                last_year = year
                last_season = season - 1
            
            this_data = data_dict[time_index]
            this_keys = list(this_data.keys())
            for key in this_keys:
                if (key in 'season'):
                    continue

                this_value = this_data[key]

                if (isinstance(this_value, (int, float))):
                    temp_dict = {"value": this_value}

                    try:
                        last_value = data_dict[f"{last_year}Q{last_season}"][key]['value']

                        temp_dict['growth'] = YoY_Calculator.cal_growth(
                            this_value, last_value, delta=1
                        )
                    except Exception as e:
                        temp_dict['growth'] = None
                        
                    this_data[key] = temp_dict

                else:
                    this_data.pop(key)
            return_dict[time_index] = this_data
        return return_dict
            