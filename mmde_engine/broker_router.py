import os

def get_broker():
    mode = os.getenv("MMDE_BROKER", "SIM")

    if mode == "OANDA":
        from mmde_engine.oanda_broker import OandaBroker

        return OandaBroker(
            token=os.getenv("OANDA_TOKEN"),
            account_id=os.getenv("OANDA_ACCOUNT")
        )

    return None
