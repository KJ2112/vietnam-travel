import requests
import time

def test_ollama():
    print("🧪 Testing Ollama setup...")
    
    # Test 1: Check if Ollama is accessible
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            models = response.json().get('models', [])
            if models:
                print("📦 Available models:")
                for model in models:
                    print(f"   - {model['name']}")
            else:
                print("ℹ️  No models found. You need to download models.")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False
    
    # Test 2: Check if embedding model is available
    try:
        print("\n🔍 Testing embedding model...")
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": "Test embedding"
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            print(f"✅ Embedding model working! Vector dimension: {len(embedding)}")
            return True
        else:
            print(f"❌ Embedding model test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Embedding test error: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    if success:
        print("\n🎉 All tests passed! You can now run pinecone_upload.py")
    else:
        print("\n💡 If embedding model is missing, run: ollama pull nomic-embed-text")