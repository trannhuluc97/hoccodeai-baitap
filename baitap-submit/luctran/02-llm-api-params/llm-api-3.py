# 3. Tóm tắt website. Dán link website vào console, bot sẽ tóm tắt lại nội dung của website đó.

#    1. Người dùng dán link <https://tuoitre.vn/cac-nha-khoa-hoc-nga-bao-tu-manh-nhat-20-nam-sap-do-bo-trai-dat-2024051020334196.htm> vào console
#    2. Sử dụng `requests` để lấy nội dung website.
#    3. Dùng thư viện `beautifulsoup4` để parse HTML. (Bạn có thể hardcode lấy thông tin từ div có id là `main-detail` ở vnexpress)
#    4. Bạn cũng có thể thay bước 2-3 bằng cách dùng <https://jina.ai/reader/>, thên `r.jina.ai` để lấy nội dung website.
#    5. Viết prompt và gửi nội dung đã parse lên API để tóm tắt. (Xem lại bài prompt engineering nha!)

from openai import OpenAI
import requests
from bs4 import BeautifulSoup

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-xxxx',
)


# Retrieve the HTML content from the specified URL
def get_html_from_url(target_url):
    try:
        res = requests.get(target_url)
        res.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        return res.text
    except requests.RequestException as err:
        print("Failed to retrieve the web page:", err)
        return None

# Extract visible paragraph text from the HTML
def extract_text_from_html(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    paragraphs = soup.select("p")
    combined_text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return combined_text

# Generate a summary using the OpenAI model
def generate_summary_with_openai(raw_text):
    summary_prompt = (
        "Please summarize the following article while focusing on the key points and important details. "
        "Your summary should be concise yet informative, capturing the essence of the content. "
        "Maintain a positive tone and add a touch of humor where appropriate, without losing the core message. "
        "Write the summary in Vietnamese.\n\n"
        "===\n"
        f"{raw_text}\n"
        "===\n"
    )

    conversation = [
        {"role": "system", "content": "You are an expert in analyzing and summarizing website content."},
        {"role": "user", "content": summary_prompt}
    ]

    try:
        response = client.chat.completions.create(
            messages=conversation,
            temperature=0.5,
            model="gpt-4o-mini"
        )
        return response.choices[0].message.content
    except Exception as api_error:
        print("OpenAI API error:", api_error)
        return None

# Main function to orchestrate the summarization flow
def summarize_webpage():
    website_url = input("Paste the website URL here: ").strip()
    html_source = get_html_from_url(website_url)

    if not html_source:
        print("Unable to fetch content from the provided link.")
        return

    article_text = extract_text_from_html(html_source)
    if not article_text:
        print("No textual content found to summarize.")
        return

    summary_result = generate_summary_with_openai(article_text)
    if summary_result:
        print("\n📌 Summary:")
        print(summary_result)
    else:
        print("Failed to generate a summary.")


summarize_webpage()