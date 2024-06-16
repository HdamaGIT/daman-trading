def trading_calculator(capital, max_risk_pct, target_profit_pips, size, entry_price):
    # Calculate risk amount in money
    risk_amount_money = capital * max_risk_pct

    # Calculate risk amount in pips
    risk_amount_pips = risk_amount_money / size

    # Calculate stop loss level
    stop_loss_level = entry_price - risk_amount_pips

    # Calculate expected return
    expected_return = target_profit_pips * size

    # Calculate risk/reward ratio
    risk_reward_ratio = risk_amount_pips / target_profit_pips

    return stop_loss_level, risk_amount_money, risk_amount_pips, expected_return, risk_reward_ratio

# example usage
capital = 2000
max_risk_pct = 0.02
target_profit_pips = 100
size = 0.5
entry_price = 15051

stop_loss_level, risk_amount_money, risk_amount_pips, expected_return, risk_reward_ratio = trading_calculator(capital, max_risk_pct, target_profit_pips, size, entry_price)

print("Stop Loss Level: ", stop_loss_level)
print("Risk Amount in Money: ", risk_amount_money)
print("Risk Amount in Pips: ", risk_amount_pips)
print("Expected Return: ", expected_return)
print("Risk/Reward Ratio: ", risk_reward_ratio)
