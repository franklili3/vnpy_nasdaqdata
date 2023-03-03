from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

from numpy import ndarray
from pandas import DataFrame, date_range, merge, read_json
import requests

from vnpy.trader.setting import SETTINGS
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.utility import round_to, ZoneInfo
from vnpy.trader.datafeed import BaseDatafeed


INTERVAL_VT2RQ: Dict[Interval, str] = {
    Interval.MINUTE: "1m",
    Interval.HOUR: "60m",
    Interval.DAILY: "1d",
}

INTERVAL_ADJUSTMENT_MAP: Dict[Interval, timedelta] = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta()         # no need to adjust for daily bar
}

CHINA_TZ = ZoneInfo("Asia/Shanghai")


class NasdaqdataDatafeed(BaseDatafeed):
    """NasdaqData数据服务接口"""

    def __init__(self):
        """"""
        self.username: str = SETTINGS["datafeed.username"]
        self.password: str = SETTINGS["datafeed.password"]

        self.inited: bool = False
        self.symbols: ndarray = None

    def init(self, output: Callable = print) -> bool:
        """初始化"""
        if self.inited:
            return True

        if not self.username:
            output("NasdaqData数据服务初始化失败：用户名为空！")
            return False

        if not self.password:
            output("NasdaqData数据服务初始化失败：密码为空！")
            return False

        self.inited = True
        return True

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """查询K线数据"""
        if not self.inited:
            n: bool = self.init(output)
            if not n:
                return []

        symbol: str = req.symbol
        exchange: Exchange = req.exchange
        interval: Interval = req.interval
        start: datetime = req.start
        end: datetime = req.end

        # 为了将Nasdaq时间戳（K线结束时点）转换为VeighNa时间戳（K线开始时点）
        adjustment: timedelta = INTERVAL_ADJUSTMENT_MAP[interval]


        url = 'https://data.nasdaq.com/api/v3/datasets/'
        api_key = self.password
        # make API request
        res = requests.get(url + exchange + '/' + symbol + '.json',
            params={'api_key': api_key})
        json = read_json(res.text)
        # convert to pandas dataframe
        df = DataFrame(json['dataset']['data'], columns = json['dataset']['column_names'])
        newest_available_date = json['dataset']['newest_available_date']
        oldest_available_date = json['dataset']['oldest_available_date']
        data: List[BarData] = []

        if df is not None:
            # 把0改为NaN
            df = df[df!= 0]
            # 修改date为日期格式
            df['date1'] = df['Date'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
            df = df.drop(['Date'], axis=1)
            df = df.rename(columns={'date1': 'Date'})

            new_date = date_range(start=oldest_available_date, end=newest_available_date, freq='D')
            df1 = DataFrame(0, index = new_date, columns = {'zero'})
            df1 = df1.reset_index()
            df1 = df1.rename({'index': 'Date'}, axis = 1)
            df1 = df1.drop('zero', axis = 1)
            df2 = merge(df, df1, how = 'right', on = 'Date')
            # 填充NaN为昨天的非空值
            df2.fillna(method='ffill', inplace=True)

            for row in df2.itertuples():
                dt: datetime = row.Date.to_pydatetime() - adjustment
                dt: datetime = dt.replace(tzinfo=CHINA_TZ)

                bar: BarData = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    datetime=dt,
                    open_price=round_to(row.Mid, 0.000001),
                    high_price=round_to(row.High, 0.000001),
                    low_price=round_to(row.Low, 0.000001),
                    close_price=round_to(row.Last, 0.000001),
                    volume=row.Volume,
                    gateway_name="NASDAQDATA"
                )

                data.append(bar)

        return data