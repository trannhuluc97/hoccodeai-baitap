from openai import OpenAI
import json

def get_current_weather(location: str, unit: str):
    """Get the current weather in a given location"""
    # Hardcoded để demo, nhưng bạn cũng có thể gọi API bên ngoài
    return "Trời rét vãi nôi, 7 độ C"

def get_stock_price(symbol: str):
    pass

def view_website(url: str):
    pass

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit"
                    }
                },
                "required": ["location", "unit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price of a given symbol",
            "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_website",
            "description": "View a website",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
        }
    }
]

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-XXXX',
)

COMPLETION_MODEL = "gpt-4o-mini"


messages = [{"role": "user", "content": "Thời tiết ở Hà Nội hôm nay thế nào?"}]

print("Bước 1: Gửi message lên cho LLM")
print(messages)

response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages,
    tools=tools
)
print("Bước 2: LLM đọc và phân tích ngữ cảnh LLM")
print(response)

print("Bước 3: Lấy kết quả từ LLM")
tool_call = response.choices[0].message.tool_calls[0]

print(tool_call)

print("Bước 4: Chạy function get_current_weather ở máy mình")

# Vì ở đây ta có 3 hàm nên phải check theo name để gọi đúng hàm `get_current_weather`
if tool_call.function.name == 'get_current_weather':
    arguments = json.loads(tool_call.function.arguments)
    weather_result = get_current_weather(arguments.get('location'), arguments.get('unit'))
    # Hoặc code này cũng tương tự
    # weather_result = get_current_weather(**arguments)
    print(f"Kết quả bước 4: {weather_result}")

    # Kết quả bước 4: Trời rét vãi nôi, 7 độ C

print("Bước 5: Gửi kết quả lên cho LLM")
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": "get_current_weather",
    "content": weather_result
})
print(messages)

final_response = client.chat.completions.create(
    model=COMPLETION_MODEL,
    messages=messages
    # Ở đây không có tools cũng không sao, vì ta không cần gọi nữa
)

print(f"Kết quả cuối cùng từ LLM: {final_response.choices[0].message.content}.")
# In kết quả ra
# Kết quả cuối cùng từ LLM: Hôm nay ở Hà Nội trời rét, nhiệt độ khoảng 7 độ C. Bạn nên mặc ấm khi ra ngoài nhé!.

