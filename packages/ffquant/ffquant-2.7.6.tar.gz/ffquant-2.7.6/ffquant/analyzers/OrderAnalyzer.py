import backtrader as bt
import pytz
import ffquant.utils.observer_data as observer_data

__ALL__ = ['OrderAnalyzer']

class OrderAnalyzer(bt.Analyzer):
    def __init__(self):
        self.order_infos = observer_data.order_info
    
    def start(self):
        super(OrderAnalyzer, self).start()
        self.order_infos.clear()

    # 当订单的状态变化时 该方法会被调用
    def notify_order(self, order):
        if order.status == order.Completed or (order.exectype == order.Limit and (order.status == order.Submitted or order.status == order.Cancelled)):
            dt = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            # 这里的position_after有个问题 当有多个订单时 position_after代表的其实是所有订单成交后的仓位信息 而不是单个订单成交后的仓位信息
            order_info = {
                'datetime': dt,
                'data': order,
                'position_after': self.strategy.position.size
            }
            self.order_infos.append(order_info)
    
    def get_analysis(self):
        return self.order_infos