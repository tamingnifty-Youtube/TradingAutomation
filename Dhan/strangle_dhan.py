from datetime import datetime
from dateutil import parser
from pprint import pprint
from dotenv import find_dotenv
from dotenv import load_dotenv

from Dhan_Tradehull import Tradehull
import os


dotenv_file: str = find_dotenv()
load_dotenv(dotenv_file)

tsl = Tradehull(os.getenv("client_code"), os.getenv("token_id"))

strategy = {
'instrument_name': "",
'quantity': 75,
'strategy_state': None,
'entry_date': str(datetime.now().date()),
'exit_date': str(datetime.now().date()),
'entry_time' : '',
'exit_time' : '',
'stop_loss': -1000,
'target': 2000,
'call_option_symbol': "",
'put_option_symbol': "",
'expiry': "",
'strangle_entry_price': 0,
'strangle_exit_price': 0,
'running_pnl' : 0,
'exit_reason': '',
'pnl': '',
'net_pnl': '',
'max_pnl_reached': 0,
'min_pnl_reached': 0
}

def create_strangle():
    data = tsl.get_ltp_data(names=['NIFTY'])
    nifty_close = data['NIFTY']
    print(f"Nifty Close Price: {nifty_close}")
    call_option_symbol, put_option_symbol, call_strike, put_strike = tsl.OTM_Strike_Selection(Underlying='NIFTY', Expiry=0, OTM_count=1)
 
    data = tsl.get_ltp_data(names=[call_option_symbol])
    sell_price_call = data[call_option_symbol]

    data = tsl.get_ltp_data(names=[put_option_symbol])
    sell_price_put = data[put_option_symbol]

    strangle_entry_price = sell_price_call + sell_price_put
    strategy['instrument_name'] = f"Nifty Strangle"
    strategy['call_option_symbol'] = call_option_symbol
    strategy['put_option_symbol'] = put_option_symbol
    strategy['strangle_entry_price'] = strangle_entry_price
    strategy['strategy_state'] = "Active"
    strategy['entry_time'] = datetime.now().strftime('%H:%M')
    pprint(strategy)

def exit_strangle(reason):
    buy_price_call = tsl.get_ltp_data(names=[strategy['call_option_symbol']])[strategy['call_option_symbol']]
    buy_price_put = tsl.get_ltp_data(names=[strategy['put_option_symbol']])[strategy['put_option_symbol']]

    strangle_exit_price = buy_price_call + buy_price_put
    strategy['strangle_exit_price'] = strangle_exit_price
    strategy['exit_time'] = datetime.now().strftime('%H:%M')
    strategy['strategy_state'] = "Exited"
    strategy['exit_reason'] = reason
    strategy['pnl'] = (strategy['strangle_entry_price'] - strategy['strangle_exit_price']) * strategy['quantity']
    strategy['net_pnl'] = strategy['pnl'] - .002 * abs(strategy['pnl'])
    pprint(strategy)

def get_pnl():
    data = tsl.get_ltp_data(strategy['call_option_symbol'])
    current_call_price = data[strategy['call_option_symbol']]
    data = tsl.get_ltp_data(strategy['put_option_symbol'])
    current_put_price = data[strategy['put_option_symbol']]
    current_strangle_price = current_call_price + current_put_price
    running_pnl = (strategy['strangle_entry_price'] - current_strangle_price) * strategy['quantity']
    strategy['running_pnl'] = running_pnl
    return running_pnl  

while True:
    current_time = datetime.now().time()
    if current_time >= parser.parse("07:20:00").time():
        if strategy['strategy_state'] == None:
            create_strangle()
        elif strategy['strategy_state'] == "Active" and strategy["running_pnl"] < strategy['stop_loss']:
            exit_strangle("Stop Loss Hit")
            break
        elif strategy['strategy_state'] == "Active" and strategy["running_pnl"] > strategy['target']:
            exit_strangle("Target Achieved")
            break
        elif strategy['strategy_state'] == "Active" and current_time >= parser.parse("15:00:00").time():
            exit_strangle("Market Close")
            break
        elif strategy['strategy_state'] == "Active" and strategy['max_pnl_reached'] < get_pnl():
            strategy['max_pnl_reached'] = get_pnl()
            strategy['stop_loss'] = strategy['stop_loss'] + strategy['max_pnl_reached']
        elif strategy['min_pnl_reached'] > get_pnl():
            strategy['min_pnl_reached'] = get_pnl()
    else:
        print("Waiting for market to open...")

    

