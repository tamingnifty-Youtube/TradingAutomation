from datetime import datetime
from time import sleep
from dateutil import parser
from dotenv import find_dotenv
from dotenv import load_dotenv
from tamingnifty import connect_definedge as edge
from tamingnifty import utils as util
import os
from pymongo import MongoClient

dotenv_file: str = find_dotenv()
load_dotenv(dotenv_file)

# MongoDB connection string
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
mongo_client = MongoClient(CONNECTION_STRING)
strategies = mongo_client['TradingSystems']['strangle']

slack_token = os.getenv("slack_token")
slack_client = util.get_slack_client(token=slack_token)

def record_details_in_mongo(call_option_symbol, put_option_symbol, strangle_entry_price, strategy_state, entry_time, expiry):
    util.notify("Recording strategy details in MongoDB...", slack_channel="strangle", slack_client=slack_client)
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
    util.notify(f"Nifty LTP: {nifty_close}", slack_channel="strangle", slack_client=slack_client)
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
    util.notify("Exiting Strangle Strategy...", slack_channel="strangle", slack_client=slack_client)
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
    strategies.update_one({'_id': strategy['_id']}, {'$set': {'running_pnl': round(running_pnl,2)}})
    print(f"Running PnL: {round(running_pnl,2)}")
    return round(running_pnl,2)   

while True:
    current_time = datetime.now().time()
    util.notify("While Loop started for Strangle bot", slack_channel="strangle", slack_client=slack_client)
    if current_time >= parser.parse("09:20:00").time():
        if strategies.count_documents({'strategy_state': 'active'}) > 0:
            util.notify("Active Strangle Strategy Found, Monitoring...", slack_channel="strangle", slack_client=slack_client)
            strategy = strategies.find_one({'strategy_state': 'active'})
            # for strategy in active_strategies:
            if strategy['strategy_state'] == "active" and strategy['running_pnl'] < strategy['stop_loss']:
                util.notify("Stop Loss Hit, Exiting Strangle...", slack_channel="strangle", slack_client=slack_client)
                exit_strangle("Stop Loss Hit")
                break
            elif strategy['strategy_state'] == "active" and strategy['running_pnl'] > strategy['target']:
                util.notify("Target Achieved, Exiting Strangle...", slack_channel="strangle", slack_client=slack_client)
                exit_strangle("Target Achieved")
                break
            elif strategy['strategy_state'] == "active" and current_time >= parser.parse("15:00:00").time():
                util.notify("Market Close Time Reached, Exiting Strangle...", slack_channel="strangle", slack_client=slack_client)
                exit_strangle("Market Close")
                break
            elif strategy['strategy_state'] == "active" and strategy['max_pnl_reached'] < get_pnl(strategy):
                util.notify("Updating Max PnL Reached and Adjusting Stop Loss...", slack_channel="strangle", slack_client=slack_client)
                max_pnl_reached = get_pnl(strategy)
                stop_loss = strategy['stop_loss'] + max_pnl_reached
                util.notify(f"New Stop Loss Set at {round(stop_loss,2)}", slack_channel="strangle", slack_client=slack_client)
                strategies.update_one({'_id': strategy['_id']}, {'$set': {'max_pnl_reached': max_pnl_reached, 'stop_loss': round(stop_loss,2)}})
            elif strategy['min_pnl_reached'] > get_pnl(strategy):
                util.notify("Updating Min PnL Reached...", slack_channel="strangle", slack_client=slack_client)
                strategies.update_one({'_id': strategy['_id']}, {'$set': {'min_pnl_reached': get_pnl(strategy)}})
        else:
            util.notify("No Active Strangle Strategy Found, Creating New Strangle...", slack_channel="strangle", slack_client=slack_client)
            create_strangle()
    else:
        util.notify("Market Not Open Yet for Strangle Bot", slack_channel="strangle", slack_client=slack_client)
    
    sleep(10)  # Wait for 10 seconds before next check

    

