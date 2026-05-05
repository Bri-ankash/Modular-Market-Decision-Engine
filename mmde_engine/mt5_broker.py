import random

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except:
    MT5_AVAILABLE = False


class MT5Broker:
    def __init__(self):
        self.connected = False

    def connect(self):
        if not MT5_AVAILABLE:
            print("[MT5] Not installed → running SIMULATED broker")
            self.connected = False
            return False

        self.connected = mt5.initialize()
        print("[MT5] Connected:", self.connected)
        return self.connected

    def get_price(self, symbol):
        if not MT5_AVAILABLE:
            return self._mock_price(symbol)

        tick = mt5.symbol_info_tick(symbol)
        if tick:
            return tick.ask
        return self._mock_price(symbol)

    def place_order(self, symbol, direction, size):
        price = self.get_price(symbol)

        if not MT5_AVAILABLE:
            return self._simulate_order(symbol, direction, size, price)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(size),
            "type": mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": 20,
            "magic": 2026,
            "comment": "MMDE_ENGINE"
        }

        result = mt5.order_send(request)
        return result

    def _simulate_order(self, symbol, direction, size, price):
        pnl = random.uniform(-1, 1)
        return {
            "symbol": symbol,
            "direction": direction,
            "size": size,
            "price": price,
            "pnl": pnl,
            "status": "SIMULATED_FILL"
        }
