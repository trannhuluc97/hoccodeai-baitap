# 2. Cải tiến ứng dụng chat: Sau mỗi câu hỏi và trả lời, ta lưu vào array `messages` và tiếp tục gửi lên API để bot nhớ nội dung trò chuyện.
# Su dung Stream

from openai import OpenAI

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-xxxx',
)


def call_open_ai(messages): 
    return client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        n=1,
        max_tokens=100,
        stream=True
    )


def qna_bot():
    messages = [{"role": "system", "content": "You are a smart and friendly companion."}]

    while True:
        question = input("\n\nYou: ")
        if question.lower() in ["exit", "quit", "bye"]:
            print("Exited.")
            break

        messages.append({"role": "user", "content": question})

        bot_response = call_open_ai(messages)

        answer=""
        for chunk in bot_response:
            chunk_ans = chunk.choices[0].delta.content or ""
            answer += chunk_ans
            print(chunk_ans, end="")

        messages.append({"role": "assistant", "content": answer})



qna_bot()