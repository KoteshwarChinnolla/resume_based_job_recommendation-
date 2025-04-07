from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.mongodb import MongoDb
from langchain_aws import BedrockEmbeddings# MongoDB Atlas connection string

mdb_connection_string = "mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

embeddings = BedrockEmbeddings(
    credentials_profile_name="default",  # AWS credentials profile
    region_name="us-east-1",
    model_id="amazon.titan-embed-text-v2:0",
)

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://arxiv.org/pdf/1706.03762"],
    vector_db=MongoDb(
        collection_name="recipes",
        db_url=mdb_connection_string,
        embedder=embeddings,
        wait_until_index_ready=60,
        wait_after_insert=300
    ),
)


agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("How to make Thai curry?", markdown=True)