from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Load PDF
loader = PyPDFLoader("test.pdf")
pages = loader.load()

# Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=600)
docs = splitter.split_documents(pages)

# Embedding
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Build and save FAISS
vectorstore = FAISS.from_documents(docs, embedding)
vectorstore.save_local("vector_db")
