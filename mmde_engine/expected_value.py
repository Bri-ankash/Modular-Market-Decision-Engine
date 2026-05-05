def expected_value(alpha, confidence):

    # simple institutional approximation
    win_prob = max(0.5, min(0.65, 0.5 + confidence * 0.1))

    avg_win = alpha * 1.2
    avg_loss = -alpha * 0.8

    ev = (win_prob * avg_win) + ((1 - win_prob) * avg_loss)

    return ev
