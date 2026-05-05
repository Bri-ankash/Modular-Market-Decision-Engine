def walk_forward(candles, window=50):
    results = []

    for i in range(window, len(candles)):
        train = candles[i-window:i]
        test = candles[i]

        train_return = train[-1]["close"] - train[0]["close"]
        test_return = test["close"] - train[-1]["close"]

        results.append({
            "train": train_return,
            "test": test_return
        })

    return results
