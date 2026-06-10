import redis
import time

r = redis.Redis.from_url('redis://localhost:6379', decode_responses=True)

async def compute_velocity_features(tx):
    acct = tx['account_id']
    now = int(time.time() * 1000)  # milliseconds

    # Add current transaction to sorted set (score = timestamp)
    key = f"vel:{acct}"
    r.zadd(key, {tx['transaction_id']: now})
    r.expire(key, 86400)  # Keep 24 hours, then auto-delete

    # Count transactions in each time window
    def count_window(ms):
        return r.zcount(key, now - ms, now)

    # Amount velocity — sum of amounts in last 1 hour
    amt_key = f"amt:{acct}"
    r.zadd(amt_key, {f"{tx['transaction_id']}:{tx['amount']}": now})
    r.expire(amt_key, 86400)

    return {
        'tx_count_1m':  count_window(60_000),
        'tx_count_5m':  count_window(300_000),
        'tx_count_1h':  count_window(3_600_000),
        'tx_count_24h': count_window(86_400_000),
    }