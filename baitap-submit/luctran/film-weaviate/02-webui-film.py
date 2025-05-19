import gradio as gr
import weaviate
from weaviate.embedded import EmbeddedOptions

# Cần chạy docker container cho model embedding:
# docker run -itp "8000:8080" semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
embedded_options = EmbeddedOptions(
    additional_env_vars={
        # Kích hoạt các module cần thiết: text2vec-transformers
        "ENABLE_MODULES": "backup-filesystem,text2vec-transformers",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",  # Chỉ định thư mục backup
        "LOG_LEVEL": "panic",  # Chỉ định level log, chỉ log khi có lỗi
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8000"  # API của model embedding
    },
    persistence_data_path="data",  # Thư mục lưu dữ liệu
)

# Khởi tạo Weaviate và kết nối
vector_db_client = weaviate.WeaviateClient(
    embedded_options=embedded_options
)
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

# Cấu hình tên collection
COLLECTION_NAME = "MovieCollection"


def search_movie(query):
    # Tìm kiếm theo ngữ nghĩa - NEAR_TEXT
    movie_collection = vector_db_client.collections.get(COLLECTION_NAME)
    response = movie_collection.query.near_text(
        query=query, limit=10
    )

    # Trả về thumbnail và title của các phim liên quan
    results = []
    for movie in response.objects:
        movie_tuple = (movie.properties['thumbnail'], movie.properties['title'])
        results.append(movie_tuple)
    print(results)
    return results


with gr.Blocks(title="Tìm kiếm phim với Vector Database") as interface:
    query = gr.Textbox(label="Tìm kiếm phim", placeholder="Tên, diễn viên, thể loại,...")
    search = gr.Button(value="Search")
    gallery = gr.Gallery(label="Movies", show_label=False, columns=[5], rows=[2], object_fit="contain", height="auto")

    # Khi người dùng bấm search, ta gọi hàm search_movie với đầu vào là query và truyền kết quả vào gallery
    search.click(fn=search_movie, inputs=query, outputs=gallery)

interface.queue().launch()