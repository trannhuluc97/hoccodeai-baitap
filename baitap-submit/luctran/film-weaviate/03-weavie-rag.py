import weaviate
from weaviate.embedded import EmbeddedOptions
from weaviate.classes.config import Configure, Property, DataType, Tokenization
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()


# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_KEY = "sk-proj-XXXX"

# Cần chạy docker container cho model embedding:
# docker run -itp "8000:8080" semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
embedded_options = EmbeddedOptions(
    additional_env_vars={
        # Kích hoạt các module cần thiết, nhớ thêm generative-openai
        "ENABLE_MODULES": "backup-filesystem,text2vec-transformers,generative-openai",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",  # Chỉ định thư mục backup
        "LOG_LEVEL": "panic",  # Chỉ định level log, chỉ log khi có lỗi
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8000",  # API của model embedding
        "OPENAI_APIKEY": OPENAI_API_KEY
    },
    persistence_data_path="data_rag",  # Thư mục lưu dữ liệu
)

vector_db_client = weaviate.WeaviateClient(
    embedded_options=embedded_options
)
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

COLLECTION_NAME = "MovieCollectionRAG"


def create_collection():
    # Đọc dữ liệu từ file JSON
    data = pd.read_json('movies-2020s.json')

    # Tạo schema cho collection
    movie_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        # Sử dụng model transformers để tạo vector
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        generative_config=Configure.Generative.openai(
            model="gpt-4o",
            # max_tokens=500,
            # presence_penalty=0,
            # temperature=0.7,
            # top_p=0.7,
        ),
        properties=[
            # Tiêu đề phim: text, được vector hóa và chuyển thành chữ thường
            Property(name="title", data_type=DataType.TEXT,
                     vectorize_property_name=True, tokenization=Tokenization.LOWERCASE),
            Property(name="extract", data_type=DataType.TEXT, tokenization=Tokenization.WHITESPACE),
            Property(name="cast", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            Property(name="genres", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.WORD),
            # Ảnh thumbnail và href, không chuyển thành vector
            Property(name="thumbnail", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="href", data_type=DataType.TEXT, skip_vectorization=True),
        ]
    )

    # Chuyển đổi dữ liệu để import
    sent_to_vector_db = data.to_dict(orient='records')
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB. Total records: {total_records}")

    # Import dữ liệu vào DB theo batch
    with movie_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)

    print("Data saved to Vector DB")


if vector_db_client.collections.exists(COLLECTION_NAME):
    print("Collection {} already exists".format(COLLECTION_NAME))
else:
    create_collection()

movies = vector_db_client.collections.get(COLLECTION_NAME)

# Dùng chung prompt để tạo 1 kết quả duy nhất với `grouped_task`
response = movies.generate.near_text(
    query="christmas holiday for family",
    grouped_task="Viết một bài giới thiệu ngắn gọn các bộ phim này.",
    limit=3
)
for movie in response.objects:
    print(movie.properties['title'])
print(f"Generated output: {response.generated}")

# Viết 3 prompt khác nhau để tạo ra 3 bài giới thiệu khác nhau cho 3 phim với `single_prompt`
response = movies.generate.near_text(
    query="christmas holiday for family",
    single_prompt="Viết một bài giới thiệu ngắn gọn tiếng Việt về bộ phim: {title}, tóm tắt: {extract}.",
    limit=3
)
for movie in response.objects:
    print(movie.properties['title'])
    print(movie.generated)

# Đóng kết nối
vector_db_client.close()