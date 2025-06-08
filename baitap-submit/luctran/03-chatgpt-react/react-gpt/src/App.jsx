import { useEffect, useState } from 'react'
import OpenAI from "openai";

function isBotMessage(chatMessage) {
  return chatMessage.role === "assistant";
}

function App() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const [apiKey, setApiKey] = useState(() => localStorage.getItem("openai_api_key") || "");
  const [inputKey, setInputKey] = useState("");


  const openai = new OpenAI({
    // KHUYẾN CÁO: Đừng bao giờ để key trong code như thế này
    // Nên lưu key ở server, hoặc để người dùng tự nhập key
    apiKey: apiKey,

    // Khi chạy ở browser, cần thêm option này
    dangerouslyAllowBrowser: true,
  });


  const handleSaveKey = () => {
    if (inputKey.startsWith("sk-")) {
      localStorage.setItem("openai_api_key", inputKey);
      setApiKey(inputKey);
    } else {
      alert("API key không hợp lệ.");
    }
  };


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

    const newHistory = [...chatHistory, userMessage, waitingBotMessage];
    setChatHistory(newHistory);
    saveChatHistoryToLocal(newHistory);

    // Gọi OpenAI API để lấy kết quả
    const chatCompletion = await openai.chat.completions.create({
      messages: [...chatHistory, userMessage],
      model: "gpt-4o-mini",
    });

    // Lấy tin nhắn của bot từ response, hiển thị cho người dùng
    const response = chatCompletion.choices[0].message.content;
    const botMessage = { role: "assistant", content: response };

    const updatedHistory = [...chatHistory, userMessage, botMessage];
    setChatHistory(updatedHistory);
    saveChatHistoryToLocal(updatedHistory); 
  };

  const saveChatHistoryToLocal = (history) => {
    localStorage.setItem("chat_history", JSON.stringify(history));
  };

  const clearChatHistory = () => {
    setChatHistory([]);
    saveChatHistoryToLocal([]);
  };

  useEffect(() => {
    const savedHistory = localStorage.getItem("chat_history");
    if (savedHistory) {
      setChatHistory(JSON.parse(savedHistory));
    }
  }, []);

  return (
    <div className="bg-gray-100 h-screen flex flex-col">
      <div className="container mx-auto p-4 flex flex-col h-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4">ChatUI với React + OpenAI</h1>

        {!apiKey ? (
          <div className="flex mb-5">
            {/* <h2 className="text-xl font-semibold mb-4 text-gray-800">🔐 Nhập OpenAI API Key</h2> */}
            <input
              type="password"
              placeholder="Enter your OpenAI Key: sk-..."
              className="flex-grow p-2 rounded-l border border-gray-300"
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
            />
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded-r bg-gray-500 hover:bg-gray-600"
              onClick={handleSaveKey}
            >
              Lưu Key
            </button>
          </div>
      ) : (
        <>
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

            <div className='text-right mb-2'>
              <button onClick={clearChatHistory} type="button" class="px-3 py-2 text-xs font-medium text-center text-white bg-gray-700 rounded-lg hover:bg-gray-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Delete chat history</button>
            </div>

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

        </>
      )}
      </div>
    </div>
  )
}

export default App
