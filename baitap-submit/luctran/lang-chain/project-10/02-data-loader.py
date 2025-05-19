# pip install langchain langchain-community pymupdf langchain-chroma chromadb

# Import các thư viện cần thiết
from langchain_community.document_loaders import PyMuPDFLoader  # Để đọc file PDF
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Để chia nhỏ văn bản
from langchain_chroma import Chroma  # Để tương tác với ChromaDB qua LangChain
from langchain_community.embeddings import SentenceTransformerEmbeddings  # Để tạo embeddings
import chromadb  # Để tương tác trực tiếp với ChromaDB
from chromadb.utils import embedding_functions  # Các hàm tạo embedding của ChromaDB
import uuid  # Để tạo ID duy nhất cho các chunks


from langchain_huggingface import HuggingFaceEmbeddings


# Bước 1: Đọc dữ liệu từ file PDF
print("========Loading data from PDF=========")
loader = PyMuPDFLoader("docs/monopoly.pdf")  # Khởi tạo loader với đường dẫn file PDF
data = loader.load()  # Đọc toàn bộ nội dung PDF

# In thông tin về dữ liệu đã đọc
print(f"Tổng số pages: {len(data)}")
print(data[0])

# Bước 2: Chia nhỏ văn bản thành các chunks
print("\n\n========Splitting data into chunks=========")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,  # Mỗi chunk có độ dài tối đa 700 ký tự
    chunk_overlap=100,  # Các chunk chồng lấp nhau 100 ký tự để đảm bảo tính liên tục
)

# Ở bài trước ta dùng `split_text` để chia nhỏ văn bản, ở đây ta dùng `split_documents` để chia nhỏ các documents
chunks = text_splitter.split_documents(data)
print(f"Tổng số chunks: {len(chunks)}")
print(chunks[0])

# Định nghĩa tên collection để lưu trong ChromaDB
COLLECTION_NAME = "monopoly"

# Bước 3: Lưu trữ dữ liệu vào ChromaDB
print("\n\n========Storing data into ChromaDB=========")
# Khởi tạo client với chế độ lưu trữ cố định
client = chromadb.PersistentClient(path="./data")
# Tạo hoặc lấy collection đã tồn tại
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    # Sử dụng hàm embedding mặc định của ChromaDB (all-MiniLM-L6-v2)
    embedding_function=embedding_functions.DefaultEmbeddingFunction(),
)

# Thêm documents vào collection
collection.add(
    documents=[doc.page_content for doc in chunks],  # Nội dung văn bản
    metadatas=[doc.metadata for doc in chunks],  # Metadata (như số trang, nguồn,...)
    # Tạo ID duy nhất cho mỗi chunk dựa trên nội dung
    ids=[str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]
)
print(f"Tổng số chunks trong collection: {collection.count()}")

# Bước 4: Thử nghiệm truy vấn dữ liệu từ ChromaDB
print("\n\n========Truy vấn dữ liệu từ ChromaDB=========")
# Tìm kiếm các chunks liên quan nhất đến câu query
q = collection.query(query_texts=["player run out of money"], n_results=3)
print(q["ids"][0])  # In ra các ID của chunks tìm được
print(q["documents"][0])  # In ra nội dung của chunks
print(q["metadatas"][0])  # In ra metadata của chunks

# Bước 5: Sử dụng LangChain Chroma để so sánh
print("\n\n========Sử dụng LangChain Chroma=========")
# Khởi tạo vector store với LangChain
vectorstore = Chroma.from_documents(
    persist_directory="./data-langchain",  # Thư mục lưu trữ
    collection_name=COLLECTION_NAME,
    # Sử dụng model SentenceTransformer để tạo embeddings
    # embedding=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    documents=chunks,
    # Tạo ID duy nhất cho mỗi chunk
    ids=[str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks],
)

# Thử nghiệm tìm kiếm với LangChain Chroma
print("\n\n========Truy vấn dữ liệu từ LangChain Chroma=========")
# Tìm kiếm các documents tương tự nhất với câu query
result = vectorstore.similarity_search(query="player run out of money", k=3)
print(result)