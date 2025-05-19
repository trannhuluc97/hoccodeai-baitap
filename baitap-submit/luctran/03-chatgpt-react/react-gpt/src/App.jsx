import { useState } from 'react'
import OpenAI from "openai";

function isBotMessage(chatMessage) {
  return chatMessage.role === "assistant";
}

const openai = new OpenAI({
  // KHUYẾN CÁO: Đừng bao giờ để key trong code như thế này
  // Nên lưu key ở server, hoặc để người dùng tự nhập key
  apiKey: "sk-proj-xxxx",

  // Khi chạy ở browser, cần thêm option này
  dangerouslyAllowBrowser: true,
});


function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const submitForm = async (e) => {
    e.preventDefault();

    // Clear message ban đầu
    setMessage("");

    // Thêm tin nhắn người dùng và tin nhắn của bot vào danh sách
    const userMessage = { role: "user", content: message };
    const waitingBotMessage = {
      role: "assistant",
      content: "Vui lòng chờ bot trả lời...",
    };
    setChatHistory([...chatHistory, userMessage, waitingBotMessage]);

    // Gọi OpenAI API để lấy kết quả
    const chatCompletion = await openai.chat.completions.create({
      messages: [...chatHistory, userMessage],
      model: "gpt-4o-mini",
    });

    // Lấy tin nhắn của bot từ response, hiển thị cho người dùng
    const response = chatCompletion.choices[0].message.content;
    const botMessage = { role: "assistant", content: response };
    setChatHistory([...chatHistory, userMessage, botMessage]);
  };

  return (
    <div className="bg-gray-100 h-screen flex flex-col">
      <div className="container mx-auto p-4 flex flex-col h-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4">ChatUI với React + OpenAI</h1>

        <form className="flex" onSubmit={submitForm}>
          <input
            type="text"
            placeholder="Tin nhắn của bạn..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-grow p-2 rounded-l border border-gray-300"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
          >
            Gửi tin nhắn
          </button>
        </form>

        <div className="flex-grow overflow-y-auto mt-4 bg-white rounded shadow p-4">
          {chatHistory.map((chatMessage, i) => (
            <div
              key={i}
              className={`mb-2 ${
                isBotMessage(chatMessage) ? "" : "text-right"
              }`}
            >
              <p className="text-gray-600 text-sm">
                {isBotMessage(chatMessage) ? "Bot" : "User"}
              </p>
              <p
                className={`p-2 rounded-lg inline-block ${
                  isBotMessage(chatMessage) ? "bg-blue-100" : "bg-gray-100"
                }`}
              >
                {chatMessage.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App
