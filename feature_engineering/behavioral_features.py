from datetime import datetime

# Merchants considered high-risk
HIGH_RISK_MERCHANTS = {'ATM', 'TRAVEL', 'ONLINE'}

# Countries considered high-risk
HIGH_RISK_COUNTRIES = {'NG', 'CN'}

async def compute_behavioral_features(tx):
    ts = datetime.fromisoformat(tx['timestamp'])
    hour = ts.hour

    # Is the transaction happening at an unusual hour? (midnight to 5am)
    is_odd_hour = 1 if hour < 5 or hour >= 23 else 0

    # Is the merchant category high risk?
    is_high_risk_merchant = 1 if tx['merchant_category'] in HIGH_RISK_MERCHANTS else 0

    # Is the country high risk?
    is_high_risk_country = 1 if tx['country'] in HIGH_RISK_COUNTRIES else 0

    # Is the amount suspiciously round? (e.g. exactly 1000, 5000)
    amount = float(tx['amount'])
    is_round_amount = 1 if amount % 100 == 0 else 0

    return {
        'hour_of_day':            hour,
        'is_odd_hour':            is_odd_hour,
        'is_high_risk_merchant':  is_high_risk_merchant,
        'is_high_risk_country':   is_high_risk_country,
        'is_round_amount':        is_round_amount,
    }