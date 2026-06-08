# app.py
import streamlit as st
from chain import build_chain
 
st.set_page_config(page_title="RAG Chatbot", page_icon="📄", layout="wide")
st.title("📄 Document Q&A — Powered by AWS Bedrock")
 
@st.cache_resource
def get_chain():
    return build_chain()
 
chain = get_chain()
 
# Sidebar: upload + ingest PDFs on the fly
with st.sidebar:
    st.header("Upload documents")
    uploaded = st.file_uploader("Drop PDFs here", type="pdf", accept_multiple_files=True)
    if uploaded and st.button("Ingest documents"):
        from ingest import ingest_pdf
        import tempfile, os
        with st.spinner("Embedding and indexing..."):
            for f in uploaded:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(f.read())
                    ingest_pdf(tmp.name)
                    os.unlink(tmp.name)
        st.success(f"Ingested {len(uploaded)} document(s)!")
 
# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# Render past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
 
# Chat input
if question := st.chat_input("Ask anything about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
 
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            result = chain.invoke(
                {"input": question},
                config={"configurable": {"session_id": "default"}}
            )
 
        answer = result["answer"]
        sources = result.get("context", [])
 
        st.markdown(answer)
 
        # Show source citations in an expander
        if sources:
            with st.expander(f"Sources ({len(sources)} chunks)"):
                for i, doc in enumerate(sources, 1):
                    meta = doc.metadata
                    st.caption(
                        f"**{i}. {meta.get('source', 'Unknown')}** "
                        f"— page {meta.get('page', '?')}"
                    )
                    st.text(doc.page_content[:300] + "...")
 
    st.session_state.messages.append({"role": "assistant", "content": answer})
 