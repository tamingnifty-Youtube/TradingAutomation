from dhanhq import dhanhq
import pandas as pd

dhan = dhanhq("CLIENT_ID","ACCESS_TOKEN_HERE")


# Place an order for Equity Cash
OHLC = dhan.historical_daily_data(security_id=13, exchange_segment='IDX_I', instrument_type='INDEX', from_date="2025-05-05", to_date="2025-11-11")
df = pd.DataFrame(OHLC['data'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
print(df)