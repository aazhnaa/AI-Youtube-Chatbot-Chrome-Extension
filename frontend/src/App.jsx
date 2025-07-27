import { useEffect, useState } from "react";
import ChatBubble from "./ChatBubble";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [videoId, setVideoId] = useState(null);

  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url;
      const id = new URL(url).searchParams.get("v");
      if (url.includes("youtube.com/watch") && id) setVideoId(id);
    });
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, video_id: videoId }),
      });

      const data = await res.json();
      setMessages([...newMessages, { sender: "bot", text: data.response }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { sender: "bot", text: "Something went wrong with the chatbot." },
      ]);
      console.log("Error:", err);
    }
  };

  return (
    <div className="p-4 w-[400px] h-[500px] rounded-2xl flex flex-col justify-center items-center bg-gray-900">
      <div className="text-xl font-bold text-white">YouTube AI ChatBot</div>
      {videoId ? (
        <>
          <p className="text-white mb-2">Ask anything related to the video</p>
          <div className="flex-1 w-full overflow-y-auto mb-2">
            {messages.map((msg, idx) => (
              <ChatBubble key={idx} sender={msg.sender} text={msg.text} />
            ))}
          </div>
          <div className="flex gap-1 w-full">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask AI about the video..."
              className="flex-1 px-2 py-1 text-white border rounded-lg text-sm bg-gray-800"
            />
            <button
              onClick={handleSend}
              className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm"
            >
              Send
            </button>
          </div>
        </>
      ) : (
        <div className="text-red-500 mt-4 text-center">
          ❌ This extension only works on YouTube video pages.
        </div>
      )}
    </div>
  );
}

export default App;
