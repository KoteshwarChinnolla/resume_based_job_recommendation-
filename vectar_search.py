from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_qdrant import QdrantVectorStore
# from qdrant_client import QdrantClient
# from qdrant_client.http.models import Distance, VectorParams
# from qdrant_client.http.exceptions import UnexpectedResponse
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from vector_store.py import MongoDBVectorStore
from agno.agent import Agent
from agno.knowledge.langchain import LangChainKnowledgeBase
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
urls = ["https://arxiv.org/pdf/1706.03762"]

loader = WebBaseLoader(urls)
data = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=50
)
chunks = text_splitter.split_documents(data)
embeddings = FastEmbedEmbeddings(model_name="thenlper/gte-large")

client = MongoClient('mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client["Growup"]  
collection_name = "jobs"
try:
    collection_info = db[collection_name].find_one()
except CollectionInvalid:
    db.create_collection(collection_name)

# Initialize the vector store
vector_store = MongoDBVectorStore(
    client=db,
    collection_name=collection_name,
    embedding=embeddings,
)
vector_store.add_documents(documents=chunks)
retriever = vector_store.as_retriever()
knowledge_base = LangChainKnowledgeBase(retriever=retriever)

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    knowledge=knowledge_base,
    description="Answer to the user question from the knowledge base",
    tools=[DuckDuckGoTools()],      # Add DuckDuckGo tool to search the web
    show_tool_calls=True,  
    markdown=True,
    search_knowledge=True,
)

agent.print_response("Tell me about a breaking news story from New York.", stream=True)

# agent = Agent(
#     model=Groq(id="llama-3.3-70b-versatile"),
#     description="You are an enthusiastic news reporter with a flair for storytelling!",
#     tools=[DuckDuckGoTools()],      # Add DuckDuckGo tool to search the web
#     show_tool_calls=True,           # Shows tool calls in the response, set to False to hide
#     markdown=True                   # Format responses in markdown
# )

# # Prompt the agent to fetch a breaking news story from New York
# agent.print_response("Tell me about a breaking news story from New York.", stream=True)