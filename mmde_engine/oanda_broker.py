import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts

class OandaBroker:
    def __init__(self, token, account_id, env="practice"):
        self.client = oandapyV20.API(access_token=token, environment=env)
        self.account_id = account_id

    def get_balance(self):
        r = accounts.AccountSummary(self.account_id)
        self.client.request(r)
        return r.response

    def place_market_order(self, instrument, units):
        data = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(int(units)),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT"
            }
        }

        r = orders.OrderCreate(self.account_id, data=data)
        self.client.request(r)
        return r.response
