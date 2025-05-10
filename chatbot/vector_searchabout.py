from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModel
import torch
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "chatbot"
COLLECTION_NAME = "aboutus"
PDF_PATH = "./pdfs/about_us.pdf"
class VectorSearch_about:
    def __init__(self):
        client = MongoClient(MONGO_URI)
        self.collection = client[DB_NAME][COLLECTION_NAME]
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.chat = ChatGroq(model_name="llama-3.3-70b-versatile")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a RAG model output generator that generates a response based on the retrieved documents."),
            ("human", "Retrieved documents: {text}.\n\nQuestion: {query}")
        ])
        self.chain= self.prompt | self.chat

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]
            return embeddings.squeeze().tolist()

    def search_documents(self, query):
        query_vector = self.get_embedding(query)
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "chatbot",
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": 3
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]
        results = list(self.collection.aggregate(pipeline))
        return results

    def generate_answer(self, query, results):
        context = "\n\n".join([res["text"] for res in results])
        response = self.chain.invoke({"text": context, "query": query})
        return response.content