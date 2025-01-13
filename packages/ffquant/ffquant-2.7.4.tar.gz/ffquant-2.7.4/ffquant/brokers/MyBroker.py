import backtrader as bt
from datetime import datetime
import os
import requests
import json
from backtrader.utils.py3 import queue
from backtrader.utils import AutoOrderedDict
import collections
from backtrader.position import Position
import getpass
from ffquant.utils.Logger import stdout_log
from urllib.parse import urlencode
import pytz

__ALL__ = ['MyBroker']

class MyBroker(bt.BrokerBase):
    # 以下是交易账号的对应关系 TV代表TradingView
    (TV_SIM1, TV_SIM2, TV_SIM3, TV_SIM4, TV_SIM5, FUTU_SIM1, FUTU_REAL) = ("14078173", "14267474", "14267483", "15539511", "15539514", "9598674", "281756473194939823")

    def __init__(self, id=None, name="tv", debug=False, *args, **kwargs):
        super(MyBroker, self).__init__(*args, **kwargs)
        self.base_url = os.environ.get('MY_BROKER_BASE_URL', 'http://192.168.25.247:8220')
        self.id = id  # 交易账号的ID 参考上面的对应关系
        self.name = name # 券商的名字 tv或者futu
        self.cash = None # 账户的现金余额
        self.value = None # 账户的总市值

        self.orders = {} # 订单信息缓存
        self.pending_orders = list() # 未完成的订单
        self.notifs = queue.Queue() # 等待发送到策略的通知
        self.debug = debug
        self.positions = collections.defaultdict(Position) # symbol维度记录仓位信息
        self.MIN_UPDATE_INTERVAL_SECONDS = 10 # 更新仓位和账户信息的间隔 因为券商有请求频率限制 所以不能太频繁
        self.last_cash_update_ts = 0    # 最后一次更新账户信息的时间
        self.last_value_update_ts = 0   # 最后一次更新账户信息的时间
        self.last_order_update_ts = 0   # 最后一次更新订单信息的时间
        self.last_position_update_ts = 0    # 最后一次更新仓位信息的时间

    # 获取账户信息 非实时
    def getcash(self):
        if self.cash is None:
            self._update_cashvalue()
        return self.cash

    # 获取账户总市值 非实时
    def getvalue(self, datas=None):
        if self.value is None:
            self._update_cashvalue()
        return self.value

    # 获取仓位 非实时
    def getposition(self, data=None, symbol=None):
        position = bt.Position()

        target_symbol = data.p.symbol if data is not None else symbol
        if not self.positions.__contains__(target_symbol):
            self._update_positions()

        if self.positions.__contains__(target_symbol):
            position = self.positions[target_symbol]

        if self.debug:
            stdout_log(f"{self.__class__.__name__}, getposition, position size: {position.size}, price: {position.price}")

        return position

    # 取消订单 需要传入backtrader的Order对象
    def cancel(self, order):
        order_id = order.ref
        url = self.base_url + f"/cancel/order/{self.name}/{self.id}"
        data = {
            "tradeId": order_id,
        }
        payload = urlencode({"content": json.dumps(data)})
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, cancel, payload: {payload}")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, headers=headers, data=payload).json()
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, cancel, response: {response}")

        ret = True
        code = response['code']
        if code != '200':
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, cancel failed, url: {url}, payload: {payload}, response: {response}")
            ret = False
        return ret

    # 获取未完成的订单
    def get_pending_orders(self):
        return self.pending_orders

    # 获取未完成的订单 这个方法跟get_pending_orders的功能一样 只是为了兼容backtrader的接口
    def get_orders_open(self):
        return self.get_pending_orders()

    # 提交订单 所有的buy和sell都通过这个方法实现
    def submit(self, order, **kwargs):
        url = self.base_url + f"/place/order/{self.name}/{self.id}"

        # is_close_pos用来标识是否是平仓 如果不传则认为是开仓
        side = None
        if order.ordtype == bt.Order.Buy:
            if kwargs.get('is_close_pos', False):
                side = 'close'
            else:
                side = 'long'
        elif order.ordtype == bt.Order.Sell:
            if kwargs.get('is_close_pos', False):
                side = 'cover'
            else:
                side = 'short'

        order.size = abs(order.size)
        # 这里的username是为了建立linux的用户名和券商账户的对应关系 追踪是谁在提交订单 以及订单的权限控制
        username = getpass.getuser()
        username = username[8:] if username.startswith('jupyter-') else username

        msg = ""
        if kwargs.get('is_tp', False):  # 是否是止盈 是为了在tradingview中打印bubble而设计的
            msg = "tp"
        elif kwargs.get('is_sl', False):    # 是否是止损 是为了在tradingview中打印bubble而设计的
            msg = "sl"

        # message一般包含了触发订单的原因
        if kwargs.get("message", None) is not None:
            msg = ((msg + ":") if msg != "" else "") + kwargs.get("message")

        data = {
            "symbol": order.data.p.symbol,
            "side": side,
            "qty": order.size,
            "price": order.price,
            "type": "market" if order.exectype == bt.Order.Market else "limit",
            "username": username,
            "message": msg
        }
        payload = urlencode({"content": json.dumps(data)})
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, submit, payload: {payload}")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, headers=headers, data=payload).json()
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, submit, response: {response}")

        order_id = None
        if response.get('code') == "200":
            order_id = response['results']
            order.status = bt.Order.Submitted
            order.ref = order_id
            order.addinfo(**kwargs)

            self.orders[order_id] = order

            kline_local_time_str = order.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
            # 这里的打印是为了在日志中体现出成功订单的信息 用于监控目的
            stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_local_time_str}, submit success, url: {url}, data: {data}, response: {response}")
        else:
            # 这里的打印是为了在日志中体现出失败订单的信息 用于监控目的
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, submit failed, url: {url}, payload: {payload}, response: {response}")

        return order

    def buy(self, owner, data, size, price=None, plimit=None, exectype=None, valid=None, tradeid=0, oco=None, trailamount=None, trailpercent=None, **kwargs):
        order = bt.order.BuyOrder(owner=owner, data=data, size=size, price=price, pricelimit=plimit, exectype=exectype, valid=valid, tradeid=tradeid, oco=oco, trailamount=trailamount, trailpercent=trailpercent)
        return self.submit(order, **kwargs)

    def sell(self, owner, data, size, price=None, plimit=None, exectype=None, valid=None, tradeid=0, oco=None, trailamount=None, trailpercent=None, **kwargs):
        order = bt.order.SellOrder(owner=owner, data=data, size=size, price=price, pricelimit=plimit, exectype=exectype, valid=valid, tradeid=tradeid, oco=oco, trailamount=trailamount, trailpercent=trailpercent)
        return self.submit(order, **kwargs)
    
    # 这个方法是被backtrader框架调用的 策略不要调用这个方法
    def get_notification(self):
        notif = None
        try:
            notif = self.notifs.get(False)
        except queue.Empty:
            pass

        return notif

    # 对于实时情况而言 next方法会被频繁调用 每一次调用都会触发更新订单信息 所以 需要控制频率
    def next(self):
        if datetime.now().timestamp() - self.last_order_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
            self.last_order_update_ts = datetime.now().timestamp()

            # Update order status
            trade_ids = []
            for order_id, order in self.orders.items():
                if order.status != bt.Order.Completed and order.status != bt.Order.Cancelled:
                    trade_ids.append(order_id)
            if len(trade_ids) > 0:
                url = self.base_url + f"/orders/query/{self.name}/{self.id}"
                data = {
                    "tradeIdList": trade_ids
                }
                payload = urlencode({"content": json.dumps(data)})

                if self.debug:
                    stdout_log(f"{self.__class__.__name__}, next, order query payload: {payload}")

                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

                response = requests.post(url, headers=headers, data=payload).json()
                if self.debug:
                    stdout_log(f"{self.__class__.__name__}, next, order query response: {response}")
                if response.get('code') == "200":
                    for item in response['results']:
                        item_status = None
                        # 这里是alisa接口的订单状态和backtrader的订单状态的映射
                        if item['orderStatus'] == "pending" or item['orderStatus'] == "working":
                            item_status = bt.Order.Submitted
                        elif item['orderStatus'] == "cancelled":
                            item_status = bt.Order.Cancelled
                        elif item['orderStatus'] == "filled":
                            item_status = bt.Order.Completed
                        elif item['orderStatus'] == "rejected":
                            item_status = bt.Order.Rejected

                        order = self.orders.get(item['tradeId'], None)
                        if order is not None and order.status != item_status:
                            if self.debug:
                                stdout_log(f"{self.__class__.__name__}, next, order status changed, orderId: {order.ref}, old status: {order.getstatusname()}, new status: {bt.Order.Status[item_status]}")

                            # 对于已完成的订单 需要记录执行的size和价格
                            if item_status == bt.Order.Completed:
                                order.executed.size = item['qty']
                                order.executed.price = item['executePrice']

                            order.status = item_status
                            self.orders[item['tradeId']] = order
                            self.notifs.put(order.clone())
                else:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, order query failed, url: {url}, payload: {payload}, response: {response}")

            # Update pending orders 这里是待成交的订单的更新
            url = self.base_url + f"/orders/query/{self.name}/{self.id}"
            data = {
                "orderStatusList": ["pending", "working"]
            }
            payload = urlencode({"content": json.dumps(data)})
            if self.debug:
                stdout_log(f"{self.__class__.__name__}, next, order query payload: {payload}")
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(url, headers=headers, data=payload).json()
            if self.debug:
                stdout_log(f"{self.__class__.__name__}, next, order query response: {response}")
            if response.get('code') == "200":
                self.pending_orders.clear()
                for item in response['results']:
                    order_id = item['tradeId']
                    exec_type = bt.Order.Market
                    if item['tradeType'] == "limit":
                        exec_type = bt.Order.Limit

                    p_order = None
                    if item['tradeSide'] == 'buy':
                        p_order = bt.order.BuyOrder(owner=None,
                                                    data=None,
                                                    size=item['qty'],
                                                    price=item['allocationPrice'],
                                                    pricelimit=item['allocationPrice'],
                                                    exectype=exec_type,
                                                    valid=None,
                                                    tradeid=0,
                                                    oco=None,
                                                    trailamount=None,
                                                    trailpercent=None,
                                                    simulated=True)
                    else:
                        p_order = bt.order.SellOrder(owner=None,
                                                    data=None,
                                                    size=item['qty'],
                                                    price=item['allocationPrice'],
                                                    pricelimit=item['allocationPrice'],
                                                    exectype=exec_type,
                                                    valid=None,
                                                    tradeid=0,
                                                    oco=None,
                                                    trailamount=None,
                                                    trailpercent=None,
                                                    simulated=True)
                    p_order.p.simulated = False
                    p_order.ref = order_id
                    p_order.status = bt.Order.Submitted
                    self.pending_orders.append(p_order)
            else:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, order query failed, url: {url}, payload: {payload}, response: {response}")

        # Update positions
        self._update_positions()

        # Update cash & value
        self._update_cashvalue()

    def get_order(self, order_id):
        return self.orders.get(order_id, None)

    def _update_cashvalue(self):
        # cash
        if datetime.now().timestamp() - self.last_cash_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
            self.last_cash_update_ts = datetime.now().timestamp()
            url = self.base_url + f"/balance/{self.name}/{self.id}"
            response = requests.get(url).json()
            if self.debug:
                stdout_log(f"{self.__class__.__name__}, _update_cashvalue, balance response: {response}")
            if response.get('code') == "200" and response['results'] is not None:
                self.cash = response['results']['balance']
            else:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, balance query failed, url: {url}, response: {response}")

        # value
        if self.cash is not None:
            if datetime.now().timestamp() - self.last_value_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
                self.last_value_update_ts = datetime.now().timestamp()

                value = self.cash
                url = self.base_url + f"/positions/{self.name}/{self.id}"
                response = requests.get(url).json()
                if self.debug:
                    stdout_log(f"{self.__class__.__name__}, _update_cashvalue, positions response: {response}")
                if response.get('code') == "200":
                    for pos in response['results']:
                        if pos['qty'] == 0:
                            continue
                        if pos['tradeSide'] == 'buy':
                            value = value + pos['qty'] * (pos['latestPrice'] - pos['avgPrice'])
                        elif pos['tradeSide'] == 'sell':
                            value = value + pos['qty'] * (pos['avgPrice'] - pos['latestPrice'])
                else:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, positions query failed, url: {url}, response: {response}")
                self.value = value

    def _update_positions(self):
        if datetime.now().timestamp() - self.last_position_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
            self.last_position_update_ts = datetime.now().timestamp()

            if self.positions.__len__() > 0:
                self.positions.clear()

            url = self.base_url + f"/positions/{self.name}/{self.id}"
            response = requests.get(url).json()

            if self.debug:
                stdout_log(f"{self.__class__.__name__}, _update_positions, positions response: {response}")

            if response.get('code') == "200":
                for pos in response['results']:
                    if pos['qty'] != 0:
                        self.positions[pos['symbol']] = bt.Position(size=pos['qty'] if pos['tradeSide'] == 'buy' else -pos['qty'], price=pos['avgPrice'])
            else:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, positions query failed, url: {url}, response: {response}")