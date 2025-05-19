# 1. Viết một ứng dụng console đơn giản, người dùng gõ câu hỏi vào console, bot trả lời và in ra. Có thể dùng `stream` hoặc `non-stream`.

from openai import OpenAI

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-xxxx',
)

question = input("Enter question: ")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": question,
        }
    ],
    model="gpt-4o-mini",
    n=1,
    max_tokens=100
)

print("Bot answer: " + chat_completion.choices[0].message.content)
        
