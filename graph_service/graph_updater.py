import json
import time
from kafka import KafkaConsumer
from neo4j_client import Neo4jClient

def start_graph_updater():
    client = Neo4jClient()

    consumer = KafkaConsumer(
        'enriched_transactions',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='graph-updater-group',
        consumer_timeout_ms=10000
    )

    print("Graph updater started. Listening to enriched_transactions...")
    count = 0

    for message in consumer:
        tx = message.value
        try:
            client.update_graph(tx)
            count += 1
            if count % 10 == 0:
                print(f"  Graph updated: {count} transactions processed")
        except Exception as e:
            print(f"  Error updating graph: {e}")

    print(f"Done. Total transactions added to graph: {count}")
    consumer.close()
    client.close()

if __name__ == "__main__":
    start_graph_updater()