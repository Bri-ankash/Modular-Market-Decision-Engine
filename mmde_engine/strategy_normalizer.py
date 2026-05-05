def normalize_signal(result):
    """
    Forces ALL strategy outputs into a stable format:
    (signal, confidence)
    """

    if result is None:
        return "HOLD", 0.0

    # case 1: string only
    if isinstance(result, str):
        return result, 0.5

    # case 2: tuple/list
    if isinstance(result, (list, tuple)):
        if len(result) == 1:
            return result[0], 0.5
        if len(result) >= 2:
            return result[0], float(result[1])

    # case 3: dict
    if isinstance(result, dict):
        return result.get("signal", "HOLD"), float(result.get("confidence", 0.5))

    # fallback
    return "HOLD", 0.0
