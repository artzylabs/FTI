# Algorithmic Trading Foundations - Momentum and Mean Reversion

This repository extends the principles introduced in *Ernest P. Chan’s*  
**Algorithmic Trading: Winning Strategies and Their Rationale**, Chapters 1-3.  
It translates the theory of bias-free backtesting and disciplined implementation into executable strategies using **Python**, **pandas**, and **backtrader**.

---

## Ⅰ. Purpose

A trading system is only as reliable as the experiment that tests it.  
This project moves through the same conceptual arc as Chan’s first three chapters:

1. **Chapter 1 — Backtesting Discipline**  
   Backtests are experiments. Every run here models commissions, bid-ask spread, and next-bar execution to prevent look-ahead bias.  
   The research and live logic share identical code to eliminate “translation errors.”

2. **Chapter 2 - Testing for Stationarity and Mean Reversion**  
   Perfect stationarity is rare; partial stationarity can be traded cautiously.  
   The *MeanRevertZ* strategy detects statistical over-extensions in normalized short-term returns and exits on mean touch, stop-loss, or time decay.

3. **Chapter 3 - Implementing Trading Rules**  
   Theory becomes code. The *MomentumTS* strategy follows time-series momentum—holding assets that have recently appreciated-and scales exposure inversely with recent volatility.

---

## Ⅱ. Strategies Implemented

### 🔹 Momentum TS
> “If it has gone up, buy it; if it has gone down, sell it - but test honestly.”    
> — E. Chan, Ch. 3

**Signal:** L-day cumulative return  
**Rule:** Go long if return > 0, else flat  
**Positioning:** Volatility-targeted so each symbol contributes similar risk  
**Objective:** Demonstrate persistence of returns under realistic frictions

---

### 🔹 Mean Revert Z
> “Stationarity is rare and fragile; treat it as a guest, not a tenant.”    
> — E. Chan, Ch. 2

**Signal:** Z-score of daily returns vs. rolling mean & standard deviation  
**Entry:** z < –k (oversold)  
**Exit:** z ≥ 0 or stop-loss or max-hold expiry  
**Objective:** Trade short-term statistical over-reaction while capping drawdown risk

---

## Ⅲ. Methodological Integrity (Chapter 1 Principles)

- **Data Hygiene:** Clean CSVs, parsed dates, numeric coercion, chronological sort  
- **Execution Realism:** Next-bar fills only; 5 bps slippage; $0.003/share commission  
- **Code Parity:** Identical logic for backtest and live  
- **Bias Awareness:** Uses current S&P 500 tickers → mild survivorship bias acknowledged

---

## Ⅳ. Typical Output (2015 – 2024, 10 S&P Symbols)

| Strategy | Ann Return | Ann Vol | Sharpe | Max DD | Win Rate |
|-----------|-------------|----------|---------|----------|-----------|
| Momentum TS | ≈ 19 % | ≈ 16 % | 1.2 | −28 % | ≈ 40 % |
| Mean Revert Z | ≈ 1 % | ≈ 4 % | 0.25 | −11 % | ≈ 56 % |

Momentum thrives in persistent regimes; mean reversion survives by restraint.

---

## Ⅴ. Structure

```

strategies/
│   ├─ momentum.py     
│   └─ meanrevert.py   
metrics.py              
run_backtests.py        
fetch_data.py           
symbols_sp500.txt       # Universe list
requirements.txt
.gitignore
LICENSE

````

---

## Ⅵ. Usage

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python fetch_data.py          # download data
python run_backtests.py       # run strategies
````

---

## Ⅶ. Interpretation

* **High Sharpe** → clean signal + honest costs
* **Large Drawdown** → insufficient diversification or regime shift
* **Flat Performance** → data-snooping or non-stationary signal

Each result passes through Chan’s four validation gates: **Bias**, **Mechanics**, **Execution**, and **Regime**.
