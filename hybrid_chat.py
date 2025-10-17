#!/usr/bin/env python3
"""
Hybrid AI Travel Assistant - Using Ollama for embeddings + Gemini for chat
Combines Vector Search (Pinecone) + Knowledge Graph (Neo4j) + AI (Gemini)
"""

import json
import requests
import google.generativeai as genai
from typing import List, Dict, Tuple
from pinecone import Pinecone
from neo4j import GraphDatabase
import config
import time

class HybridTravelAssistant:
    def __init__(self):
        """Initialize all clients"""
        print("🚀 Initializing Hybrid Travel Assistant...\n")
        
        # Initialize Pinecone (v2+ format)
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
        print("✅ Pinecone connected")
        
        # Initialize Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        print("✅ Neo4j connected")
        
        # Initialize Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(config.GEMINI_CHAT_MODEL)
        print("✅ Gemini connected")
        
        # Cache for embeddings and results
        self.embedding_cache = {}
        self.query_cache = {}
        
        print("✅ Using Ollama for embeddings + Gemini for chat")
        print("\n✨ All systems ready!\n")
    
    def close(self):
        """Close connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
    
    def create_embedding(self, text: str) -> List[float]:
        """Generate embedding with caching using Ollama"""
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": config.OLLAMA_EMBEDDING_MODEL,
                    "prompt": text
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", [])
                
                if embedding:
                    # Cache the result
                    self.embedding_cache[text] = embedding
                    return embedding
                else:
                    print(f"❌ No embedding in response: {result}")
                    return []
            else:
                print(f"❌ Error from Ollama API: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return []
    
    def vector_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search Pinecone for similar vectors"""
        print(f"🔍 Searching vector database for: '{query}'")
        
        # Create query embedding
        query_embedding = self.create_embedding(query)
        if not query_embedding:
            return []
        
        try:
            # Query Pinecone (v2+ format)
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            matches = []
            for match in results.matches:
                matches.append({
                    'id': match.id,
                    'score': match.score,
                    'metadata': match.metadata
                })
            
            print(f"   Found {len(matches)} similar results")
            return matches
        except Exception as e:
            print(f"❌ Error querying Pinecone: {e}")
            return []
    
    def graph_search(self, locations: List[str], node_types: List[str] = None) -> List[Dict]:
        """Search Neo4j for related nodes and their connections"""
        print(f"🕸️  Querying knowledge graph...")
        
        with self.neo4j_driver.session() as session:
            # Use properties that actually exist in the database
            query = """
            MATCH (n)
            WHERE n.location IN $locations OR ANY(loc IN $locations WHERE n.name CONTAINS loc)
            OPTIONAL MATCH (n)-[r]-(connected)
            RETURN n.name as name, 
                   labels(n)[0] as type,
                   n.location as location,
                   n.description as description,
                   collect({rel: type(r), node: connected.name, type: labels(connected)[0]}) as connections
            LIMIT 20
            """
            
            result = session.run(query, locations=locations)
            
            graph_results = []
            for record in result:
                node_data = {
                    'name': record['name'],
                    'type': record['type'],
                    'location': record['location'],
                    'description': record['description'],
                    'connections': [c for c in record['connections'] if c['node']]
                }
                graph_results.append(node_data)
            
            print(f"   Found {len(graph_results)} graph nodes")
            return graph_results
    
    def extract_locations(self, query: str, vector_results: List[Dict]) -> List[str]:
        """Extract location information from query and results"""
        locations = set()
        
        # Common Vietnam locations
        vietnam_locations = [
            'Hanoi', 'Ho Chi Minh', 'Saigon', 'Hoi An', 'Da Nang', 
            'Hue', 'Nha Trang', 'Phu Quoc', 'Halong Bay', 'Sapa',
            'Dalat', 'Mekong Delta', 'Can Tho', 'Mui Ne', 'Vung Tau'
        ]
        
        # Check query for location mentions
        for loc in vietnam_locations:
            if loc.lower() in query.lower():
                locations.add(loc)
        
        # Extract locations from vector results
        for result in vector_results:
            if 'metadata' in result:
                meta = result['metadata']
                if 'city' in meta:
                    locations.add(meta['city'])
                elif 'region' in meta:
                    locations.add(meta['region'])
        
        # Default to Vietnam if no specific location found
        if not locations:
            locations.add('Vietnam')
        
        return list(locations)
    
    def build_context(self, query: str) -> Tuple[str, Dict]:
        """Build combined context from vector + graph search"""
        print("\n" + "="*80)
        print("🔄 Building hybrid context...")
        print("="*80)
        
        # Step 1: Vector search
        vector_results = self.vector_search(query, top_k=config.TOP_K_RESULTS)
        
        # Step 2: Extract locations and search graph
        locations = self.extract_locations(query, vector_results)
        graph_results = self.graph_search(locations)
        
        # Step 3: Build rich context
        context_parts = []
        
        # Add vector search results
        context_parts.append("=== SEMANTIC SEARCH RESULTS ===\n")
        for i, result in enumerate(vector_results, 1):
            meta = result['metadata']
            context_parts.append(f"{i}. {meta.get('name', 'Unknown')} (Relevance: {result['score']:.3f})")
            context_parts.append(f"   Type: {meta.get('type', 'N/A')}")
            if 'city' in meta:
                context_parts.append(f"   City: {meta['city']}")
            if 'region' in meta:
                context_parts.append(f"   Region: {meta['region']}")
            context_parts.append(f"   Description: {meta.get('description', 'N/A')}")
            if 'tags' in meta:
                context_parts.append(f"   Tags: {meta['tags']}")
            context_parts.append("")
        
        # Add graph search results
        context_parts.append("\n=== KNOWLEDGE GRAPH CONTEXT ===\n")
        for i, node in enumerate(graph_results, 1):
            context_parts.append(f"{i}. {node['name']} ({node['type']})")
            context_parts.append(f"   Location: {node['location']}")
            context_parts.append(f"   Description: {node['description']}")
            
            # Add connections
            if node['connections']:
                conn_summary = []
                for conn in node['connections'][:5]:  # Limit connections
                    if conn['node']:
                        conn_summary.append(f"{conn['node']} ({conn['type']})")
                if conn_summary:
                    context_parts.append(f"   Connected to: {', '.join(conn_summary)}")
            context_parts.append("")
        
        context = "\n".join(context_parts)
        
        # Metadata for analysis
        metadata = {
            'vector_results_count': len(vector_results),
            'graph_results_count': len(graph_results),
            'locations': locations,
            'top_result_score': vector_results[0]['score'] if vector_results else 0
        }
        
        return context, metadata
    
    def generate_answer(self, query: str, context: str, metadata: Dict) -> str:
        """Generate answer using Gemini"""
        
        # Build the prompt
        system_prompt = """You are an expert Vietnam travel assistant with deep knowledge of Vietnamese culture, destinations, and travel planning.

Your task is to provide comprehensive, accurate, and personalized travel recommendations based on:
1. Semantic search results from a vector database (most relevant destinations)
2. Knowledge graph connections (related places, activities, accommodations)

Guidelines:
- Use BOTH the semantic search results AND the knowledge graph context
- Create detailed, day-by-day itineraries when requested
- Include practical details: activities, accommodations, restaurants, transportation
- Consider connections between places (nearby attractions, related activities)
- Mention best times to visit when available
- Be specific and actionable
- Use a warm, enthusiastic tone
- If creating multi-day itineraries, ensure logical flow and realistic pacing"""

        user_prompt = f"""User Query: {query}

Available Context:
{context}

Based on the above context, please provide a comprehensive answer to the user's query. 
Use specific information from both the semantic search results and the knowledge graph connections."""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            response = self.gemini_model.generate_content(full_prompt)
            
            if response and response.text:
                answer = response.text
                
                # Add metadata footer
                footer = f"\n\n---\n💡 Answer generated using {metadata['vector_results_count']} semantic matches and {metadata['graph_results_count']} graph connections."
                
                return answer + footer
            else:
                print(f"❌ No response from Gemini: {response}")
                return "I apologize, but I encountered an error generating the response. Please try again."
        
        except Exception as e:
            print(f"❌ Error generating answer with Gemini: {e}")
            return "I apologize, but I encountered an error generating the response. Please try again."
    
    def chat(self, query: str) -> str:
        """Main chat function - combines everything"""
        start_time = time.time()
        
        # Check cache
        if query in self.query_cache:
            print("⚡ Returning cached result")
            return self.query_cache[query]
        
        # Build context from hybrid search
        context, metadata = self.build_context(query)
        
        # Generate answer
        print("\n🤖 Generating AI response...")
        answer = self.generate_answer(query, context, metadata)
        
        # Cache the result
        self.query_cache[query] = answer
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total time: {elapsed:.2f}s")
        
        return answer

