# 4. Dịch nguyên 1 file dài từ ngôn ngữ này sang ngôn ngữ khác.

#    1. Viết prompt để set giọng văn, v...v
#    2. Đọc từ file gốc, sau đó cắt ra thành từng phần để dịch vì LLM có context size có hạn
#    3. Sau khi dịch xong, gom kết quả lại, ghi vào file mới.

from openai import OpenAI

client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key='sk-proj-xxxx',
)

def generate_prompt(text, source_language, target_language):
    return (
        f"Translate the following government document from {source_language} to {target_language}. "
        "The translation should be accurate, clear, and maintain the original meaning and tone. "
        "Preserve the original formatting as much as possible. Use formal language appropriate for an official government document.\n\n"
        "===\n"
        f"{text}\n"
        "==="
    )

def translate_text(text, source_language, target_language):
    prompt = generate_prompt(text, source_language, target_language)
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        model="gpt-4o-mini"
    )
    
    return response.choices[0].message.content

def split_text(text, max_length=2000):
    parts = []
    while len(text) > max_length:
        split_index = text.rfind(' ', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(text[:split_index])
        text = text[split_index:].strip()
    parts.append(text) 
    return parts

def translate_text_file():
    source_language = "English"  
    target_language = "Vietnamese"

    # Đọc nội dung từ file
    with open("llm-api-4-input.txt", "r", encoding="utf-8") as file:
        content = file.read()

    print(content)
    
    # Tách nội dung thành các phần nhỏ
    text_parts = split_text(content, max_length=2000)
    
    translated_parts = []
    for part in text_parts:
        print(part)
        translated_part = translate_text(part, source_language, target_language)
        translated_parts.append(translated_part)
    
    # Ghi kết quả vào file mới
    with open("llm-api-4-output.txt", "w", encoding="utf-8") as file:
        for translated in translated_parts:
            file.write(translated + "\n")

    print("Translated done!!")

translate_text_file()