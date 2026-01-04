from datetime import datetime
from dateutil import parser
from dotenv import find_dotenv
from dotenv import load_dotenv
from tamingnifty import connect_definedge as edge

from pymongo import MongoClient

# MongoDB connection string
CONNECTION_STRING = "mongodb+srv://adminuser:edX4mktR69lZ4K8M@tradingcluster.xux7hfc.mongodb.net/"
mongo_client = MongoClient(CONNECTION_STRING)
strategies = mongo_client['TradingSystems']['strangle']


dotenv_file: str = find_dotenv()
load_dotenv(dotenv_file)

def record_details_in_mongo(call_option_symbol, put_option_symbol, strangle_entry_price, strategy_state, entry_time, expiry):
    strategy = {
    'instrument_name': "Nifty Strangle",
    'quantity': 65,
    'strategy_state': strategy_state,
    'entry_date': str(datetime.now().date()),
    'exit_date': str(datetime.now().date()),
    'entry_time' : entry_time,
    'exit_time' : '',
    'stop_loss': -1000,
    'target': 2000,
    'call_option_symbol': call_option_symbol,
    'put_option_symbol': put_option_symbol,
    'expiry': str(expiry),
    'strangle_entry_price': strangle_entry_price,
    'strangle_exit_price': 0,
    'running_pnl' : 0,
    'exit_reason': '',
    'pnl': '',
    'net_pnl': '',
    'max_pnl_reached': 0,
    'min_pnl_reached': 0
    }
    strategies.insert_one(strategy)

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
    record_details_in_mongo(call_option_symbol=call_option_symbol, put_option_symbol=put_option_symbol, strangle_entry_price=strangle_entry_price, strategy_state="active", entry_time=datetime.now().strftime('%H:%M'), expiry=expiry)

def exit_strangle(reason):
    strategy = strategies.find_one({'strategy_state': 'active'})
    buy_price_call = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['call_option_symbol'])
    buy_price_put = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['put_option_symbol'])
    strangle_exit_price = buy_price_call + buy_price_put
    pnl = (strategy['strangle_entry_price'] - strangle_exit_price) * strategy['quantity']
    net_pnl = pnl - .002 * abs(pnl)
    strategies.update_one({'_id': strategy['_id']}, {'$set': {'strangle_exit_price': strangle_exit_price, 'exit_time': datetime.now().strftime('%H:%M'), 'strategy_state': "Exited", 'exit_reason': reason, 'pnl': pnl, 'net_pnl': net_pnl}})

def get_pnl(strategy):
    current_call_price = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['call_option_symbol'])
    current_put_price = edge.fetch_ltp(edge.login_to_integrate(), 'NFO' , strategy['put_option_symbol'])
    current_strangle_price = current_call_price + current_put_price
    running_pnl = (strategy['strangle_entry_price'] - current_strangle_price) * strategy['quantity']
    strategies.update_one({'_id': strategy['_id']}, {'$set': {'running_pnl': running_pnl}})
    return running_pnl   

while True:
    current_time = datetime.now().time()
    if current_time >= parser.parse("09:20:00").time():
        if strategies.count_documents({'strategy_state': 'active'}) > 0:
            strategy = strategies.find_one({'strategy_state': 'active'})
            # for strategy in active_strategies:
            if strategy['strategy_state'] == "active" and strategy['running_pnl'] < strategy['stop_loss']:
                exit_strangle("Stop Loss Hit")
                break
            elif strategy['strategy_state'] == "active" and strategy['running_pnl'] > strategy['target']:
                exit_strangle("Target Achieved")
                break
            elif strategy['strategy_state'] == "active" and current_time >= parser.parse("15:00:00").time():
                exit_strangle("Market Close")
                break
            elif strategy['strategy_state'] == "active" and strategy['max_pnl_reached'] < get_pnl(strategy):
                max_pnl_reached = get_pnl(strategy)
                stop_loss = strategy['stop_loss'] + max_pnl_reached
                strategies.update_one({'_id': strategy['_id']}, {'$set': {'max_pnl_reached': max_pnl_reached, 'stop_loss': stop_loss}})
            elif strategy['min_pnl_reached'] > get_pnl(strategy):
                strategies.update_one({'_id': strategy['_id']}, {'$set': {'min_pnl_reached': get_pnl(strategy)}})
        else:
            create_strangle()
    else:
        print("Waiting for market to open...")

    

