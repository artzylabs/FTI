import math
import backtrader as bt

class MomentumTS(bt.Strategy):
    """
    Time-series momentum with basic vol targeting.
    - Signal: L-day return > 0 => long next bar, else flat (start long-only)
    - Position size scales down when recent volatility is high
    """
    params = dict(
        lookback=126,     # ~6 months
        vol_lookback=20,  # for realized vol
        base_risk=0.10,   # max target % per symbol
        long_only=True
    )

    def __init__(self):
        self.lag_close = {d: d.close(-self.p.lookback) for d in self.datas}
        # realized daily vol (stdev of pct change) over 20 bars
        self.daily_ret = {d: bt.indicators.PercentChange(d.close, period=1) for d in self.datas}
        self.vol = {d: bt.indicators.StdDev(self.daily_ret[d], period=self.p.vol_lookback) for d in self.datas}

    def next(self):
        for d in self.datas:
            if len(d) <= max(self.p.lookback, self.p.vol_lookback) + 1:
                continue

            # L-day return
            past = float(self.lag_close[d][0])
            if past == 0 or math.isnan(past):
                continue
            ret_L = d.close[0] / past - 1.0

            # basic vol target: smaller weight if vol is high
            vol = float(self.vol[d][0])
            # annualize daily vol roughly for scaling
            ann_vol = vol * math.sqrt(252) if vol == vol else None
            # inverse-vol cap; clamp to base_risk
            target = self.p.base_risk
            if ann_vol and ann_vol > 0:
                target = min(self.p.base_risk, self.p.base_risk / (ann_vol / 0.20))  # aim around 20% ann vol

            pos = self.getposition(d).size

            if self.p.long_only:
                if ret_L > 0 and pos <= 0:
                    self.order_target_percent(data=d, target=target)
                elif ret_L <= 0 and pos > 0:
                    self.close(data=d)
            else:
                if ret_L > 0 and pos <= 0:
                    self.order_target_percent(data=d, target=target)
                elif ret_L <= 0 and pos >= 0:
                    self.order_target_percent(data=d, target=-target)
