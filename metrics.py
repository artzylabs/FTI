import numpy as np
import pandas as pd

TRADING_DAYS = 252

def summarize_metrics(daily_ret: pd.Series, riskfree=0.0):
    r = daily_ret.fillna(0.0)
    ex = r - riskfree/ TRADING_DAYS
    ann_ret = (1 + r).prod() ** (TRADING_DAYS/len(r)) - 1
    ann_vol = r.std(ddof=1) * np.sqrt(TRADING_DAYS)
    sharpe  = 0.0 if ann_vol == 0 else (ann_ret - riskfree) / ann_vol

    downside = r[r < 0]
    ds_vol = 0.0 if downside.empty else downside.std(ddof=1) * np.sqrt(TRADING_DAYS)
    sortino = np.nan if ds_vol == 0 else (ann_ret - riskfree) / ds_vol

    # Max drawdown
    equity = (1 + r).cumprod()
    peak = equity.cummax()
    dd = (equity / peak) - 1.0
    max_dd = dd.min()

    return pd.Series({
        'AnnReturn': ann_ret,
        'AnnVol': ann_vol,
        'Sharpe': sharpe,
        'Sortino': sortino,
        'MaxDrawdown': max_dd,
        'Days': len(r)
    })
