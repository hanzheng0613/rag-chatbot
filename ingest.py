# ingest.py
import os, boto3
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import RequestsHttpConnection, AWSV4SignerAuth

load_dotenv()

# --- Config ---
REGION        = os.getenv("AWS_REGION", "us-east-1")
OS_HOST       = os.getenv("OPENSEARCH_HOST")          # no trailing slash
OS_INDEX      = os.getenv("OPENSEARCH_INDEX", "rag-documents")
OS_USER       = os.getenv("OPENSEARCH_USER", "hanzheng0613")
OS_PASS       = os.getenv("OPENSEARCH_PASS")

# --- Bedrock embeddings (Titan Embeddings V2) ---
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name=REGION,
)

# --- Text splitter ---
# chunk_size=1000 chars, overlap=200 so context isn't lost at boundaries
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "],
)

def ingest_pdf(pdf_path: str):
    print(f"Loading {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    pages  = loader.load()                        # list of Document objects

    print(f"  → {len(pages)} pages loaded")
    chunks = splitter.split_documents(pages)
    print(f"  → {len(chunks)} chunks created")

    # Each chunk keeps metadata: source filename + page number
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(pdf_path)

    # --- Store in OpenSearch ---
    # First call creates the index; subsequent calls append
    vectorstore = OpenSearchVectorSearch.from_documents(
        documents=chunks,
        embedding=embeddings,
        opensearch_url=OS_HOST,
        http_auth=(OS_USER, OS_PASS),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        index_name=OS_INDEX,
        engine="faiss",          # OpenSearch's built-in ANN engine
        bulk_size=500,
    )
    print(f"  → Stored in OpenSearch index '{OS_INDEX}'")
    return vectorstore

if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    ingest_pdf(pdf)