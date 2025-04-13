#pdfchucks.py
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModel
from pymongo import MongoClient
import torch
MONGO_URI = "mongodb+srv://Mithunlogin:12345@cluster0.nfdmggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "chatbot"
# COLLECTION_NAME = "aboutus"
COLLECTION_NAME = "services"
# PDF_PATH = "./pdfs/about_us.pdf"
PDF_PATH = "./pdfs/Our_Services.pdf"
class PDFChunkEmbedder:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.pdf_path = PDF_PATH
        self.mongo_uri = MONGO_URI
        self.db = MongoClient(self.mongo_uri)[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            return outputs.last_hidden_state[:, 0, :].squeeze().tolist()

    def process_and_store(self):
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        for chunk in chunks:
            embedding = self.get_embedding(chunk.page_content)
            self.collection.insert_one({"text": chunk.page_content, "embedding": embedding})

        print("Chunks embedded and stored in MongoDB.")

# store=PDFChunkEmbedder()
# store.process_and_store()
