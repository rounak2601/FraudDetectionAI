from neo4j_client import Neo4jClient

def compute_graph_features(account_id):
    client = Neo4jClient()
    features = {}

    with client.driver.session() as session:

        # How many accounts share the same device
        r1 = session.run('''
            MATCH (a:Account {id: $id})-[:USED_DEVICE]->(d:Device)
                  <-[:USED_DEVICE]-(b:Account)
            WHERE b.id <> $id
            RETURN count(DISTINCT b) as shared_device_count
        ''', id=account_id)
        rec1 = r1.single()
        features['shared_device_count'] = rec1['shared_device_count'] if rec1 else 0

        # How many accounts share the same IP
        r2 = session.run('''
            MATCH (a:Account {id: $id})-[:CONNECTED_FROM]->(i:IP)
                  <-[:CONNECTED_FROM]-(b:Account)
            WHERE b.id <> $id
            RETURN count(DISTINCT b) as shared_ip_count
        ''', id=account_id)
        rec2 = r2.single()
        features['shared_ip_count'] = rec2['shared_ip_count'] if rec2 else 0

        # How many fraud neighbors
        r3 = session.run('''
            MATCH (a:Account {id: $id})-[:USED_DEVICE]->(d:Device)
                  <-[:USED_DEVICE]-(b:Account)
            WHERE b.is_fraud = true AND b.id <> $id
            RETURN count(DISTINCT b) as fraud_neighbor_count
        ''', id=account_id)
        rec3 = r3.single()
        features['fraud_neighbor_count'] = rec3['fraud_neighbor_count'] if rec3 else 0

    client.close()
    return features

if __name__ == "__main__":
    test_account = "ACC0011723"
    features = compute_graph_features(test_account)
    print(f"Graph features for {test_account}:")
    for k, v in features.items():
        print(f"  {k}: {v}")