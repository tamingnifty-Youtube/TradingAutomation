from datetime import datetime
from dateutil import parser
from pprint import pprint
from dotenv import find_dotenv
from dotenv import load_dotenv
from tamingnifty import connect_definedge as edge

dotenv_file: str = find_dotenv()
load_dotenv(dotenv_file)

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
    connection = edge.login_to_integrate()
    nifty_close = edge.fetch_ltp(connection, 'NSE', 'Nifty 50')
    print(f"Nifty LTP: {nifty_close}")
    atm_strike = round(nifty_close / 50) * 50
    call_strike = atm_strike + 50
    put_strike = atm_strike - 50
    call_option_symbol, expiry = edge.get_index_option_symbol(call_strike, "CE")
    put_option_symbol, expiry = edge.get_index_option_symbol(put_strike, "PE")
    sell_price_call = edge.fetch_ltp(connection, 'NFO', call_option_symbol)
    sell_price_put = edge.fetch_ltp(connection, 'NFO', put_option_symbol)
    strangle_entry_price = sell_price_call + sell_price_put
    strategy['instrument_name'] = f"Nifty Strangle"
    strategy['call_option_symbol'] = call_option_symbol
    strategy['put_option_symbol'] = put_option_symbol
    strategy['strangle_entry_price'] = strangle_entry_price
    strategy['strategy_state'] = "Active"
    strategy['entry_time'] = datetime.now().strftime('%H:%M')
    strategy['expiry'] = expiry
    pprint(strategy)

def exit_strangle(reason):
    buy_price_call = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['call_option_symbol'])
    buy_price_put = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['put_option_symbol'])
    strangle_exit_price = buy_price_call + buy_price_put
    strategy['strangle_exit_price'] = strangle_exit_price
    strategy['exit_time'] = datetime.now().strftime('%H:%M')
    strategy['strategy_state'] = "Exited"
    strategy['exit_reason'] = reason
    strategy['pnl'] = (strategy['strangle_entry_price'] - strategy['strangle_exit_price']) * strategy['quantity']
    strategy['net_pnl'] = strategy['pnl'] - .002 * abs(strategy['pnl'])
    pprint(strategy)

def get_pnl():
    current_call_price = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['call_option_symbol'])
    current_put_price = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['put_option_symbol'])
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

    

