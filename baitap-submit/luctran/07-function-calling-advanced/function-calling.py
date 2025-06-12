import os
import json
import openai
import inspect
import requests
from typing_extensions import TypedDict, Literal
from dotenv import load_dotenv
from pprint import pprint
from pydantic import TypeAdapter

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-xxxx',
)

# Định nghĩa kiểu dữ liệu
UnitType = Literal["celsius", "fahrenheit"]

class WeatherParams(TypedDict):
    location: str
    unit: UnitType

class StockParams(TypedDict):
    symbol: str

class WebsiteParams(TypedDict):
    url: str

# Các function
def get_current_weather(location: str, unit: UnitType):
    """Get the current weather in a given location"""
    return "Hà Nội hôm nay 7 độ C, trời rét, mưa phùn và sương mù dày"

def get_stock_price(symbol: str):
    """Get the current stock price of a given symbol"""
    pass

def view_website(url: str):
    """Retrieve the markdown content of a website using JinaAI Readability API."""
    
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    
    jina_url = f"https://r.jina.ai/{url}"

    try:
        print(f"Đang gửi request đến JinaAI: {jina_url}")
        response = requests.get(jina_url, headers=headers)

        print(f"Phản hồi HTTP: {response.status_code}")
        print(f"Nội dung phản hồi: {response.text[:500]}")
        
        response.raise_for_status()
        return response.text  # Trả về nội dung markdown

    except requests.exceptions.HTTPError as http_err:
        return f"❌ HTTP error: {http_err} - Response: {response.text}"
    except requests.exceptions.RequestException as req_err:
        return f"❌ Request error: {req_err}"
    
# Tạo tools tự động từ function list
def generate_tools(*funcs):
    tools = []
    for func in funcs:
        sig = inspect.signature(func)
        params = {k: v.annotation for k, v in sig.parameters.items()}
        adapter = TypeAdapter(TypedDict("Params", params))
        
        tools.append({
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__.strip() if func.__doc__ else "",
                "parameters": adapter.json_schema()
            }
        })
    return tools

# Tạo danh sách tools
tools = generate_tools(get_current_weather, get_stock_price, view_website)

COMPLETION_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"

# Nhập URL từ bàn phím
user_url = input("Nhập URL trang web cần tóm tắt: ")
messages = [{"role": "user", "content": f"Tóm tắt nội dung trang web {user_url}"}]

print("Bước 1: Gửi message lên cho LLM")
pprint(messages)

response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

print("\nBước 2: LLM đọc và phân tích ngữ cảnh")
pprint(response)

print("\nBước 3: Lấy kết quả từ LLM")
tool_call = response.choices[0].message.tool_calls[0]
pprint(tool_call)
arguments = json.loads(tool_call.function.arguments)

print("Bước 4: Chạy function tương ứng")

if tool_call.function.name == 'view_website':
    website_content = view_website(**arguments)
    print(f"\nKết quả bước 4: {website_content[:500]}...")  # Chỉ in 500 ký tự đầu để xem trước

    print("\nBước 5: Gửi nội dung website lên cho LLM để tóm tắt")
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "content": website_content
    })

    final_response = client.chat.completions.create(
        model=COMPLETION_MODEL,
        messages=messages
    )
    print(f"Kết quả cuối cùng từ LLM: {final_response.choices[0].message.content}.")