import pyotp
import pandas as pd
from integrate import ConnectToIntegrate, IntegrateData
from datetime import datetime, timedelta
pd.set_option('display.max_rows', None)



api_token = "TOKEN_FROM_PORTAL"
api_secret = "SECRET_FROM_PORTAL"
conn = ConnectToIntegrate()
totp = pyotp.TOTP("TOTP_FROM_PORTAL").now()
conn.login(api_token=api_token, api_secret=api_secret, totp=totp)
days_ago = datetime.now() - timedelta(days=90)
start = days_ago.replace(hour=9, minute=15, second=0, microsecond=0)

ic = IntegrateData(conn)
history = ic.historical_data(
    exchange='NSE',
    trading_symbol='Nifty 50',
    timeframe=conn.TIMEFRAME_TYPE_DAY,  # Use the specific timeframe value
    start=start,
    end=datetime.today(),
)

df = pd.DataFrame(list(history))

print("\n***** Fetched OHLC Data *****\n")
print(df.iloc[-10:])






    