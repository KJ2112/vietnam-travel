#!/usr/bin/env python3
"""
Pinecone Upload Script – with Ollama for embeddings
Uploads Vietnam travel dataset embeddings to Pinecone
"""

import json
import time
import requests
from typing import List, Dict
from pinecone import Pinecone, ServerlessSpec
import config

# Initialize Pinecone
pc = Pinecone(api_key=config.PINECONE_API_KEY)

def load_dataset(filepath: str = "vietnam_travel_dataset.json") -> List[Dict]:
    """Load the travel dataset from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} records from {filepath}")
        return data
    except FileNotFoundError:
        print(f"❌ Error: {filepath} not found!")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return []

def create_embedding(text: str) -> List[float]:
    """Generate embedding using Ollama"""
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

def create_pinecone_index():
    """Create Pinecone index if it doesn't exist (v2+ format)"""
    index_name = config.PINECONE_INDEX_NAME
    existing = [idx.name for idx in pc.list_indexes()]
    if index_name in existing:
        print(f"✅ Index '{index_name}' already exists")
        return pc.Index(index_name)
    
    print(f"Creating new index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=config.EMBEDDING_DIMENSION,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
    # Wait
    while not pc.describe_index(index_name).status['ready']:
        print("⏳ Waiting for index to be ready...")
        time.sleep(1)
    print(f"✅ Index '{index_name}' created successfully")
    return pc.Index(index_name)

def prepare_vectors(dataset: List[Dict]) -> List[tuple]:
    """Prepare vectors for upsert with embeddings"""
    vectors = []
    successful = 0
    failed = 0
    
    for i, item in enumerate(dataset):
        # Build text to embed
        parts = []
        if 'name' in item:
            parts.append(f"Name: {item['name']}")
        if 'type' in item:
            parts.append(f"Type: {item['type']}")
        if 'description' in item:
            parts.append(f"Description: {item['description']}")
        if 'location' in item:
            parts.append(f"Location: {item['location']}")
        if 'activities' in item:
            acts = (', '.join(item['activities'])
                    if isinstance(item['activities'], list)
                    else item['activities'])
            parts.append(f"Activities: {acts}")
        text_to_embed = ' | '.join(parts)
        
        print(f"Processing {i+1}/{len(dataset)}: {item.get('name', 'Unknown')}")
        
        embedding = create_embedding(text_to_embed)
        if not embedding:
            print(f"⚠️ Skipping item {i+1} due to embedding error")
            failed += 1
            continue
        
        metadata = {
            'name': item.get('name', 'Unknown'),
            'type': item.get('type', 'Unknown'),
            'description': item.get('description', '')[:500],
            'location': item.get('location', 'Unknown'),
            'text': text_to_embed[:1000]
        }
        if 'activities' in item:
            acts = (item['activities']
                    if isinstance(item['activities'], list)
                    else [item['activities']])
            metadata['activities'] = ', '.join(acts[:5])
        if 'best_time' in item:
            metadata['best_time'] = item['best_time']
        
        vid = f"node_{i}"
        vectors.append((vid, embedding, metadata))
        successful += 1
        
        # Small delay to avoid overwhelming Ollama
        time.sleep(0.1)
    
    print(f"✅ Successfully embedded {successful} items, failed: {failed}")
    return vectors

def upload_to_pinecone(index, vectors: List[tuple], batch_size: int = 100):
    """Upload vectors to Pinecone in batches"""
    total = len(vectors)
    print(f"\n📤 Starting upload of {total} vectors in batches of {batch_size}")
    
    for i in range(0, total, batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"✅ Uploaded batch {i//batch_size + 1}: items {i+1} to {min(i+batch_size, total)}")
        except Exception as e:
            print(f"❌ Error uploading batch {i//batch_size + 1}: {e}")
    
    time.sleep(2)
    stats = index.describe_index_stats()
    print(f"\n📊 Index Statistics:")
    print(f"   Total vectors: {stats.total_vector_count}")
    print(f"   Dimension: {stats.dimension}")

def main():
    """Main execution"""
    print("🚀 Starting Pinecone Upload via Ollama embeddings\n")
    
    if not config.validate_config():
        return
    
    data = load_dataset()
    if not data:
        return
    
    idx = create_pinecone_index()
    print("\n🔄 Generating embeddings with Ollama...")
    
    vecs = prepare_vectors(data)
    if not vecs:
        print("❌ No vectors to upload")
        return
    
    upload_to_pinecone(idx, vecs, batch_size=config.BATCH_SIZE)
    print("\n✅ Done. Verify in Pinecone dashboard.")

if __name__ == "__main__":
    main()