"""
MMDE v2 — MetaTrader 5 Bridge
─────────────────────────────
PURPOSE:
  Connects MMDE engine to MT5 for:
  1. Reading live OHLCV candle data
  2. Sending trade signals to MT5
  3. Reading open positions
  4. Closing trades

REQUIREMENTS:
  pip install MetaTrader5
  MT5 must be installed on Windows or Wine on Linux
  MT5 account must be logged in

USAGE:
  from mmde_engine.mt5_bridge.bridge import MT5Bridge
  bridge = MT5Bridge()
  bridge.connect()
  candles = bridge.get_candles('EURUSD', '1H', 60)
  bridge.send_signal(result)  # result from MMDE engine
"""
import os

MT5_AVAILABLE = False
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    pass

class MT5Bridge:
    def __init__(self):
        self.connected = False
        self.available = MT5_AVAILABLE

    def connect(self, login=None, password=None, server=None) -> bool:
        if not self.available:
            print('[MT5] MetaTrader5 package not installed. Run: pip install MetaTrader5')
            return False
        if not mt5.initialize():
            print(f'[MT5] Initialization failed: {mt5.last_error()}')
            return False
        if login and password and server:
            authorized = mt5.login(login, password=password, server=server)
            if not authorized:
                print(f'[MT5] Login failed: {mt5.last_error()}')
                return False
        self.connected = True
        info = mt5.account_info()
        print(f'[MT5] Connected: {info.name} | Balance: {info.balance} {info.currency}')
        return True

    def disconnect(self):
        if self.available and self.connected:
            mt5.shutdown()
            self.connected = False

    def get_candles(self, symbol: str, timeframe: str, count: int = 60) -> list:
        """Fetch OHLCV candles from MT5"""
        if not self.connected:
            raise RuntimeError('Not connected to MT5')

        tf_map = {
            'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15, 'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1, 'W1': mt5.TIMEFRAME_W1,
        }
        tf = tf_map.get(timeframe.upper(), mt5.TIMEFRAME_H1)
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)

        if rates is None:
            raise ValueError(f'No data for {symbol}: {mt5.last_error()}')

        candles = []
        for r in rates:
            candles.append({
                'timestamp': str(r['time']),
                'open':  float(r['open']),
                'high':  float(r['high']),
                'low':   float(r['low']),
                'close': float(r['close']),
                'volume': int(r['tick_volume']),
            })
        return candles

    def get_current_price(self, symbol: str) -> dict:
        if not self.connected: return {}
        tick = mt5.symbol_info_tick(symbol)
        if not tick: return {}
        return {'bid': tick.bid, 'ask': tick.ask, 'time': tick.time}

    def send_signal(self, mmde_result: dict, symbol: str, lot: float = 0.01) -> dict:
        """
        OPTIONAL: Send MMDE trade decision to MT5.
        Only executes if action is BUY or SELL.
        Always uses stop loss from MMDE risk engine.
        """
        if not self.connected:
            return {'status': 'error', 'message': 'Not connected'}

        action = mmde_result.get('action', 'WAIT')
        if action not in ['BUY', 'SELL']:
            return {'status': 'skipped', 'reason': f'Action is {action} — no trade placed'}

        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return {'status': 'error', 'message': f'No tick data for {symbol}'}

        price = tick.ask if action == 'BUY' else tick.bid
        sl_str = mmde_result.get('stop_loss', '')
        tp_str = mmde_result.get('take_profit', [''])[0] if mmde_result.get('take_profit') else ''

        try:
            sl = float(sl_str) if sl_str and 'manually' not in str(sl_str) else 0
            tp = float(tp_str) if tp_str and 'TP' not in str(tp_str) else 0
        except:
            return {'status': 'error', 'message': 'Could not parse SL/TP from MMDE output. Set manually.'}

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': lot,
            'type': mt5.ORDER_TYPE_BUY if action == 'BUY' else mt5.ORDER_TYPE_SELL,
            'price': price,
            'sl': sl,
            'tp': tp,
            'comment': f'MMDE v2 | conf:{mmde_result.get("confidence_pct","?")}',
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return {'status': 'executed', 'ticket': result.order, 'price': result.price, 'volume': lot}
        else:
            return {'status': 'failed', 'retcode': result.retcode, 'comment': result.comment}

    def get_open_positions(self) -> list:
        if not self.connected: return []
        positions = mt5.positions_get()
        if not positions: return []
        return [{'ticket': p.ticket, 'symbol': p.symbol, 'type': 'BUY' if p.type == 0 else 'SELL',
                 'volume': p.volume, 'price_open': p.price_open, 'sl': p.sl,
                 'tp': p.tp, 'profit': p.profit} for p in positions]

    def close_position(self, ticket: int) -> dict:
        if not self.connected: return {'status': 'error'}
        position = mt5.positions_get(ticket=ticket)
        if not position: return {'status': 'error', 'message': 'Position not found'}
        p = position[0]
        close_type = mt5.ORDER_TYPE_SELL if p.type == 0 else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(p.symbol)
        close_price = tick.bid if p.type == 0 else tick.ask
        request = {
            'action': mt5.TRADE_ACTION_DEAL, 'symbol': p.symbol,
            'volume': p.volume, 'type': close_type, 'position': ticket,
            'price': close_price, 'comment': 'MMDE close',
            'type_filling': mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        return {'status': 'closed' if result.retcode == mt5.TRADE_RETCODE_DONE else 'failed', 'retcode': result.retcode}


# Django view endpoint for MT5 status
def get_mt5_status_view(request):
    from django.http import JsonResponse
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Admin only'}, status=403)
    if not MT5_AVAILABLE:
        return JsonResponse({
            'available': False,
            'message': 'MetaTrader5 Python package not installed.',
            'install': 'pip install MetaTrader5',
            'note': 'Requires MT5 on Windows or Wine. Mobile (Termux) cannot run MT5 natively.',
        })
    return JsonResponse({'available': True, 'message': 'MT5 package available. Call connect() to link to terminal.'})
