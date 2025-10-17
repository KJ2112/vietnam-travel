# 🧠 Hybrid AI Travel Assistant - Complete Solution

A sophisticated AI-powered travel assistant combining vector search (Pinecone), knowledge graphs (Neo4j), and large language models using Ollama for embeddings and Gemini for chat to provide intelligent travel recommendations for Vietnam.

## 🎯 Overview

This system demonstrates advanced RAG (Retrieval-Augmented Generation) architecture by:
- **Vector Search**: Finding semantically similar travel destinations using embeddings
- **Graph Context**: Enriching results with relationship-based information
- **LLM Generation**: Producing coherent, context-aware travel recommendations

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────────────────────────┐
│   Hybrid Travel Assistant           │
├─────────────────────────────────────┤
│  1. Query Embedding                 │
│     ↓                                │
│  2. Vector Search (Pinecone)        │ ← Semantic Similarity
│     ↓                                │
│  3. Location Extraction             │
│     ↓                                │
│  4. Graph Search (Neo4j)            │ ← Relationship Context
│     ↓                                │
│  5. Context Fusion                  │
│     ↓                                │
│  6. LLM Generation (Gemini)         │ ← Intelligent Response
└─────────────────────────────────────┘
    ↓
Final Answer
```

## 📋 Prerequisites

### Required Accounts & API Keys
1. **Pinecone Account** - [Sign up](https://www.pinecone.io/)
2. **Google Gemini API Key** - [Get key](https://ai.google.dev/)
3. **Neo4j Database** - Options:
   - [Neo4j Desktop](https://neo4j.com/download/) (Local)
   - [Neo4j Aura](https://neo4j.com/cloud/aura/) (Cloud)
4. **Ollama** (Local embeddings server) - [Install](https://ollama.com/)

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- Internet connection for API calls

## 🚀 Installation & Setup

### Step 1: Clone/Download Files

Ensure you have these files:
```
project/
├── config.py
├── pinecone_upload.py
├── load_to_neo4j.py
├── visualize_graph.py
├── hybrid_chat.py
├── requirements.txt
├── vietnam_travel_dataset.json
├── improvements.md
└── README.md
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

Edit `config.py` and add your API keys:

```python
# config.py
PINECONE_API_KEY = "your-pinecone-api-key-here"
GEMINI_API_KEY = "your-gemini-api-key-here"
NEO4J_URI = "bolt://localhost:7687"  # or your Neo4j Aura URI
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-neo4j-password"

# Embeddings via Ollama (local)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"  # 768-dim
```

**Alternatively**, use environment variables (recommended):

```bash
# Create .env file
PINECONE_API_KEY=your-pinecone-api-key
GEMINI_API_KEY=your-gemini-api-key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Step 5: Setup Neo4j

#### Option A: Neo4j Desktop (Local)
1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new database
3. Set password
4. Start the database
5. Note the connection details (usually `bolt://localhost:7687`)

