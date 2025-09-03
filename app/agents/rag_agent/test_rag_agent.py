import os
import sys
from datetime import datetime

# Ensure project root is on sys.path for direct execution (python3 app/agents/...)
CURRENT_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(CURRENT_FILE), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from app.agents.rag_agent.rag_agent import VerificationRAGPipeline
from app.models.rag import RagRequest, RagResponse

pipeline = VerificationRAGPipeline()

request = RagRequest(
    post_id="123",
    post_content="Delhi is a union territory",
    context=[
        "Delhi is a union territory",
        "Delhi is the capital of India",
    ]
)

response = pipeline.verify(request, top_k=4)
print(response)