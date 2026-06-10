import json
import random
import time
import uuid
import numpy as np
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction():
    return {
        "transaction_id": str(uuid.uuid4()),
        "account_id": f"ACC{random.randint(1, 100000):07d}",
        "amount": round(float(np.random.lognormal(4, 1.5)), 2),
        "merchant_id": f"MER{random.randint(1, 5000):05d}",
        "merchant_category": random.choice(['GROCERY','FUEL','TRAVEL','ONLINE','ATM']),
        "device_id": f"DEV{random.randint(1, 200000):07d}",
        "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.0.1",
        "country": random.choice(['IN','US','UK','DE','FR','CN','NG']),
        "timestamp": datetime.utcnow().isoformat(),
        "is_fraud": 1 if random.random() < 0.02 else 0
    }

print("Sending 100 test transactions to Kafka...")
for i in range(100):
    tx = generate_transaction()
    producer.send('raw_transactions', tx)
    if (i+1) % 10 == 0:
        print(f"  Sent {i+1} transactions...")
    time.sleep(0.05)

producer.flush()
print("Done! 100 transactions sent to Kafka topic: raw_transactions")
