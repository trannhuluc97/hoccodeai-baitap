import services
import io

from models import ImageRequest
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Khởi tạo FastAPI
app = FastAPI()

# Thêm CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Stable Diffusers API"}

@app.post("/api/v1/generate/")
async def generate_image(imgRequest: ImageRequest):
    # Gọi hàm generate_image để tạo ảnh
    image = await services.generate_image(imgRequest=imgRequest)

    # Chuyển ảnh thành memory_stream để gửi về client
    memory_stream = io.BytesIO()
    image.save(memory_stream, format="PNG")
    memory_stream.seek(0)

    # API trả về một ảnh PNG, media type "image/png"
    return StreamingResponse(memory_stream, media_type="image/png")

@app.post("/api/v1/generatebase64/")
async def generate_base64_image(imgRequest: ImageRequest):
    # Gọi hàm generate_image để tạo ảnh
    image = await services.generate_image(imgRequest=imgRequest)

    # Chuyển ảnh thành base64 để gửi về client
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    # API trả về một ảnh base64
    return {"image": img_str}


# uvicorn 03-rest-api:app --reload --port 8080
# --reload cho phép FastAPI tự động reload khi có thay đổi trong code.
# --port 8080 để chọn port mà FastAPI sẽ chạy.