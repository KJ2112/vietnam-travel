#!/usr/bin/env python3
"""
Neo4j Loader Script
Loads Vietnam travel dataset into Neo4j graph database
"""

import json
from typing import List, Dict
from neo4j import GraphDatabase
import config

class Neo4jLoader:
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            print(f"✅ Connected to Neo4j at {uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("🔌 Neo4j connection closed")
    
    def clear_database(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("🧹 Database cleared")
    
    def create_node(self, tx, node_data: Dict):
        """Create a travel node in Neo4j"""
        node_type = node_data.get('type', 'Unknown')
        
        # Create node with properties
        query = f"""
        CREATE (n:{node_type} {{
            id: $id,
            name: $name,
            type: $type,
            description: $description,
            location: $location
        }})
        RETURN n
        """
        
        params = {
            'id': node_data.get('id', f"node_{hash(node_data.get('name'))}"),
            'name': node_data.get('name', 'Unknown'),
            'type': node_type,
            'description': node_data.get('description', ''),
            'location': node_data.get('location', 'Vietnam')
        }
        
        # Add optional properties
        if 'activities' in node_data:
            activities = node_data['activities']
            if isinstance(activities, list):
                params['activities'] = ', '.join(activities)
            else:
                params['activities'] = activities
        
        if 'best_time' in node_data:
            params['best_time'] = node_data['best_time']
        
        tx.run(query, **params)
    
    def create_relationship(self, tx, source_id: str, rel: Dict):
        """Create a single relationship"""
        rel_type = rel.get("relation", "RELATED_TO")
        target_id = rel.get("target")
        if not target_id:
            print(f"❌ No target_id for relationship from {source_id}")
            return False
        
        # Debug: Check if both nodes exist
        check_query = """
        MATCH (a {id: $source_id})
        MATCH (b {id: $target_id})
        RETURN a.id AS source, b.id AS target
        """
        result = tx.run(check_query, source_id=source_id, target_id=target_id)
        record = result.single()
        
        if not record:
            print(f"❌ Cannot create relationship: {source_id} -> {target_id}")
            print(f"   One or both nodes don't exist")
            return False
        
        # Create relationship if both nodes exist
        cypher = (
            "MATCH (a {id: $source_id}), (b {id: $target_id}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "RETURN r"
        )
        result = tx.run(cypher, source_id=source_id, target_id=target_id)
        
        if result.single():
            print(f"✅ Created relationship: {source_id} -[{rel_type}]-> {target_id}")
            return True
        else:
            print(f"❌ Failed to create relationship: {source_id} -> {target_id}")
            return False
    
    def create_all_relationships(self, dataset: List[Dict]):
        """Create all relationships from the dataset"""
        relationship_count = 0
        
        with self.driver.session() as session:
            for node in dataset:
                source_id = node.get('id')
                connections = node.get('connections', [])
                
                for rel in connections:
                    success = session.execute_write(self.create_relationship, source_id, rel)
                    if success:
                        relationship_count += 1
        
        return relationship_count
    
    def load_dataset(self, filepath: str = "vietnam_travel_dataset.json"):
        """Load dataset and create graph"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            print(f"✅ Loaded {len(dataset)} records from {filepath}")
        except FileNotFoundError:
            print(f"❌ Error: {filepath} not found!")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return
        
        # Clear existing data
        self.clear_database()
        
        # Create nodes
        print(f"\n🔄 Creating {len(dataset)} nodes...")
        with self.driver.session() as session:
            for i, item in enumerate(dataset):
                # Don't overwrite the id - use the original one from JSON
                # item['id'] = f"node_{i}"  # REMOVE THIS LINE
                session.execute_write(self.create_node, item)
                if (i + 1) % 10 == 0:
                    print(f"   Created {i + 1}/{len(dataset)} nodes")
        
        print(f"✅ All nodes created")
        
        # Create relationships
        print("\n🔄 Creating relationships...")
        relationship_count = self.create_all_relationships(dataset)
        print(f"✅ Created {relationship_count} relationships")
        
        # Get statistics
        self.print_statistics()
    
    def print_statistics(self):
        """Print database statistics"""
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()['count']
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()['count']
            
            # Count by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            print(f"\n📊 Neo4j Database Statistics:")
            print(f"   Total Nodes: {node_count}")
            print(f"   Total Relationships: {rel_count}")
            print(f"\n   Node Types:")
            for record in result:
                print(f"      {record['type']}: {record['count']}")

def main():
    """Main execution function"""
    print("🚀 Starting Neo4j Load Process\n")
    
    try:
        loader = Neo4jLoader(
            uri=config.NEO4J_URI,
            username=config.NEO4J_USERNAME,
            password=config.NEO4J_PASSWORD
        )
        
        loader.load_dataset()
        
        print("\n✅ Neo4j load complete! Use visualize_graph.py to view the graph.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'loader' in locals():
            loader.close()

if __name__ == "__main__":
    main()