#### Option B: Neo4j Aura (Cloud)
1. Sign up at [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create a free instance
3. Save the connection URI and credentials
4. Update `config.py` with your Aura URI

### Step 6: Load Data into Neo4j

```bash
python load_to_neo4j.py
```

Expected output:
```
🚀 Starting Neo4j Load Process
✅ Connected to Neo4j at bolt://localhost:7687
✅ Loaded 35 records from vietnam_travel_dataset.json
🔄 Creating 35 nodes...
✅ All nodes created
🔄 Creating relationships...
✅ Relationships created

📊 Neo4j Database Statistics:
   Total Nodes: 35
   Total Relationships: 78
   Node Types:
      Destination: 15
      Activity: 12
      Accommodation: 6
      Restaurant: 2
```

### Step 7: Visualize Graph (Optional)

```bash
python visualize_graph.py
```

This shows:
- Node type distribution
- Location summary
- Sample nodes and relationships
- Instructions for browser visualization

### Step 8: Upload Embeddings to Pinecone (Ollama embeddings)

```bash
python pinecone_upload.py
```

Expected output:
```
🚀 Starting Pinecone Upload Process
✅ Configuration validated successfully!
✅ Loaded 35 records from vietnam_travel_dataset.json
Creating new index: vietnam-travel
✅ Index 'vietnam-travel' created successfully

🔄 Generating embeddings...
Processing 1/35: Hanoi
Processing 2/35: Halong Bay
...
📤 Starting upload of 35 vectors in batches of 100
✅ Uploaded batch 1: vectors 1 to 35

📊 Index Statistics:
   Total vectors: 35
   Dimension: 768

✅ All done! Check your Pinecone dashboard to verify the upload.
```

### Step 9: Run the Hybrid Chat

```bash
python hybrid_chat.py
```

## 💬 Using the Assistant

### Interactive Commands

- **Type your question**: Get AI-generated travel recommendations
- **`examples`**: Show sample queries
- **`stats`**: Display system statistics
- **`clear`**: Clear cache
- **`quit`** or **`exit`**: Exit the program

### Example Queries

1. **Itinerary Planning**:
   ```
   Create a romantic 4 day itinerary for Vietnam
   ```

2. **Activity Recommendations**:
   ```
   What are the best activities in Hanoi?
   ```

3. **Accommodation Suggestions**:
   ```
   Recommend luxury hotels in Ho Chi Minh City
   ```

4. **Destination Information**:
   ```
   Tell me about Halong Bay
   ```

5. **Food & Dining**:
   ```
   Best restaurants in Hoi An for authentic Vietnamese food
   ```

6. **Adventure Travel**:
   ```
   Plan a trekking adventure in Sapa
   ```

### Sample Interaction 

```
================================================================================
🌏  HYBRID AI TRAVEL ASSISTANT FOR VIETNAM
================================================================================

🗣️  Enter your travel question: Create a romantic 4 day itinerary for Vietnam

================================================================================
🔄 Building hybrid context (async)...
================================================================================
🔍 Searching vector database for: 'Create a romantic 4 day itinerary for Vietnam'
🕸️  Querying knowledge graph...
   Found 20 graph nodes
   Found 5 similar results

=== SUMMARY ===
Top semantic matches:
- Hanoi (score 0.92)
- Halong Bay (score 0.88)
- Hoi An (score 0.86)
Top graph nodes:
- Hanoi (Destination)
- Halong Bay (Destination)
- Hoi An (Destination)

🤖 Generating AI response with Gemini...

⏱️  Total time: 44.68s

================================================================================
💬 RESPONSE:
================================================================================
Chào bạn! What a wonderful idea to plan a romantic getaway to Vietnam! Based on your request and our knowledge base, here is a dreamy 4‑day itinerary designed for romance in Hoi An, with a nod to Đà Lạt as a future option.

Overview
- Focus on Hoi An’s lantern-lit Ancient Town for a magical couple experience.

Best Time to Visit
- Dry season Feb–May for warm, sunny weather and evening lantern charm.

Day-by-day plan
- Day 1: Arrival & Lantern-Lit Romance
  - Arrive at Da Nang (DAD) → private transfer to Hoi An (~45m)
  - Settle in, riverside dinner, lantern boat ride on Thu Bon River
- Day 2: Cultural Charms & Culinary Love
  - Japanese Covered Bridge, Phung Hung Old House; cooking class + tailoring
  - Couple’s spa; candlelit dinner away from main streets
- Day 3: Countryside Serenity & Beach Bliss
  - Bicycle to Tra Que Vegetable Village; relax at An Bang Beach
  - Optional riverside fine dining (e.g., Mango Mango)
- Day 4: Farewell & Cherished Memories
  - Coffee in Old Town; last tailoring pickup; transfer to DAD

Logistics
- Flights: Fly into Da Nang International Airport (DAD)
- Transportation: Private car DAD ↔ Hoi An (~45m); walk/cycle inside the town
- Visa: Check requirements for your nationality well in advance

Food & Stay
- Accommodation: Anantara Hoi An Resort; The Little Riverside Hoi An; Hotel Royal Hoi An – MGallery
- Must‑try foods: Cao Lầu, White Rose Dumplings, Cơm Gà, Bánh Mì Phượng, fresh seafood (An Bang)

Tips
- Embrace the slow pace; time visits around the monthly lantern festival; carry cash for small vendors; bring swimwear

---
💡 Answer generated using 5 semantic matches and 20 graph connections.

================================================================================
🗣️  Enter your travel question: What are the best activities in Hanoi?


