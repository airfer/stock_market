from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)


        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        macd=bt.indicators.MACD()
        self.macd=macd.macd
        self.signal = macd.signal
        histo=bt.ind.MACDHisto()
        self.macd_histo=histo.histo

        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        abs_macd = self.macd[0]
        sig=self.signal[0]
        abs_macd_histo=self.macd_histo[0]
        # self.log("macd-value: %s, date：%s" %(abs_macd,self.datas[0].datetime.date(0)))
        # self.log("sig: %s, date：%s" %(sig,self.datas[0].datetime.date(0)))
        # self.log("macd-histo-value: %s, date：%s" %(abs_macd_histo * 2,self.datas[0].datetime.date(0)))

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            # if self.dataclose[0] > self.sma[0]:
            #
            #     # BUY, BUY, BUY!!! (with all possible default parameters)
            #     self.log('BUY CREATE, %.2f' % self.dataclose[0])
            #
            #     # Keep track of the created order to avoid a 2nd order
            #     self.order = self.buy()
            if abs(abs_macd_histo) <= 0.1 :
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order=self.buy()

        else:

            # if self.dataclose[0] < self.sma[0]:
            #     # SELL, SELL, SELL!!! (with all possible default parameters)
            #     self.log('SELL CREATE, %.2f' % self.dataclose[0])
            #
            #     # Keep track of the created order to avoid a 2nd order
            #     self.order = self.sell()
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.order=self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    stake_code = "sh.600276";
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # path in linux
    relative_path_in_linux = "../stock_weekly/%s/history_A_stock_k_data.csv" % (stake_code);
    # path in windows
    relative_path_in_windows = relative_path_in_linux.replace("/", "\\");
    datapath=os.path.join(modpath, relative_path_in_linux);

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2018, 1, 1),
        todate=datetime.datetime(2020, 2, 29),
        nullvalue=0.0,
        dtformat=('%Y-%m-%d'),
        datetime=0,
        open=2,
        high=3,
        low=4,
        close=5,
        volume=6,
        openinterest=-1
    )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    start=cerebro.broker.getvalue();
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    end=cerebro.broker.getvalue();
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    print('利润率：%.2f' %((end -start)/start))
    # Plot the result
    cerebro.plot()