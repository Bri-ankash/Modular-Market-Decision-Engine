class ExecutionEngine:
    """
    Simple execution layer (SIM broker for now)
    """

    def __init__(self):
        self.trades = []

    def place_order(self, symbol, direction, size, price):

        trade = {
            "symbol": symbol,
            "direction": direction,
            "size": float(size),
            "price": price,
            "status": "FILLED_SIM"
        }

        self.trades.append(trade)

        print(f"[BROKER] {direction} {symbol} size={size} price={price}")

        return trade
