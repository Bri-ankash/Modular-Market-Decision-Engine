def walk_forward_split(data, train_size=100, test_size=50):
    i = 0
    while i + train_size + test_size < len(data):
        train = data[i:i+train_size]
        test = data[i+train_size:i+train_size+test_size]
        yield train, test
        i += test_size


def evaluate_strategy(strategy, data):
    wins = 0
    total = 0

    for train, test in walk_forward_split(data):

        for i in range(len(test)-1):
            signal = strategy(train)

            if signal == "HOLD":
                continue

            entry = test[i]["close"]
            future = test[i+1]["close"]

            if (signal == "BUY" and future > entry) or \
               (signal == "SELL" and future < entry):
                wins += 1
            total += 1

    return (wins / total) if total > 0 else 0
