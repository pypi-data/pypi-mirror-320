import pytest

mongo_uri = "mongodb+srv://admin:Neurowatt456&@axonnews-mongodb.nlui1.mongodb.net/?retryWrites=true&w=majority&appName=axonnews-mongodb"
ticker = "2330"

def test_QoQ():
    from neurostats_API import FinanceReportFetcher

    fetcher = FinanceReportFetcher(mongo_uri)

    data = fetcher.get(
        ticker,
        fetch_mode = fetcher.FetchMode.QOQ_NOCAL,
        start_date="2024-01-01",
        end_date="2024-12-31",
        indexes = ['bp41', 'bp51']
    )

    print(data)

def test_YoY():
    from neurostats_API import FinanceReportFetcher
    fetcher = FinanceReportFetcher(mongo_uri)

    data = fetcher.get(ticker, fetcher.FetchMode.YOY_NOCAL, indexes = ['bp41', 'bp51', 'arv'])
    print (data)