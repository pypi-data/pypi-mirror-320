from .base import BaseTEJFetcher
from datetime import datetime
from enum import Enum
import pandas as pd
from pymongo import MongoClient
from ..utils import StatsProcessor, YoY_Calculator
import warnings


class FinanceReportFetcher(BaseTEJFetcher):
    class FetchMode(Enum):
        YOY = 1
        QOQ = 2
        YOY_NOCAL = 3
        QOQ_NOCAL = 4

    def __init__(self, mongo_uri, db_name = "company", collection_name = "TWN/AINVFQ1"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        self.check_index = {
            'coid', 'mdate', 'key3', 'no',
            'sem', 'merg', 'curr', 'annd',
            'fin_ind', 'bp11', 'bp21', 'bp22',
            'bp31', 'bp41', 'bp51', 'bp53',
            'bp61', 'bp62', 'bp63', 'bp64',
            'bp65', 'bf11', 'bf12', 'bf21',
            'bf22', 'bf41', 'bf42', 'bf43',
            'bf44', 'bf45', 'bf99', 'bsca',
            'bsnca', 'bsta','bscl','bsncl',
            'bstl','bsse','bslse','debt',
            'quick','ppe','ar','ip12',
            'ip22','ip31','ip51','iv41',
            'if11','isibt','isni','isnip',
            'eps','ispsd','gm','opi',
            'nri','ri','nopi','ebit',
            'cip31','cscfo','cscfi','cscff',
            'person','shares','wavg','taxrate',
            'r104','r115','r105','r106',
            'r107','r108','r201','r112',
            'r401','r402','r403','r404',
            'r405','r408','r409','r410',
            'r502','r501','r205','r505',
            'r517','r512','r509','r608',
            'r616','r610','r607','r613',
            'r612','r609','r614','r611',
            'r307','r304','r305','r306',
            'r316','r834'
        }

    def get(
        self, 
        ticker, 
        fetch_mode: FetchMode = FetchMode.QOQ,
        start_date: str = None,
        end_date: str = None,
        report_type: str = "Q",
        indexes: list = []
    ):
        """
        基礎的query function
        ticker(str): 股票代碼
        start_date(str):  開頭日期範圍
        end_date(str):  = 結束日期範圍
        report_type(str): 報告型態 {"A", "Q", "TTM"}  
        fetch_mode(class FetchMode): 
           YoY : 起始日期到結束日期範圍內，特定該季的資料
           QoQ : 起始日期到結束日期內，每季的資料(與上一季成長率)
        indexes(List): 指定的index
        """
        # 確認indexes中是否有錯誤的index，有的話回傳warning
        if (indexes and self.check_index):
            indexes = set(indexes)
            difference = indexes-self.check_index
            if (difference):
                warnings.warn(
                    f"{list(difference)} 沒有出現在資料表中，請確認column名稱是否正確",
                    UserWarning
                )


        if (fetch_mode in {
                self.FetchMode.QOQ,
                self.FetchMode.QOQ_NOCAL
            }   
        ):
            if (not start_date):
                warnings.warn("No start_date specified, use default date = \"2005-01-01\"", UserWarning)
                start_date = datetime.strptime("2005-01-01", "%Y-%m-%d")      
            if (not end_date):
                warnings.warn("No end_date specified, use default date = today", UserWarning)
                end_date = datetime.today()

            assert (start_date <= end_date)
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            start_year = start_date.year
            start_season = (start_date.month - 1) // 4 + 1
            end_year = end_date.year
            end_season = (end_date.month - 1) // 4 + 1

            if (fetch_mode == self.FetchMode.QOQ):
                use_cal = True
            else:
                use_cal = False

            data_df = self.get_QoQ_data(
                ticker=ticker,
                start_year=start_year,
                start_season=start_season,
                end_year=end_year,
                end_season=end_season,
                report_type=report_type,
                indexes=indexes,
                use_cal=use_cal
            )

            return data_df

        elif (fetch_mode in {
                self.FetchMode.YOY,
                self.FetchMode.YOY_NOCAL
            }
        ):
            start_year = 2005
            end_date = self.get_latest_data_time(ticker)
            if (not end_date):
                end_date = datetime.today()

            end_year = end_date.year
            season = (end_date.month - 1) // 4 + 1

            if (fetch_mode == self.FetchMode.YOY):
                use_cal = True
            else:
                use_cal = False

            data_df = self.get_YoY_data(
                ticker = ticker,
                start_year = start_year,
                end_year = end_year,
                season = season,
                report_type = report_type,
                indexes = indexes
            )
        
            return data_df

    def get_QoQ_data(
        self,
        ticker,
        start_year,
        start_season,
        end_year,
        end_season,
        report_type = "Q",
        indexes = [],
        use_cal = False
    ):
        """
            取得時間範圍內每季資料
        """
        if (not indexes): # 沒有指定 -> 取全部
            pipeline = [
                { "$match": { "ticker": ticker } },
                { "$unwind": "$data" },
                { "$match": {
                    "$or": [
                        { "data.year": { "$gt": start_year, "$lt": end_year } },
                        { "data.year": start_year, "data.season": { "$gte": start_season } },
                        { "data.year": end_year, "data.season": { "$lte": end_season } }
                    ]
                }},
                { "$project": {
                    "data.year": 1,
                    "data.season": 1,
                    f"data.{report_type}": 1,
                    "_id": 0
                    } 
                }
            ]

        
        else: # 取指定index
            project_stage = {
                "data.year": 1,
                "data.season": 1
            }
            for index in indexes:
                project_stage[f"data.{report_type}.{index}"] = 1

            pipeline = [
                { "$match": { "ticker": ticker } },
                { "$unwind": "$data" },
                { "$match": {
                    "$or": [
                        { "data.year": { "$gt": start_year, "$lt": end_year } },
                        { "data.year": start_year, "data.season": { "$gte": start_season } },
                        { "data.year": end_year, "data.season": { "$lte": end_season } }
                    ]
                }},
                { "$project": project_stage }
            ]


        fetched_data = self.collection.aggregate(pipeline).to_list()
        
        data_dict = StatsProcessor.list_of_dict_to_dict(
            fetched_data,
            keys = ["year", "season"],
            delimeter = "Q",
            data_key=report_type
        )
        if (use_cal):
            data_with_QoQ = self.cal_QoQ(data_dict)
            data_df = pd.DataFrame.from_dict(data_with_QoQ)
        else:
            data_df = pd.DataFrame.from_dict(data_dict)
        return data_df
    
    def get_YoY_data(
        self,
        ticker,
        start_year,
        end_year,
        season,
        report_type = "Q",
        indexes = [],
        use_cal = False
    ):
        """
        取得某季歷年資料
        """
        if (use_cal):
            select_year = set()

            for year in range(start_year, end_year + 1):
                year_shifts = {
                    year,
                    year - 1,
                    year - 3,
                    year - 5,
                    year - 10
                }

                select_year = select_year.union(year_shifts)
            
            select_year = sorted(list(select_year), reverse=True)
        else:
            select_year = [year for year in range(start_year, end_year + 1)]

        if (not indexes): # 沒有指定 -> 取全部
            pipeline = [
                { "$match": { "ticker": ticker } },
                { "$unwind": "$data" },
                { "$match": {
                    "$or":[
                        {
                            "$and": [
                                { "data.year": {"$in": select_year }},
                                { "data.season": {"$eq": season}}
                            ]
                        },
                    ]
                }},
                { "$project": {
                    "data.year": 1,
                    "data.season": 1,
                    f"data.{report_type}": 1, 
                    "_id": 0 
                    } 
                }
            ]

        
        else: # 取指定index
            project_stage = {
                "data.year": 1,
                "data.season": 1
            }
            for index in indexes:
                project_stage[f"data.{report_type}.{index}"] = 1

            pipeline = [
                { "$match": { "ticker": ticker } },
                { "$unwind": "$data" },
                { "$match": {
                    "$and": [
                                { "data.year": {"$in": select_year}},
                                { "data.season": {"$eq": season}}
                            ]
                }},
                { "$project": project_stage }
            ]

        fetched_data = self.collection.aggregate(pipeline).to_list()

        # 處理計算YoY
        data_dict = StatsProcessor.list_of_dict_to_dict(
            fetched_data,
            keys = ['year', 'season'],
            data_key=report_type,
            delimeter='Q'
        )
        if (use_cal):
            data_with_YoY = self.cal_YoY(data_dict, start_year, end_year)
            result_df = pd.DataFrame.from_dict(data_with_YoY)
        else:
            result_df = pd.DataFrame.from_dict(data_dict)

        return result_df
