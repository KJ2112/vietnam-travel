from neo4j import GraphDatabase
import config

driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))

def check_database():
    with driver.session() as session:
        # Check nodes
        node_result = session.run("MATCH (n) RETURN count(n) as node_count")
        node_count = node_result.single()["node_count"]
        print(f"Total nodes: {node_count}")
        
        # Check relationships
        rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
        rel_count = rel_result.single()["rel_count"]
        print(f"Total relationships: {rel_count}")
        
        # Check node types
        types_result = session.run("""
        MATCH (n) 
        RETURN labels(n)[0] as type, count(*) as count
        """)
        print("Node types:")
        for record in types_result:
            print(f"  {record['type']}: {record['count']}")
        
        # Check a few sample relationships
        sample_rels = session.run("""
        MATCH (a)-[r]->(b) 
        RETURN a.id as source, type(r) as relationship, b.id as target 
        LIMIT 10
        """)
        print("Sample relationships:")
        for record in sample_rels:
            print(f"  {record['source']} -[{record['relationship']}]-> {record['target']}")

if __name__ == "__main__":
    check_database()