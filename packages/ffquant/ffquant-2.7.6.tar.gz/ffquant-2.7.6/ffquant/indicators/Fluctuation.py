from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['Fluctuation']

class Fluctuation(BaseIndicator):
    (FLUCT_BEARISH_L10,
     FLUCT_BEARISH_L9,
     FLUCT_BEARISH_L8,
     FLUCT_BEARISH_L7,
     FLUCT_BEARISH_L6,
     FLUCT_BEARISH_L5,
     FLUCT_BEARISH_L4,
     FLUCT_BEARISH_L3,
     FLUCT_BEARISH_L2,
     FLUCT_BEARISH_L1,
     NA,
     FLUCT_BULLISH_L1,
     FLUCT_BULLISH_L2,
     FLUCT_BULLISH_L3,
     FLUCT_BULLISH_L4,
     FLUCT_BULLISH_L5,
     FLUCT_BULLISH_L6,
     FLUCT_BULLISH_L7,
     FLUCT_BULLISH_L8,
     FLUCT_BULLISH_L9,
     FLUCT_BULLISH_L10) = (-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    lines = ('fluct',)

    def __init__(self):
        super(Fluctuation, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        if item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L10':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L10
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L9':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L9
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L8':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L8
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L7':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L7
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L6':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L6
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L5':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L5
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L4':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L4
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L3':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L3
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L2':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L2
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BULLISH_L1':
            self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L1
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L1':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L1
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L2':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L2
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L3':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L3
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L4':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L4
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L5':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L5
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L6':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L6
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L7':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L7
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L8':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L8
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L9':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L9
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'FLUCT_BEARISH_L10':
            self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L10
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'NA':
            self.cache[result_time_str]['value'] = self.NA
            self.cache[result_time_str]['create_time'] = item['createTime']

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.fluct[0] = self.cache[current_bar_time_str]['value']

        return self.cache[current_bar_time_str]['create_time']

    def get_internal_key(self):
        return 'TYPE_FLUCTUATION' if self.p.version is None else f'TYPE_FLUCTUATION_{str(self.p.version).upper()}'