import backtrader as bt

class MeanRevertZ(bt.Strategy):
    """
    Return z-score mean reversion with max-hold + stop.
    - Signal: 1-day returns standardized over a rolling window
    - Entry: z < -k (oversold)
    - Exit: z >= 0 (mean touch) OR stop OR max-hold
    """
    params = dict(
        lookback=20,     # window for mean/std of returns
        k=2.0,           # z-score threshold
        target_pct=0.10, # portfolio % per symbol
        max_hold=10,     # bars
        stop_pct=0.05,   # 5% protective stop from entry price
        long_only=True   # start long-only; add shorts later
    )

    def __init__(self):
        # 1-day returns
        self.ret = {d: bt.indicators.PercentChange(d.close, period=1) for d in self.datas}
        self.rmu = {d: bt.indicators.SMA(self.ret[d], period=self.p.lookback) for d in self.datas}
        self.rsd = {d: bt.indicators.StdDev(self.ret[d], period=self.p.lookback) for d in self.datas}
        self.z   = {d: (self.ret[d] - self.rmu[d]) / (self.rsd[d] + 1e-12) for d in self.datas}

        # track entry for max-hold/stop
        self.entry_idx = {d: None for d in self.datas}
        self.entry_px  = {d: None for d in self.datas}

    def next(self):
        for d in self.datas:
            if len(d) < self.p.lookback + 2:
                continue

            z = float(self.z[d][0])
            pos = self.getposition(d).size

            # entries
            if pos == 0:
                if z < -self.p.k:
                    if self.p.long_only:
                        self.order_target_percent(data=d, target=self.p.target_pct)
                        self.entry_idx[d] = len(d)
                        self.entry_px[d]  = d.close[0]
                    else:
                        self.order_target_percent(data=d, target=self.p.target_pct)
                        self.entry_idx[d] = len(d)
                        self.entry_px[d]  = d.close[0]
                elif (not self.p.long_only) and (z > self.p.k):
                    self.order_target_percent(data=d, target=-self.p.target_pct)
                    self.entry_idx[d] = len(d)
                    self.entry_px[d]  = d.close[0]
                continue

            # exits
            held = 0 if self.entry_idx[d] is None else (len(d) - self.entry_idx[d])
            px0  = self.entry_px[d] if self.entry_px[d] is not None else d.close[0]

            # mean touch exit
            mean_touch = (pos > 0 and z >= 0) or (pos < 0 and z <= 0)

            # stop-loss (5% from entry)
            if pos > 0:
                stopped = d.close[0] <= (1 - self.p.stop_pct) * px0
            else:
                stopped = d.close[0] >= (1 + self.p.stop_pct) * px0  # for shorts when enabled

            # max hold
            timeout = held >= self.p.max_hold

            if mean_touch or stopped or timeout:
                self.close(data=d)
                self.entry_idx[d] = None
                self.entry_px[d]  = None
