import base64
import os
import uuid
import gradio as gr

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma  # Để tương tác với ChromaDB qua LangChain
from langchain_community.embeddings import SentenceTransformerEmbeddings  # Để tạo embeddings

from openai import OpenAI
from dotenv import load_dotenv


def get_or_create_vectorstore(file_path: str):
    # Tạo tên collection từ tên file
    file_name = file_path.split("/")[-1]
    vectorstore = Chroma(
        persist_directory="./data",  # Thư mục lưu trữ
        collection_name=file_name,
        # Sử dụng model SentenceTransformer để tạo embeddings
        embedding_function=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    )

    return vectorstore


def read_pdf_content(file_path: str | None):
    """Đọc nội dung file PDF"""
    if file_path is None:
        return None

    loader = PyMuPDFLoader(file_path)
    documents = loader.load()

    return documents


def chunk_document(documents):
    """Chia tài liệu thành các đoạn nhỏ 800 ký tự, với độ chồng lấp 80 ký tự"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
    )
    chunks = text_splitter.split_documents(documents)
    # Tạo ID duy nhất cho mỗi chunk dựa trên nội dung
    for chunk in chunks:
        chunk.id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.page_content))

    return chunks


def create_pdf_html(file_path: str | None):
    """Tạo HTML để xem trước PDF"""
    if file_path is None:
        return ""

    try:
        # Đọc file PDF
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Tạo HTML với PDF viewer nhúng
        pdf_display = f'''
            <div style="width: 100%; height: 800px;">
                <iframe
                    src="data:application/pdf;base64,{base64_pdf}"
                    width="100%"
                    height="100%"
                    style="border: none;">
                </iframe>
            </div>
        '''
        return pdf_display
    except Exception as e:
        return f"Error displaying PDF: {str(e)}"


def process_file(file_path: str | None):
    """Xử lý file PDF đã tải lên và trả về trạng thái cùng bản xem trước HTML"""

    if file_path is None:
        yield "Please upload a PDF file first.", ""

    try:
        # Tạo bản xem trước PDF
        yield "Reading PDF file...", ""
        pdf_html = create_pdf_html(file_path)
        yield "Processing PDF file...", pdf_html

        # Đọc nội dung file PDF và chia thành các đoạn nhỏ
        documents = read_pdf_content(file_path)
        if not documents:
            yield "Error processing PDF file.", ""

        chunks = chunk_document(documents)

        # Tạo vector store và thêm các đoạn văn bản vào đó
        yield "Creating vector store...", pdf_html
        vectorstore = get_or_create_vectorstore(file_path)
        yield "Adding documents to vector store...", pdf_html
        vectorstore.add_documents(chunks)

        yield "PDF file processed successfully.", pdf_html
    except Exception as e:
        yield f"Error processing file: {str(e)}", ""


# Load biến môi trường
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "Please set the OPENAI_API_KEY environment variable. You can get one at https://platform.openai.com/account/api-keys")
# openai_client = OpenAI(api_key=OPENAI_API_KEY)


from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)




def chat_with_pdf(file_path: str, message: str, history):
    """Xử lý tương tác chat"""
    if not message:
        yield []

    try:
        history.append((message, "Đang xử lý..."))
        yield "", history

        # Lấy dữ liệu liên quan từ VectorDB
        vectorstore = get_or_create_vectorstore(file_path)
        results = vectorstore.similarity_search(query=message, k=3)

        if not results:
            history.append((message, "Không tìm thấy dữ liệu liên quan trong PDF."))
            yield "", history

        history[-1] = (message, "Tìm được dữ liệu trong VectorDB!")
        yield "", history

        # Đưa dữ liệu vào context của prompt để trả lời
        CONTEXT = ""
        for document in results:
            CONTEXT += document.page_content + "\n\n"

        prompt = f"""
        Use the following CONTEXT to answer the QUESTION at the end.
        If you don't know the answer or unsure of the answer, just say that you don't know, don't try to make up an answer.
        Use an unbiased and journalistic tone.

        CONTEXT: {CONTEXT}
        QUESTION: {message}
        """

        print(prompt)
        # response = openai_client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ],
        # )

        # print(response.choices[0].message.content)

        # # Cập nhật cặp tin nhắn cuối cùng
        # history[-1] = (message, response.choices[0].message.content)
        # yield "", history

        response = llm.invoke(
            [
                ("user", prompt)
            ],
        )

        history[-1] = (message, response.content)
        yield "", history



    except Exception as e:
        print('error', e)
        history.append((message, f"Error: {str(e)}"))
        return "", history


def create_ui():
    """Tạo giao diện Gradio"""
    with gr.Blocks() as demo:
        gr.Markdown("# Chat with PDF")

        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                )
                process_button = gr.Button("Process PDF")
                status_output = gr.Textbox(label="Status")
                pdf_preview = gr.HTML(label="PDF Preview")

            with gr.Column(scale=1):
                message_box = gr.Textbox(label="Ask a question about your PDF")
                chatbot = gr.Chatbot(height=600)

        # Xử lý sự kiện
        process_button.click(
            fn=process_file,
            inputs=[file_input],
            outputs=[status_output, pdf_preview]
        )

        message_box.submit(
            fn=chat_with_pdf,
            inputs=[file_input, message_box, chatbot],
            outputs=[message_box, chatbot]
        )

    return demo


# Khởi chạy ứng dụng
if __name__ == "__main__":
    demo = create_ui()
    demo.launch()