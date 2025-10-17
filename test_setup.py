#!/usr/bin/env python3
"""
Test Setup Script - Verify all components are working
Run this before submission to ensure everything is configured correctly
"""

import sys
import json
from typing import Tuple

def test_imports() -> Tuple[bool, str]:
    """Test if all required packages are installed"""
    print("📦 Testing package imports...")
    try:
        import pinecone
        from openai import OpenAI
        from neo4j import GraphDatabase
        import config
        print("   ✅ All packages imported successfully")
        return True, "All required packages installed"
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False, f"Missing package: {e}"

def test_config() -> Tuple[bool, str]:
    """Test if configuration is valid"""
    print("\n🔑 Testing configuration...")
    try:
        import config
        
        # Check if API keys are set
        if config.PINECONE_API_KEY.startswith("your-"):
            print("   ⚠️  Pinecone API key not configured")
            return False, "Pinecone API key not set"
        
        if config.OPENAI_API_KEY.startswith("your-"):
            print("   ⚠️  OpenAI API key not configured")
            return False, "OpenAI API key not set"
        
        if config.NEO4J_PASSWORD.startswith("your-"):
            print("   ⚠️  Neo4j password not configured")
            return False, "Neo4j password not set"
        
        print("   ✅ Configuration appears valid")
        return True, "Configuration valid"
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False, str(e)

def test_dataset() -> Tuple[bool, str]:
    """Test if dataset file exists and is valid"""
    print("\n📊 Testing dataset...")
    try:
        with open('vietnam_travel_dataset.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("   ❌ Dataset is not a list")
            return False, "Invalid dataset format"
        
        if len(data) == 0:
            print("   ❌ Dataset is empty")
            return False, "Empty dataset"
        
        # Check first item structure
        required_fields = ['name', 'type', 'description', 'location']
        first_item = data[0]
        
        for field in required_fields:
            if field not in first_item:
                print(f"   ⚠️  Missing field '{field}' in dataset")
                return False, f"Missing field: {field}"
        
        print(f"   ✅ Dataset loaded: {len(data)} items")
        return True, f"Dataset valid with {len(data)} items"
    except FileNotFoundError:
        print("   ❌ Dataset file not found")
        return False, "vietnam_travel_dataset.json not found"
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON: {e}")
        return False, "Invalid JSON format"

def test_pinecone_connection() -> Tuple[bool, str]:
    """Test Pinecone connection"""
    print("\n🌲 Testing Pinecone connection...")
    try:
        from pinecone import Pinecone
        import config
        
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        indexes = pc.list_indexes()
        
        print(f"   ✅ Connected to Pinecone")
        print(f"   📋 Available indexes: {[idx.name for idx in indexes]}")
        
        # Check if our index exists
        index_names = [idx.name for idx in indexes]
        if config.PINECONE_INDEX_NAME in index_names:
            print(f"   ✅ Index '{config.PINECONE_INDEX_NAME}' found")
            index = pc.Index(config.PINECONE_INDEX_NAME)
            stats = index.describe_index_stats()
            print(f"   📊 Vector count: {stats.total_vector_count}")
            return True, f"Pinecone connected, {stats.total_vector_count} vectors"
        else:
            print(f"   ⚠️  Index '{config.PINECONE_INDEX_NAME}' not found")
            print(f"   💡 Run: python pinecone_upload.py")
            return False, "Index not created yet"
            
    except Exception as e:
        print(f"   ❌ Pinecone error: {e}")
        return False, str(e)

def test_neo4j_connection() -> Tuple[bool, str]:
    """Test Neo4j connection"""
    print("\n🕸️  Testing Neo4j connection...")
    try:
        from neo4j import GraphDatabase
        import config
        
        driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1")
            result.single()
        
        print("   ✅ Connected to Neo4j")
        
        # Check if data is loaded
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()['count']
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()['count']
        
        print(f"   📊 Nodes: {node_count}, Relationships: {rel_count}")
        
        driver.close()
        
        if node_count == 0:
            print("   ⚠️  No data in Neo4j")
            print("   💡 Run: python load_to_neo4j.py")
            return False, "No data loaded yet"
        
        return True, f"Neo4j connected with {node_count} nodes"
        
    except Exception as e:
        print(f"   ❌ Neo4j error: {e}")
        return False, str(e)

def test_openai_connection() -> Tuple[bool, str]:
    """Test OpenAI connection"""
    print("\n🤖 Testing OpenAI connection...")
    try:
        from openai import OpenAI
        import config
        
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Test with a simple embedding
        response = client.embeddings.create(
            model=config.OPENAI_EMBEDDING_MODEL,
            input="test"
        )
        
        embedding = response.data[0].embedding
        print(f"   ✅ OpenAI connected")
        print(f"   📏 Embedding dimension: {len(embedding)}")
        
        return True, "OpenAI connected successfully"
        
    except Exception as e:
        print(f"   ❌ OpenAI error: {e}")
        return False, str(e)

def test_hybrid_system() -> Tuple[bool, str]:
    """Test the complete hybrid system"""
    print("\n🔄 Testing hybrid system...")
    try:
        from hybrid_chat import HybridTravelAssistant
        
        assistant = HybridTravelAssistant()
        print("   ✅ Hybrid assistant initialized")
        
        # Test a simple query
        print("   🧪 Testing query: 'Hanoi attractions'")
        answer = assistant.chat("Hanoi attractions")
        
        if answer and len(answer) > 100:
            print("   ✅ Query successful")
            print(f"   📝 Response length: {len(answer)} characters")
            assistant.close()
            return True, "Hybrid system working"
        else:
            print("   ⚠️  Response too short or empty")
            assistant.close()
            return False, "Response generation issue"
            
    except Exception as e:
        print(f"   ❌ Hybrid system error: {e}")
        return False, str(e)

def print_summary(results: dict):
    """Print summary of all tests"""
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r[0])
    
    for test_name, (success, message) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for submission.")
        print("\nNext steps:")
        print("1. Take screenshots for submission")
        print("2. Fill out improvements.md")
        print("3. Review SUBMISSION_GUIDE.md")
        print("4. Submit your work!")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before submitting.")
        print("\nCheck:")
        print("- API keys are correctly configured")
        print("- Services (Neo4j) are running")
        print("- Data has been uploaded (run upload scripts)")
    
    print("="*80)

def main():
    """Run all tests"""
    print("="*80)
    print("🧪 AI-HYBRID CHAT SYSTEM TEST")
    print("="*80)
    print("\nThis script will verify that all components are working correctly.\n")
    
    results = {}
    
    # Run tests in order
    results["Package Imports"] = test_imports()
    results["Configuration"] = test_config()
    results["Dataset"] = test_dataset()
    
    # Only test connections if config is valid
    if results["Configuration"][0]:
        results["Pinecone Connection"] = test_pinecone_connection()
        results["Neo4j Connection"] = test_neo4j_connection()
        results["OpenAI Connection"] = test_openai_connection()
        
        # Only test hybrid system if all connections work
        if all([results["Pinecone Connection"][0], 
                results["Neo4j Connection"][0], 
                results["OpenAI Connection"][0]]):
            results["Hybrid System"] = test_hybrid_system()
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    all_passed = all(r[0] for r in results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()