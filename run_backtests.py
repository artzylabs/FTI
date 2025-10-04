import backtrader as bt
import pandas as pd
from pathlib import Path
from strategies.momentum import MomentumTS
from strategies.meanrevert import MeanRevertZ
import metrics as m

CASH = 100_000
COMMISSION_PER_SHARE = 0.003      # e.g., $0.003/share
SLIPPAGE_PCT = 0.001             # 5 bps per trade
RISKFREE = 0.0

def load_csv(path):
    import numpy as np
    df = pd.read_csv(path, parse_dates=['Date'])

    # Keep only needed columns, coerce numerics
    needed = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name} missing columns: {missing} (has {list(df.columns)})")

    for c in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[c] = (
            df[c].astype(str)
                 .str.replace(',', '', regex=False)
                 .str.strip()
        )
        df[c] = pd.to_numeric(df[c], errors='coerce')

    df = df.dropna(subset=['Open','High','Low','Close','Volume'])
    df = df.sort_values('Date').set_index('Date')

    # Print a tiny diagnostic so we SEE rows and dates
    if len(df) == 0:
        print(f"⚠️ {path.name}: 0 rows after cleaning")
    else:
        print(f"✓ {path.name}: {len(df)} rows [{df.index.min().date()} → {df.index.max().date()}]")

    # Explicitly map column names for Backtrader
    feed = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=-1
    )
    return feed


def run_strategy(strategy_cls, symbols):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(CASH)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.broker.set_slippage_perc(SLIPPAGE_PCT)

    class PerShare(bt.CommInfoBase):
        params = dict(commission=COMMISSION_PER_SHARE, percabs=False, stocklike=True)
        def _getcommission(self, size, price, pseudoexec):
            return abs(size) * self.p.commission
    cerebro.broker.addcommissioninfo(PerShare())

    cerebro.addstrategy(strategy_cls)   # <— add your strategy to the engine

    for s in symbols:
        p = Path('data') / f'{s}.csv'
        if p.exists():
            cerebro.adddata(load_csv(p), name=s)

    
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns', timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days,
                        annualize=True, riskfreerate=RISKFREE)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')

    res = cerebro.run(maxcpus=1)[0]
    daily = pd.Series(res.analyzers.returns.get_analysis())
    ta = res.analyzers.trades.get_analysis()
    dd = res.analyzers.dd.get_analysis()

    # small summary
    closed = ta.total.closed if hasattr(ta, 'total') else 0
    won = ta.won.total if hasattr(ta, 'won') else 0
    lost = ta.lost.total if hasattr(ta, 'lost') else 0
    winrate = won / closed if closed else 0
    print(f"Trades closed: {closed}, Win rate: {winrate:.2%}, Max DD: {dd.max.drawdown:.1f}%")

    perf = m.summarize_metrics(daily, riskfree=RISKFREE)
    return perf, cerebro.broker.getvalue()


if __name__ == '__main__':
    # tiny demo universe; replace with your txt list
    symbols = [s.strip() for s in Path('symbols_sp500.txt').read_text().splitlines() if s.strip()]
    perf_mom, val_mom = run_strategy(MomentumTS, symbols)
    perf_mr,  val_mr  = run_strategy(MeanRevertZ, symbols)

    print('\n=== Momentum TS ===')
    print(perf_mom)
    print('\n=== Mean Revert Z ===')
    print(perf_mr)
