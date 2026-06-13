# 📄 RAG Chatbot — AWS Bedrock + OpenSearch + Streamlit

A Retrieval-Augmented Generation (RAG) chatbot that lets you upload PDF documents and ask questions about their content. The app retrieves relevant document chunks from a vector database and uses Claude (via AWS Bedrock) to generate grounded, cited answers.

---

## Features

- 📤 Upload PDFs directly from the chat interface
- 🔍 Semantic search over document chunks using vector embeddings
- 🤖 Conversational Q&A powered by Claude on AWS Bedrock
- 📚 Source citations (document name + page number) for every answer
- 🧠 Chat history-aware retrieval (follow-up questions work naturally)
- 🐳 Containerized with Docker, deployable on AWS ECS Fargate

---

## Architecture

```
PDF Upload → Text Splitter → Titan Embeddings V2 (Bedrock)
                                      │
                                      ▼
                            OpenSearch (vector store)
                                      │
User Question → History-aware Retriever → Top-k chunks
                                      │
                                      ▼
                     Claude (Bedrock) → Answer + Citations
```

**Components:**

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Orchestration | LangChain |
| Embeddings | Amazon Titan Embeddings V2 |
| LLM | Anthropic Claude (via Amazon Bedrock) |
| Vector store | Amazon OpenSearch Service |
| Deployment | Docker + Amazon ECS Fargate + ECR |

---

## Project Structure

```
rag-chatbot/
├── app.py            # Streamlit UI and chat logic
├── chain.py          # RAG chain (retriever + LLM + memory)
├── retriever.py       # OpenSearch vector store retriever
├── ingest.py          # PDF loading, chunking, and embedding into OpenSearch
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container build definition
├── .env                # Environment variables (NOT committed)
└── .gitignore
```

---

## Prerequisites

- Python 3.11+
- AWS account with access to:
  - **Amazon Bedrock** (Titan Embeddings V2 and an Anthropic Claude model enabled)
  - **Amazon OpenSearch Service**
- AWS CLI configured (`aws configure`)
- Docker (for containerized deployment)

---

## Setup (Local)

### 1. Clone the repo
```bash
git clone https://github.com/hanzheng0613/rag-chatbot.git
cd rag-chatbot
```

### 2. Create a virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:
```bash
AWS_REGION=us-east-1
AWS_PROFILE=default
OPENSEARCH_HOST=https://your-domain.us-east-1.es.amazonaws.com
OPENSEARCH_INDEX=rag-documents
OPENSEARCH_USER=your-master-username
OPENSEARCH_PASS=your-master-password
```

### 5. Ingest a PDF (optional — can also be done from the UI)
```bash
python ingest.py path/to/document.pdf
```

### 6. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Deployment (AWS ECS Fargate)

### 1. Build and push the Docker image to ECR
```bash
aws ecr create-repository --repository-name rag-chatbot

aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

docker build --platform linux/amd64 -t rag-chatbot .
docker tag rag-chatbot:latest <account_id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest
docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/rag-chatbot:latest
```

### 2. Create ECS cluster, task definition, and service
- Register a Fargate task definition with the pushed image
- Set environment variables (`AWS_REGION`, `OPENSEARCH_HOST`, `OPENSEARCH_INDEX`, `OPENSEARCH_USER`, `OPENSEARCH_PASS`)
- Attach an IAM **task role** with `AmazonBedrockFullAccess` and `AmazonOpenSearchServiceFullAccess`
- Create a service with `assignPublicIp=ENABLED` and a security group allowing inbound traffic on port `8501`

### 3. Access the app
```
http://<task_public_ip>:8501
```

> ⚠️ Note: the public IP changes if the task restarts. For a stable URL, add an Application Load Balancer.

---

## Cost Notes

| Resource | Approx. cost |
|---|---|
| OpenSearch (`t3.small.search`) | ~$25–50/month (runs 24/7) |
| Bedrock (Titan + Claude) | Pay-per-token, usually <$1/month for light use |
| ECS Fargate | Pay while running |
| ECR | Minimal storage cost |

**To avoid ongoing charges when not in use:**
```bash
# Scale ECS service to 0
aws ecs update-service --cluster rag-chatbot-cluster --service rag-chatbot-service --desired-count 0

# Delete OpenSearch domain
aws opensearch delete-domain --domain-name <your-domain-name>
```

---

## Security Notes

- Never commit `.env`, task definitions, or any file containing credentials
- Rotate your OpenSearch master password regularly
- Consider AWS Secrets Manager for production credential storage
- Add authentication (e.g. `streamlit-authenticator`) before sharing the app publicly

---

## License

MIT
