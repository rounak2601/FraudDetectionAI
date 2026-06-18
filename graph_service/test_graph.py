from neo4j_client import Neo4jClient

c = Neo4jClient()
with c.driver.session() as s:
    r = s.run("MATCH (n) RETURN labels(n)[0] as type, count(n) as count")
    for rec in r:
        print(f"{rec['type']}: {rec['count']} nodes")
c.close()