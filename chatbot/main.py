from pdfchucks import PDFChunkEmbedder
from chatbot.vector_searchabout import VectorSearch


# pdf_store=PDFChunkEmbedder(PDF_PATH, MONGO_URI, DB_NAME, COLLECTION_NAME)
# pdf_store.process_and_store()
searcher = VectorSearch()
query = input("Enter your query: ")
results = searcher.search_documents(query)

for i, res in enumerate(results):
    print(f"\nResult {i+1} (Score: {res['score']}):\n{res['text']}")

answer = searcher.generate_answer(query, results)
print("\n\nAnswer:\n", answer)

