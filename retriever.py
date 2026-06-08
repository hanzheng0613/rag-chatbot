# retriever.py
import os
from dotenv import load_dotenv
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import RequestsHttpConnection

load_dotenv()

REGION   = os.getenv("AWS_REGION", "us-east-1")
OS_HOST  = os.getenv("OPENSEARCH_HOST")
OS_INDEX = os.getenv("OPENSEARCH_INDEX", "rag-documents")
OS_USER  = os.getenv("OPENSEARCH_USER", "admin")
OS_PASS  = os.getenv("OPENSEARCH_PASS")

embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name=REGION,
)

def get_retriever(k: int = 4):
    """Return a LangChain retriever that fetches top-k relevant chunks."""
    vectorstore = OpenSearchVectorSearch(
        index_name=OS_INDEX,
        embedding_function=embeddings,
        opensearch_url=OS_HOST,
        http_auth=(OS_USER, OS_PASS),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    # k=4 means "return the 4 most relevant chunks" for each query
    return vectorstore.as_retriever(search_kwargs={"k": k})