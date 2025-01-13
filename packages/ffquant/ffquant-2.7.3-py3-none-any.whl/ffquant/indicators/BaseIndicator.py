import backtrader as bt
import os
import pytz
import requests
from datetime import datetime, timedelta, timezone
import time
from ffquant.utils.Logger import stdout_log

__ALL__ = ['BaseIndicator']

class BaseIndicator(bt.Indicator):

    params = (
        ('url', f"{os.environ.get('FINTECHFF_INDICATOR_BASE_URL', 'http://192.168.25.127:8288')}/signal/list"),
        ('symbol', 'CAPITALCOM:HK50'),
        ('max_retries', 15),        # 请求行情的HTTP接口的重试次数 每次重试间隔为1秒 默认最大重试15次 如果最大重试次数内没有成功则沿用上一根K线的数据
        ('version', None),          # 指标版本 该参数的优先级高于通过BaseIndicator.VERSION指定的版本号
        ('test', None),             # 指标测试模式 该参数的优先级高于通过BaseIndicator.TEST指定的测试模式
        ('debug', None),            # 指标调试模式 该参数的优先级高于通过BaseIndicator.DEBUG指定的调试模式
    )

    # 对于都一个时间区间 信号HTTP接口返回的数据都是一样的 这里缓存在静态变量中是为了防止重复请求
    http_resp_cache = {}

    VERSION = 'V2024112911'         # 指标版本号 用户通过给BaseIndicator.VERSION赋值来指定指标版本号
    TEST = False                    # 指标测试模式 用户通过给BaseIndicator.TEST赋值来指定指标测试模式
    DEBUG = False                   # 指标调试模式 用户通过给BaseIndicator.DEBUG赋值来指定指标调试模式

    def __init__(self):
        super(BaseIndicator, self).__init__()
        if self.p.test is None:
            self.p.test = self.TEST

        if self.p.debug is None:
            self.p.debug = self.DEBUG

        if self.p.test:
            self.p.url = self.p.url + "/test"

        if self.p.version is None:
            self.p.version = self.VERSION

        self.cache = {}

    # 子类需要实现这个方法 用于处理HTTP接口返回的数据项 把返回的字符串映射为数字
    def handle_api_resp(self, result):
        pass

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        pass

    # 子类需要实现这个方法 返回指标的内部key 比如：TYPE_TREND_W，注意它返回的值不能包含信号版本
    def get_internal_key(self):
        pass

    def next(self):
        cur_bar_local_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cur_bar_local_time_str = cur_bar_local_time.strftime('%Y-%m-%d %H:%M:%S')

        # 实时模式
        is_live = self.data.islive()
        if is_live:
            if len(self.cache) == 0:
                # 在加载数据的最开始进行数据回填
                backfill_size = self.data.p.backfill_size
                if backfill_size > 0:
                    end_time = datetime.now().replace(second=0, microsecond=0)
                    start_time = end_time - timedelta(minutes=backfill_size)

                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

                    params = self.prepare_params(start_time_str, end_time_str)

                    # fill with -inf
                    minutes_delta = int((end_time.timestamp() - start_time.timestamp()) / 60)
                    for i in range(0, minutes_delta):
                        self.cache[(start_time + timedelta(minutes=i + 1)).strftime('%Y-%m-%d %H:%M:%S')] = {'value': float('-inf'), 'create_time': 0}

                    if self.p.debug:
                        stdout_log(f"{self.__class__.__name__}, fetch data params: {params}, url: {self.p.url}")

                    response = requests.get(self.p.url, params=params).json()
                    if self.p.debug:
                        stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

                    if response.get('code') != '200':
                        raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")
                    results = response.get('results', [])
                    results.sort(key=lambda x: x['closeTime'])

                    for result in results:
                        self.handle_api_resp(result)

            # 如果不在缓存中 则请求数据
            if cur_bar_local_time_str not in self.cache:
                start_time = cur_bar_local_time - timedelta(minutes=1)
                start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time = cur_bar_local_time

                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

                params = self.prepare_params(start_time_str, end_time_str)

                # fill with -inf
                minutes_delta = int((end_time.timestamp() - start_time.timestamp()) / 60)
                for i in range(0, minutes_delta):
                    self.cache[(start_time + timedelta(minutes=i + 1)).strftime('%Y-%m-%d %H:%M:%S')] = {'value': float('-inf'), 'create_time': 0}

                key = f"{self.p.symbol}_{start_time_str}_{end_time_str}"
                response = BaseIndicator.http_resp_cache.get(key, None)
                if response is None:
                    retry_count = 0
                    max_retry_count = self.p.max_retries
                    while retry_count < max_retry_count:
                        retry_count += 1
                        if self.p.debug:
                            stdout_log(f"{self.__class__.__name__}, fetch data params: {params}, url: {self.p.url}")

                        response = requests.get(self.p.url, params=params).json()
                        if self.p.debug:
                            stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

                        if response.get('code') != '200':
                            raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")

                        BaseIndicator.http_resp_cache[key] = response
                        if response.get('results') is not None and len(response['results']) > 0:
                            results = response['results']
                            results.sort(key=lambda x: x['closeTime'])
                            for result in results:
                                self.handle_api_resp(result)
                            break
                        time.sleep(1)
                else:
                    if self.p.debug:
                        stdout_log(f"{self.__class__.__name__}, use cached response: {response}")
                    if response.get('results') is not None and len(response['results']) > 0:
                        results = response['results']
                        results.sort(key=lambda x: x['closeTime'])
                        if results[len(results) - 1].get(self.get_internal_key(), None) is None:
                            if self.p.debug:
                                stdout_log(f"{self.__class__.__name__}, cached response's last result has no {self.get_internal_key()}, refresh data params: {params}, url: {self.p.url}")

                            time.sleep(1)
                            response = requests.get(self.p.url, params=params).json()
                            if self.p.debug:
                                stdout_log(f"{self.__class__.__name__}, refresh data response: {response}")

                            if response.get('code') != '200':
                                raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")

                            BaseIndicator.http_resp_cache[key] = response
                            results = response['results']
                            results.sort(key=lambda x: x['closeTime'])

                        for result in results:
                            self.handle_api_resp(result)
            else:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]['value']}")
        else:
            # 非实时模式 一次性把所有的数据都捞回来
            if len(self.cache) == 0:
                start_time_str = self.data.p.start_time
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S').replace(second=0, microsecond=0)
                end_time_str = self.data.p.end_time
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S').replace(second=0, microsecond=0)
                backfill_size = self.data.p.backfill_size

                if backfill_size > 0:
                    start_time = start_time - timedelta(minutes=backfill_size)
                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

                params = self.prepare_params(start_time_str, end_time_str)

                # fill with -inf
                minutes_delta = int((end_time.timestamp() - start_time.timestamp()) / 60)
                for i in range(0, minutes_delta):
                    self.cache[(start_time + timedelta(minutes=(i + 1))).strftime('%Y-%m-%d %H:%M:%S')] = {'value': float('-inf'), 'create_time': 0}

                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, fetch data params: {params}, url: {self.p.url}")

                response = requests.get(self.p.url, params=params).json()
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

                if response.get('code') != '200':
                    raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")

                if response.get('results') is not None and len(response['results']) > 0:
                    results = response['results']
                    results.sort(key=lambda x: x['closeTime'])
                    for result in results:
                        self.handle_api_resp(result)
            elif cur_bar_local_time_str in self.cache:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]['value']}")

        # 不管是实时模式还是非实时模式 都在此判断最终应该返回什么数值
        create_time = self.determine_final_result()

        # Replace -info with previous value. Starting value is zero. heartbeat info print
        for line_name in self.lines.getlinealiases():
            line = getattr(self.lines, line_name)
            if line[0] == float('-inf'):
                if len(self) > 1:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, kline time: {cur_bar_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')}, line[0] inherited from line[-1]: {line[-1]}")
                    line[0] = line[-1]
                else:
                    line[0] = 0
            kline_local_time_str = cur_bar_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
            create_local_time_str = datetime.fromtimestamp(create_time / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

            # 这里的打印最终会输出到标准输出日志中 这样的日志被用于分析行情的延迟等问题
            stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_local_time_str}, create_time: {create_local_time_str}, {line_name}: {line[0]}")

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'startTime' : start_time_str,
            'endTime' : end_time_str,
            'symbol' : self.p.symbol
        }

        return params