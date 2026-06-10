import asyncio
import json
import sys
import os

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from velocity_features import compute_velocity_features
from behavioral_features import compute_behavioral_features

KAFKA_BROKER = 'localhost:9092'

async def run():
    consumer = AIOKafkaConsumer(
        'raw_transactions',
        bootstrap_servers=KAFKA_BROKER,
        group_id='feature-eng-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda m: json.dumps(m).encode('utf-8'),
    )

    await consumer.start()
    await producer.start()
    print("Feature engineering worker started. Waiting for transactions...")

    try:
        async for msg in consumer:
            tx = msg.value
            try:
                velocity   = await compute_velocity_features(tx)
                behavioral = await compute_behavioral_features(tx)
                enriched = {**tx, **velocity, **behavioral}
                await producer.send('enriched_transactions', enriched)
                print(f"Enriched: {tx['transaction_id'][:8]}... | acc={tx['account_id']} | 1m_count={velocity['tx_count_1m']} | risk_merchant={behavioral['is_high_risk_merchant']}")
            except Exception as e:
                print(f"Error processing transaction: {e}")
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == '__main__':
    asyncio.run(run())
