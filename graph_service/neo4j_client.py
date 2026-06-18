import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password123")
            )
        )
        print("Neo4j connected successfully.")

    def close(self):
        self.driver.close()

    def create_indexes(self):
        with self.driver.session() as session:
            session.run("CREATE INDEX account_id_idx IF NOT EXISTS FOR (a:Account) ON (a.id)")
            session.run("CREATE INDEX device_id_idx IF NOT EXISTS FOR (d:Device) ON (d.id)")
            session.run("CREATE INDEX merchant_id_idx IF NOT EXISTS FOR (m:Merchant) ON (m.id)")
            session.run("CREATE INDEX ip_idx IF NOT EXISTS FOR (i:IP) ON (i.address)")
            print("Indexes created successfully.")

    def update_graph(self, tx):
        with self.driver.session() as session:
            session.execute_write(self._upsert_transaction, tx)

    @staticmethod
    def _upsert_transaction(tx_session, tx):
        tx_session.run('''
            MERGE (a:Account {id: $account_id})
            MERGE (d:Device {id: $device_id})
            MERGE (m:Merchant {id: $merchant_id})
            MERGE (i:IP {address: $ip_address})
            MERGE (a)-[:USED_DEVICE]->(d)
            MERGE (a)-[:MADE_PURCHASE_AT]->(m)
            MERGE (a)-[:CONNECTED_FROM]->(i)
        ''',
            account_id=tx["account_id"],
            device_id=tx["device_id"],
            merchant_id=tx["merchant_id"],
            ip_address=tx["ip_address"]
        )

    def get_subgraph_features(self, account_id):
        with self.driver.session() as session:
            result = session.run('''
                MATCH (a:Account {id: $id})-[*1..2]-(n)
                RETURN n.id as node_id, labels(n)[0] as type
            ''', id=account_id)
            return [dict(r) for r in result]

    def get_fraud_neighbor_count(self, account_id):
        with self.driver.session() as session:
            result = session.run('''
                MATCH (a:Account {id: $id})-[:USED_DEVICE]->(d:Device)
                      <-[:USED_DEVICE]-(b:Account)
                WHERE b.is_fraud = true AND b.id <> $id
                RETURN count(b) as fraud_neighbors
            ''', id=account_id)
            record = result.single()
            return record["fraud_neighbors"] if record else 0

if __name__ == "__main__":
    client = Neo4jClient()
    client.create_indexes()
    client.close()