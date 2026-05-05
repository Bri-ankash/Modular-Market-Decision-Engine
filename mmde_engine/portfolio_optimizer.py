import numpy as np

SECTOR_MAP = {
    "EURUSD=X": "FX",
    "GBPJPY=X": "FX",
    "BTC-USD": "CRYPTO",
    "ETH-USD": "CRYPTO",
    "AAPL": "STOCK",
    "NVDA": "STOCK",
    "TSLA": "STOCK"
}

def compute_volatility(candles):
    closes = np.array([c["close"] for c in candles])
    returns = np.diff(closes)
    return np.std(returns) if len(returns) > 1 else 1

def portfolio_weights(symbols, data_map, base_risk=1.0):

    vols = {}
    for s in symbols:
        vols[s] = compute_volatility(data_map[s])

    inv_vol = {s: 1.0 / (v + 1e-6) for s, v in vols.items()}

    total = sum(inv_vol.values())

    weights = {s: inv_vol[s] / total for s in symbols}

    # sector caps
    sector_exposure = {}

    for s in symbols:
        sector = SECTOR_MAP.get(s, "OTHER")
        sector_exposure[sector] = sector_exposure.get(sector, 0) + weights[s]

    # cap adjustment
    for s in symbols:
        sector = SECTOR_MAP.get(s, "OTHER")
        if sector_exposure[sector] > 0.4:
            weights[s] *= 0.7

    return weights
