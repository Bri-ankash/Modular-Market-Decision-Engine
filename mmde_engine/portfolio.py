from mmde_engine.paper_broker import get_account

def portfolio_status():

    acc = get_account()

    return {
        "balance": acc["balance"],
        "open_trades": len([t for t in acc["trades"] if t["status"] == "OPEN"]),
        "total_trades": len(acc["trades"])
    }
