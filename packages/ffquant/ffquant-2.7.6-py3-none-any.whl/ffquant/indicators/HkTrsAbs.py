from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['HkTrsAbs']

class HkTrsAbs(BaseIndicator):
    (OVER_MKT_HK_SELL_CN_BUY,
     HK_ACT_SELL,
     HK_TRS_DN,
     NA,
     HK_TRS_UP,
     HK_ACT_BUY,
     OVER_MKT_HK_BUY_CN_SELL) = (-3, -2, -1, 0, 1, 2, 3)

    lines = ('hk_trs_abs',)

    def __init__(self):
        super(HkTrsAbs, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime']/ 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        if item.get(internal_key, None) is not None and item[internal_key] == 'OVER_MKT_HK_SELL_CN_BUY':
            self.cache[result_time_str]['value'] = self.OVER_MKT_HK_SELL_CN_BUY
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'HK_ACT_SELL':
            self.cache[result_time_str]['value'] = self.HK_ACT_SELL
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'HK_TRS_DN':
            self.cache[result_time_str]['value'] = self.HK_TRS_DN
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'HK_TRS_UP':
            self.cache[result_time_str]['value'] = self.HK_TRS_UP
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'HK_ACT_BUY':
            self.cache[result_time_str]['value'] = self.HK_ACT_BUY
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'OVER_MKT_HK_BUY_CN_SELL':
            self.cache[result_time_str]['value'] = self.OVER_MKT_HK_BUY_CN_SELL
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'NA':
            self.cache[result_time_str]['value'] = self.NA
            self.cache[result_time_str]['create_time'] = item['createTime']

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.hk_trs_abs[0] = self.cache[current_bar_time_str]['value']

        return self.cache[current_bar_time_str]['create_time']

    def get_internal_key(self):
        return 'TYPE_HK_TRS_ABS' if self.p.version is None else f'TYPE_HK_TRS_ABS_{str(self.p.version).upper()}'