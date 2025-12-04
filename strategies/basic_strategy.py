# strategies/basic_strategy.py

def simple_moving_average_decision(current_price, moving_average):
    """
    Simple SMA-based trading rule.
    Returns one of: 'BUY', 'SELL', 'HOLD'
    """

    # Safety checks
    if current_price is None or moving_average is None:
        return "HOLD"

    try:
        current_price = float(current_price)
        moving_average = float(moving_average)
    except ValueError:
        return "HOLD"

    # Strategy logic
    if current_price > moving_average:
        return "BUY"
    elif current_price < moving_average:
        return "SELL"
    else:
        return "HOLD"
