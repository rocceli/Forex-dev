from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import time  

def market_order(symbol, volume,order_type, **kwargs):
    tick = mt5.symbol_info_tick(symbol)
    order_dict = {'buy':0 ,'sell':1}
    price_dict = {'buy': tick.ask , 'sell': tick.bid}
    request = {
        "action":mt5.TRADE_ACTION_DEAL,
        "symbol":symbol,
        "volume":volume,
        "type":order_dict[order_type],
        "price":price_dict[order_type],
        "deviation":DEVIATION,
        "magic":100,
        "Comment":"python market order",
        "type_time":mt5.ORDER_TIME_GTC,
        "type_filling":mt5.ORDER_FILLING_IOC
    }
     # Set stop loss and take profit if provided
    # if stop_loss is not None:
    #     request["sl"] = stop_loss  # Stop loss level
    # if take_profit is not None:
    #     request["tp"] = take_profit  # Take profit level
    order_result = mt5.order_send(request)
    print(order_result)

    return order_result


def signal(symbol,time_frame,sma_period):
    bars = mt5.copy_rates_from_pos(symbol,time_frame,1,sma_period)
    bars_df = pd.DataFrame(bars)

    last_close = bars_df.iloc[-1].close
    sma = bars_df.close.mean()

    direction = 'flat'
    if last_close > sma :
        direction = 'buy'
    elif last_close < sma :
        direction = 'sell'

    return last_close,sma,direction

def close_order(ticket):
    positions = mt5.positions_get()

    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        type_dict={0: 1,1: 0}
        price_dict = {0 : tick.ask ,1 : tick.bid}

        if pos.ticket == ticket :
            request = {
                "action":mt5.TRADE_ACTION_DEAL,
                "symbol":pos.symbol,
                "volume":pos.volume,
                "type":type_dict[pos.type],
                "price":price_dict[pos.type],
                "deviation":DEVIATION,
                "magic":100,
                "Comment":"python close order",
                "type_time":mt5.ORDER_TIME_GTC,
                "type_filling":mt5.ORDER_FILLING_IOC
            }
            order_result = mt5.order_send(request)
            return order_result
        else:
            return 'Order does not exist'

def get_exposure(symbol):
    positions = mt5.positions_get(symbol = symbol)
    if positions:
        pos_df = pd.DataFrame(positions, columns = positions[0]._asdict().keys())
        exposure = pos_df['volume'].sum()

        return exposure
if __name__ == '__main__':

        SYMBOL = 'GBPUSD'
        VOLUME = 0.70
        TIMEFRAME = mt5.TIMEFRAME_M1
        SMA_PERIOD = 10
        DEVIATION = 20

        mt5.initialize()

        while True :
             exposure = get_exposure(SYMBOL)

             last_close ,sma,direction = signal(SYMBOL,TIMEFRAME,SMA_PERIOD)

             if direction == 'buy':
                  for pos in mt5.positions_get():
                    if pos.type == 1:
                        close_order(pos.ticket)

                    if not mt5.positions_get():
                        market_order(SYMBOL,VOLUME,direction)
             elif direction == 'sell':
                    # Get all positions
                    positions = mt5.positions_get()

                    # Filter positions that match your criteria (symbol, volume, and direction)
                    filtered_positions = [pos for pos in positions if pos.symbol == SYMBOL and pos.volume == VOLUME and pos.type == 0]

                    # Close each filtered position
                    for pos in filtered_positions:
                        close_order(pos.ticket)

            #  elif direction == 'sell':
            #      for pos in mt5.positions_get(SYMBOL,VOLUME,direction):
            #          if pos.type == 0 :
            #              close_order(pos.ticket)

                    
                    if not mt5.positions_get(SYMBOL,VOLUME,direction):
                        market_order(SYMBOL,VOLUME,direction)

                
             print('time:' , datetime.now())
             print('exposure:',exposure)
             print('last_close', last_close)
             print('sma: ',sma)
             print('signal:', direction)
             print('--------------\n')
             time.sleep(1)