def interactive_cli():
    """Interactive command-line interface"""
    print("="*80)
    print("🌏  HYBRID AI TRAVEL ASSISTANT FOR VIETNAM")
    print("="*80)
    print("\nCombining Vector Search (Pinecone) + Knowledge Graph (Neo4j) + AI (Gemini)")
    print("\nCommands:")
    print("  - Type your travel question")
    print("  - 'examples' - Show example queries")
    print("  - 'stats' - Show system statistics") 
    print("  - 'clear' - Clear cache")
    print("  - 'quit' or 'exit' - Exit the program")
    print("\n" + "="*80 + "\n")
    
    try:
        assistant = HybridTravelAssistant()
        
        while True:
            try:
                query = input("🗣️  Enter your travel question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Hybrid AI Travel Assistant!")
                    break
                
                if query.lower() == 'examples':
                    print("\n📝 Example Queries:")
                    print("  1. Create a romantic 4 day itinerary for Vietnam")
                    print("  2. What are the best activities in Hanoi?")
                    print("  3. Recommend luxury hotels in Ho Chi Minh City")
                    print("  4. Plan a beach vacation in Nha Trang")
                    print("  5. What's the best time to visit Halong Bay?")
                    print("  6. Find adventure activities in Sapa")
                    print("  7. Suggest a food tour in Hoi An\n")
                    continue
                
                if query.lower() == 'stats':
                    print(f"\n📊 System Statistics:")
                    print(f"  Cached embeddings: {len(assistant.embedding_cache)}")
                    print(f"  Cached queries: {len(assistant.query_cache)}")
                    print(f"  Pinecone index: {config.PINECONE_INDEX_NAME}")
                    print(f"  Neo4j URI: {config.NEO4J_URI}")
                    print(f"  Gemini model: {config.GEMINI_CHAT_MODEL}\n")
                    continue
                
                if query.lower() == 'clear':
                    assistant.embedding_cache.clear()
                    assistant.query_cache.clear()
                    print("✅ Cache cleared\n")
                    continue
                
                # Process the query
                print("")
                answer = assistant.chat(query)
                
                print("\n" + "="*80)
                print("💬 RESPONSE:")
                print("="*80)
                print(answer)
                print("\n" + "="*80 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error processing query: {e}\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
    finally:
        if 'assistant' in locals():
            assistant.close()

def main():
    """Main entry point"""
    # Validate configuration
    if not config.validate_config():
        print("\n❌ Please check your configuration before running!")
        return
    
    # Start interactive CLI
    interactive_cli()

if __name__ == "__main__":
    main()