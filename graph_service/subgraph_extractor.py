from neo4j_client import Neo4jClient

def extract_subgraph(account_id):
    client = Neo4jClient()

    with client.driver.session() as session:
        result = session.run('''
            MATCH (a:Account {id: $id})-[r1]-(n1)-[r2]-(n2)
            RETURN
                a.id as center,
                type(r1) as rel1,
                n1.id as node1,
                labels(n1)[0] as type1,
                type(r2) as rel2,
                n2.id as node2,
                labels(n2)[0] as type2
            LIMIT 50
        ''', id=account_id)

        rows = [dict(r) for r in result]

    client.close()
    return rows

if __name__ == "__main__":
    test_account = "ACC0011723"
    subgraph = extract_subgraph(test_account)
    print(f"Subgraph for {test_account}:")
    for row in subgraph[:5]:
        print(f"  {row['center']} -[{row['rel1']}]-> {row['node1']} -[{row['rel2']}]-> {row['node2']}")
    print(f"Total nodes in subgraph: {len(subgraph)}")