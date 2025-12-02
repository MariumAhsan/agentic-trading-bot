# strategies/basic_strategy.py
def simple_moving_average_decision(current_price, moving_average):
    """
    Returns 'BUY', 'SELL', or 'HOLD'
    """
    if current_price is None or moving_average is None:
        return "HOLD"

    if current_price > moving_average:
        return "BUY"
    elif current_price < moving_average:
        return "SELL"
    return "HOLD"
