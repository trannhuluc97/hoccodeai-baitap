from dotenv import load_dotenv
from openai import OpenAI
import os
import inspect
from pydantic import TypeAdapter
import requests
import yfinance as yf
import json
import gradio as gr


def get_symbol(company: str) -> str:
    """
    Retrieve the stock symbol for a specified company using the Yahoo Finance API.
    :param company: The name of the company for which to retrieve the stock symbol, e.g., 'Nvidia'.
    :output: The stock symbol for the specified company.
    """
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": company, "country": "United States"}
    user_agents = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    res = requests.get(
        url=url,
        params=params,
        headers=user_agents)

    data = res.json()
    symbol = data['quotes'][0]['symbol']
    return symbol


def get_stock_price(symbol: str):
    """
    Retrieve the most recent stock price data for a specified company using the Yahoo Finance API via the yfinance Python library.
    :param symbol: The stock symbol for which to retrieve data, e.g., 'NVDA' for Nvidia.
    :output: A dictionary containing the most recent stock price data.
    """
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")
    latest = hist.iloc[-1]
    return {
        "timestamp": str(latest.name),
        "open": latest["Open"],
        "high": latest["High"],
        "low": latest["Low"],
        "close": latest["Close"],
        "volume": latest["Volume"]
    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_symbol",
            "description": inspect.getdoc(get_symbol),
            "parameters": TypeAdapter(get_symbol).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": inspect.getdoc(get_stock_price),
            "parameters": TypeAdapter(get_stock_price).json_schema(),
        },
    }
]

FUNCTION_MAP = {
    "get_symbol": get_symbol,
    "get_stock_price": get_stock_price
}

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-xxxx'
)


def get_completion(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        temperature=0
    )
    return response


# Bắt đầu làm bài tập từ line này!

def chat_logic_AI(message, history_message):
    messages = [
        {"role": "system", "content": "You are a cheerful, playful, and slightly cheeky customer support assistant. Your job is to help users with accurate, clear, and helpful answers — but make it fun! Use a light-hearted, friendly tone, sprinkle in some emojis where appropriate, and don’t be afraid to crack a gentle joke or two. Think of yourself as a helpful bestie who happens to know everything about the company. Stay informative, but keep things casual, upbeat, and a little bit sassy (in a good way)."}
    ]
    for user_message, bot_message in history_message:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": bot_message})
        
    messages.append({"role": "user", "content": message})
    
    history_message.append([message, "waitting.."])
    yield "", history_message

    response = get_completion(messages)
    first_choice = response.choices[0]
    finish_reason = first_choice.finish_reason

    # Loop cho tới khi model báo stop và đưa ra kết quả
    while finish_reason != "stop":
        tool_call = first_choice.message.tool_calls[0]
        tool_call_function = tool_call.function
        tool_call_arguments = json.loads(tool_call_function.arguments)

        tool_function = FUNCTION_MAP[tool_call_function.name]
        result = tool_function(**tool_call_arguments)

        messages.append(first_choice.message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call_function.name,
            "content": json.dumps({"result": result})
        })

        # Chờ kết quả từ LLM
        response = get_completion(messages)
        first_choice = response.choices[0]
        finish_reason = first_choice.finish_reason

    final_response = first_choice.message.content or ""
    history_message[-1][1] = final_response
    yield "", history_message

with gr.Blocks() as blocks:
    gr.Markdown("#Chatbot")
    message = gr.Textbox(label="Nhập nội dung tin nhắn:")
    chatbot = gr.Chatbot(label="Stock Chatbot", height=600)
    message.submit(chat_logic_AI, [message, chatbot], [message, chatbot])

blocks.launch()