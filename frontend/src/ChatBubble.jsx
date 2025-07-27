const ChatBubble = ({ text, sender }) => {
  const isUser = sender === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} my-1`}>
      <div
        className={`max-w-[70%] px-4 py-2 rounded-2xl text-sm shadow-md ${
          isUser
            ? "bg-gray-500 text-white rounded-br-none"
            : "bg-red-500 text-white rounded-bl-none"
        }`}
      >
        {text}
      </div>
    </div>
  );
};

export default ChatBubble;
