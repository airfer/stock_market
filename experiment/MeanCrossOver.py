from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # 用于datetime对象操作
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称
import backtrader as bt # 引入backtrader框架

# 创建策略
class SmaCross(bt.Strategy):
    # 可配置策略参数
    params = dict(
        pfast=5,  # 短期均线周期
        pslow=10   # 长期均线周期
    )
    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # 短期均线
        sma2 = bt.ind.SMA(period=self.p.pslow)  # 长期均线
        macd=bt.ind.MACD() # 周 Macd
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # 交叉信号
        self.macd = macd.macd
        self.signal = macd.signal
        self.histo = bt.ind.MACDHisto()

    def next(self):
        if not self.position:  # 不在场内，则可以买入
            if self.crossover > 0:  # 如果金叉
                self.buy()  # 买入
        elif self.crossover < 0:  # 在场内，且死叉
            self.close()  # 卖出

if __name__ == '__main__':
    cerebro = bt.Cerebro()  # 创建cerebro
    # 先找到脚本的位置，然后根据脚本与数据的相对路径关系找到数据位置
    # 这样脚本从任意地方被调用，都可以正确地访问到数据
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    #windows
    #datapath = os.path.join(modpath, '..\stock\sh.600000\history_A_stock_k_data.csv')
    #linux or macos
    datapath = os.path.join(modpath, '../stock_weekly/sh.600276/history_A_stock_k_data.csv')

    frequency = "w"
    volume_default_field = 7

    if frequency == "w":
        volume_default_filed=6
    # 创建价格数据
    data = bt.feeds.GenericCSVData(
            dataname = datapath,
            fromdate = datetime.datetime(2018, 1, 1),
            todate = datetime.datetime(2020, 2, 29),
            nullvalue = 0.0,
            dtformat = ('%Y-%m-%d'),
            datetime = 0,
            open = 2,
            high = 3,
            low = 4,
            close = 5,
            volume = volume_default_field,
            openinterest = -1
            )
    # 在Cerebro中添加价格数据
    cerebro.adddata(data)
    # 设置启动资金
    cerebro.broker.setcash(100000.0)
    # 设置交易单位大小
    cerebro.addsizer(bt.sizers.FixedSize, stake = 5000)
    # 设置佣金为千分之一
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(SmaCross)  # 添加策略
    cerebro.run()  # 遍历所有数据
    cerebro.plot()  # 绘图
