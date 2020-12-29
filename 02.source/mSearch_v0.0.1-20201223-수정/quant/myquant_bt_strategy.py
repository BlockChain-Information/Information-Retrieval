# -*- coding: utf-8 -*-
"""
Created on Fri May 29 16:47:49 2020

@author: 3337389
"""


import backtrader as bt

# =============================================================================
# 전략 Class 정의
# =============================================================================
# 모멘텀 전략
class Momentum(bt.Strategy):
    params = dict(
        pfast=10, # period for the fast moving average
        pslow=20  # period for the slow moving average
    )
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.smaSlow = bt.ind.SimpleMovingAverage(period = self.p.pslow)
        self.smaFast = bt.ind.SimpleMovingAverage(period = self.p.pslow)
        self.order = None
        
    def log(self,txt,dt=None):
        ''' Loging  function fot this stratege'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s'%(dt.isoformat(),txt))
        
    def notify_order(self,order):
        # 1. If order is submitted/accepted,do nothing
        if order.status in [order.Submitted,order.Accepted]:
            return
        # 2. If order is buy/sell executed,report price executed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price:{0:8.2f},Size:{1:8.2f} Cost:{2:8.2f}, Comm:{3:8.2f}'.format(
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm ))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price:{0:8.2f},Size:{1:8.2f} Cost:{2:8.2f}, Comm:{3:8.2f}'.format(
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm ))
            self.bar_executed = len(self)
        # 3.If order is canceled/margin/rejected,report order canceled
        elif order.status in [order.Canceled,order.Margin,order.Rejected]:
            self.Log('Order Canceled/Margin/Rejected')
        

    def next(self):
        cash = self.broker.get_cash()
        value = self.broker.get_value()
        size = int(cash/self.data.close[0])
        
        # Order 가 Pending 인지 확인,그렇다면 다시 주문할 수 없음
        if self.order:
            return
        if not self.position: # not in the market
            if self.smaSlow < self.data.close[0]:
                self.order = self.buy(size=size)
        elif self.getposition().size > 0: # in the market
            if self.smaSlow > self.data.close[0]:
                self.order = self.sell(size=self.getposition().size)
# SmaCross(이평선 교차) 전략
class SmaCross(bt.Strategy):
        # list of parameters which are configurable for the strategy
        params = dict(
            pfast=10,  # period for the fast moving average
            pslow=30   # period for the slow moving average
        )

        def __init__(self):
            sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
            sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
            self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

        def next(self):
            if not self.position:  # not in the market
                if self.crossover > 0:  # if fast crosses slow to the upside
                    self.buy()  # enter long

            elif self.crossover < 0:  # in the market & cross to the downside
                self.close()  # close long position
                
# firstStratey 전략                
class firstStrategy(bt.Strategy):

      def __init__(self):
          self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

      def next(self):
          if not self.position:
              if self.rsi < 30:
                  self.buy(size=100)
          else:
              if self.rsi > 70:
                  self.sell(size=100)