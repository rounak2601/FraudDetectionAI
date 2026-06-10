from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

TOPICS = [
    NewTopic(name="raw_transactions", num_partitions=10, replication_factor=1),
    NewTopic(name="enriched_transactions", num_partitions=10, replication_factor=1),
    NewTopic(name="fraud_decisions", num_partitions=10, replication_factor=1),
]

def create_topics():
    admin = KafkaAdminClient(bootstrap_servers="localhost:9092")
    for topic in TOPICS:
        try:
            admin.create_topics([topic])
            print(f"Created topic: {topic.name}")
        except TopicAlreadyExistsError:
            print(f"Topic already exists: {topic.name}")
    admin.close()
    print("All topics ready.")

if __name__ == "__main__":
    create_topics()