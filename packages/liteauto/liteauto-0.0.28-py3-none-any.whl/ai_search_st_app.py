import streamlit as st
import os
from typing import List, Literal
from ai_enhanced_search import GoogleSearch, GoogleSearchDocument

# Define available models
AVAILABLE_MODELS = [
    "qwen2.5:7b-instruct",
    "qwen2.5-coder:1.5b-instruct",
    "qwen2.5-coder:0.5b-instruct",
    "qwen2.5:3b-instruct",
    "qwen2.5:0.5b-instruct",
    "qwen2.5:1.5b-instruct",
    "qwen2.5-coder:3b-instruct-q4_k_m",
    "qwen2.5-coder:7b-instruct",
    "qwen2.5-coder:14b-instruct-q4_K_M",
    "qwen2.5-coder:32b-instruct-q4_K_M",
    "llama3.2:1b-instruct-q4_K_M",
    "llama3.2:1b-instruct-fp16",
    "llama3.2:3b-instruct-q4_K_M",
    "llama3.2:3b-instruct-fp16",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "CohereForAI/c4ai-command-r-plus-08-2024",
    "Qwen/QwQ-32B-Preview",
    "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
    "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "NousResearch/Hermes-3-Llama-3.1-8B",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "microsoft/Phi-3.5-mini-instruct",
    "exaone3.5:2.4b",
    "EXAONE-3.5-2.4B-Instruct-BF16.gguf",
    "EXAONE-3.5-2.4B-Instruct-Q4_K_M.gguf",
    "Llama-3.2-1B-Instruct-f16.gguf",
    "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    "Llama-3.2-1B-Instruct-Q4_K_S.gguf",
    "Llama-3.2-1B-Instruct-Q8_0.gguf",
    "Llama-3.2-3B-Instruct-f16.gguf",
    "qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "qwen2.5-3b-instruct-fp16-00002-of-00002.gguf",
    "qwen2.5-7b-instruct-q4_k_m.gguf",
    "Qwen2.5-0.5B-Instruct-f16.gguf",
    "Qwen2.5-0.5B-Instruct-Q5_K_M.gguf"
]
import os
import sqlite3
from datetime import datetime
import json
from typing import List


# Database initialization
def init_db():
    conn = sqlite3.connect('search_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            results TEXT NOT NULL,
            model_name TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn


def save_search(conn, query: str, results: List[GoogleSearchDocument], model_name: str):
    c = conn.cursor()
    results_json = json.dumps([{'url': r.url, 'content': r.content} for r in results])
    c.execute('INSERT INTO searches (query, results, model_name) VALUES (?, ?, ?)',
              (query, results_json, model_name))
    conn.commit()


def get_search_history(conn):
    c = conn.cursor()
    c.execute('SELECT id, query, timestamp FROM searches ORDER BY timestamp DESC')
    return c.fetchall()


def get_search_by_id(conn, search_id):
    c = conn.cursor()
    c.execute('SELECT * FROM searches WHERE id = ?', (search_id,))
    return c.fetchone()


# Available models - keeping only the main ones for cleaner UI
AVAILABLE_MODELS = [
    "qwen2.5:7b-instruct",
    "qwen2.5-coder:1.5b-instruct",
    "qwen2.5:3b-instruct",
    "qwen2.5:0.5b-instruct",
    "llama3.2:3b-instruct-fp16"
]


def main():
    conn = init_db()

    # Remove default page margins and padding
    st.set_page_config(page_title="AI-Enhanced Search", layout="wide", initial_sidebar_state="auto")

    # Add custom CSS to reduce spacing
    st.markdown("""
            <style>
                .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                }
                div.stTitle {
                    margin-top: -3rem;
                }
            </style>
        """, unsafe_allow_html=True)

    # Rest of your main() function code...
    st.title("🚀 AI-Enhanced MultiSearch")

    # Model selection
    with st.sidebar.popover(label="",icon=":material/settings:",):
        # c1, c2, c3 = st.columns([1, 1, 1])

        model = st.text_input(
            "Select Model",
            value="qwen2.5:7b-instruct"
        )

        # API Key input
        api_key = st.text_input(
            "API Key",
            value="dsollama",
            type="password"
        )

        # Base URL input with default value
        base_url = st.text_input(
            "Base URL",
            value="http://192.168.170.76:11434/v1"
        )

        k = st.slider("How old are you?", 1, 10, 5)

    # Save settings button
    if st.sidebar.button("Start new chat"):
        os.environ['OPENAI_MODEL_NAME'] = model
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_BASE_URL'] = base_url
        st.sidebar.success("✅ Settings saved!")


    # Chat history section in sidebar
    st.sidebar.title("Recents")

    history = get_search_history(conn)
    for search_id, query, timestamp in history:
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if st.sidebar.button(f"🔍 {query[:30]}... ({dt.strftime('%H:%M')})", key=f"hist_{search_id}"):
            search_data = get_search_by_id(conn, search_id)
            if search_data:
                _, stored_query, _, results_json, used_model = search_data
                results = [GoogleSearchDocument(url=r['url'], content=r['content'])
                           for r in json.loads(results_json)]
                st.info(f"📜 Historical search: '{stored_query}' (using {used_model})")
                for idx, result in enumerate(results, 1):
                    with st.expander(f"Source {idx}: {result.url}", expanded=True):
                        st.markdown(result.content)




    # Search input
    # query = st.text_input("Enter your search query:", placeholder="e.g., when is modi born?")
    query = st.chat_input("Enter your search query:")

    if query:
        try:
            with st.spinner("🤖 AI is processing your query and searching..."):
                # Verify environment variables are set
                if not all(k in os.environ for k in ['OPENAI_MODEL_NAME', 'OPENAI_API_KEY', 'OPENAI_BASE_URL']):
                    st.error("⚠️ Please save settings first!")
                    return

                # Perform search
                results = GoogleSearch.perform_multi_queries_search(query,doc_k=k)

                # Save to database
                save_search(conn, query, results, os.environ['OPENAI_MODEL_NAME'])

                # Display results
                st.subheader(f"📊 Search Results ({len(results)} sources)")
                for idx, result in enumerate(results, 1):
                    with st.expander(f"Source {idx}: {result.url}", expanded=True):
                        st.markdown(result.content)


        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your settings and try again.")


if __name__ == "__main__":
    main()