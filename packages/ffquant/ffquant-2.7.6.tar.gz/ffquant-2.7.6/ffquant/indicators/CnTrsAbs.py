from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['CnTrsAbs']

class CnTrsAbs(BaseIndicator):
    (CN_ACT_SELL,
     CN_TRS_DN,
     NA,
     CN_TRS_UP,
     CN_ACT_BUY) = (-2, -1, 0, 1, 2)

    lines = ('cn_trs_abs',)

    def __init__(self):
        super(CnTrsAbs, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime']/ 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        if item.get(internal_key, None) is not None and item[internal_key] == 'CN_ACT_SELL':
            self.cache[result_time_str]['value'] = self.CN_ACT_SELL
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'CN_TRS_DN':
            self.cache[result_time_str]['value'] = self.CN_TRS_DN
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'CN_TRS_UP':
            self.cache[result_time_str]['value'] = self.CN_TRS_UP
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'CN_ACT_BUY':
            self.cache[result_time_str]['value'] = self.CN_ACT_BUY
            self.cache[result_time_str]['create_time'] = item['createTime']
        elif item.get(internal_key, None) is not None and item[internal_key] == 'NA':
            self.cache[result_time_str]['value'] = self.NA
            self.cache[result_time_str]['create_time'] = item['createTime']

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.cn_trs_abs[0] = self.cache[current_bar_time_str]['value']

        return self.cache[current_bar_time_str]['create_time']

    def get_internal_key(self):
        return 'TYPE_CN_TRS_ABS' if self.p.version is None else f'TYPE_CN_TRS_ABS_{str(self.p.version).upper()}'