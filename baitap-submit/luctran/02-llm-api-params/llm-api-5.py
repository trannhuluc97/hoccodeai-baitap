# 5. Dùng bot để... giải bài tập lập trình. Viết ứng dụng console cho phép bạn đưa câu hỏi vào, bot sẽ viết code Python/JavaScript. 
# Sau đó, viết code lưu đáp án vào file `final.py` và chạy thử. (Dùng Python sẽ dễ hơn JavaScript nhé!)

def generate_code(question):
    prompt = f"Write a Python code snippet to perform: {question} result only show code"
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5, 
        model="gemma2-9b-it",
    )
    
    return response.choices[0].message.content

def generate_code_snippet():
    print("Input your question for code generation (type 'exit' to quit):")
    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            print("Exiting code generation mode.")
            break
        
        code = generate_code(question)
        print("Code result:\n", code)
        
        # Ghi kết quả vào file final.py
        with open("final.py", "a", encoding="utf-8") as f:
            f.write(f"# Question: {question}\n")
            f.write(code + "\n\n")

generate_code_snippet()