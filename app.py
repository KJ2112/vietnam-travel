# streamlit_app.py
import streamlit as st
import time
import config
from hybrid_chat import HybridTravelAssistant

st.set_page_config(page_title="Vietnam Travel Assistant", page_icon="🌏", layout="wide")

# Sidebar: health and settings
with st.sidebar:
    st.title("⚙️ Settings")
    ok = config.validate_config()
    st.markdown("—")
    st.subheader("Stats")
    if "assistant" in st.session_state:
        a = st.session_state["assistant"]
        st.write(f"Cached embeddings: {len(a.embedding_cache)}")
        st.write(f"Cached queries: {len(a.query_cache)}")
    st.markdown("—")
    st.caption("Powered by: Ollama (nomic-embed-text) + Pinecone + Neo4j + Gemini")

# Initialize assistant once per session
if "assistant" not in st.session_state:
    try:
        st.session_state["assistant"] = HybridTravelAssistant()
    except Exception as e:
        st.error(f"Failed to initialize assistant: {e}")
        st.stop()

assistant = st.session_state["assistant"]

st.title("🌏 Hybrid AI Travel Assistant for Vietnam")
st.write("Combines Vector Search (Pinecone) + Knowledge Graph (Neo4j) + AI (Gemini)")

# Example prompts
examples = [
    "Create a romantic 4 day itinerary for Vietnam",
    "What are the best activities in Hanoi?",
    "Recommend luxury hotels in Ho Chi Minh City",
    "Plan a beach vacation in Nha Trang"
]

cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True):
        st.session_state["query"] = ex

query = st.text_input("Enter your travel question:", value=st.session_state.get("query", ""))

run_cols = st.columns(3)
run = run_cols[0].button("Ask", type="primary")
clear_cache = run_cols[1].button("Clear cache")
show_context = run_cols[2].checkbox("Show context details")

if clear_cache:
    assistant.embedding_cache.clear()
    assistant.query_cache.clear()
    st.success("Cache cleared!")

if run and query.strip():
    with st.spinner("Building hybrid context and generating answer..."):
        t0 = time.time()
        answer = assistant.chat(query.strip())
        elapsed = time.time() - t0

    st.success(f"Done in {elapsed:.2f}s")
    st.subheader("💬 Response")
    st.markdown(answer)

    # Optionally rebuild context to show details (no LLM call)
    if show_context:
        st.subheader("🧠 Context (debug)")
        context, metadata = assistant.build_context(query.strip())
        st.write(f"Vector results: {metadata['vector_results_count']}, Graph nodes: {metadata['graph_results_count']}")
        st.text_area("Context used", context, height=250)