import yfinance as yf
import pandas as pd
from pathlib import Path

# Load tickers from symbols_sp500.txt
symbols = [s.strip() for s in Path('symbols_sp500.txt').read_text().splitlines() if s.strip()]

data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

# Define date range
start = "2015-01-01"
end = "2025-01-01"

for sym in symbols:
    print(f"Downloading {sym}...")
    df = yf.download(sym, start=start, end=end)
    if not df.empty:
        df.reset_index(inplace=True)
        df.to_csv(data_dir / f"{sym}.csv", index=False)
    else:
        print(f"⚠️ No data for {sym}")

print("✅ All done! Files saved in /data")
