import { useLocation } from "react-router-dom";
import { useState, useRef, useEffect } from "react";
import styles from "./Chat.module.css";

function Chat() {
  const location = useLocation();
  const initialMessage = location.state?.userMessage || "";
  const persona = localStorage.getItem("persona"); // ✅ 선택된 페르소나 가져오기

  const personaEmojis = {
    doctor: "👨‍⚕️",
    herbalist: "🌿",
    trainer: "💪",
  };

  const [messages, setMessages] = useState(
    initialMessage
      ? [
          { sender: "user", text: initialMessage },
          { sender: "bot", text: "..." },
        ]
      : []
  );
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ 서버 호출 함수
  const fetchAnswer = async (userInput) => {
    try {
      const res = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userInput, persona }),
      });

      const data = await res.json();

      // ✅ 페르소나 이모지 붙여서 출력
      const prefix = personaEmojis[persona] || "🤖";
      const responseText = `${prefix} ${data.answer}`;

      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          sender: "bot",
          text: responseText,
        };
        return newMessages;
      });
    } catch (err) {
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          sender: "bot",
          text: "⚠️ 서버 오류",
        };
        return newMessages;
      });
    }
  };

  // ✅ Chat 진입 시 초기 메시지 처리
  useEffect(() => {
    if (initialMessage) {
      fetchAnswer(initialMessage);
    }
  }, [initialMessage]);

  // ✅ 입력창에서 엔터 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [
      ...prev,
      { sender: "user", text: input },
      { sender: "bot", text: "..." },
    ]);

    const userInput = input;
    setInput("");
    fetchAnswer(userInput);
  };

  return (
    <div className={styles.container}>
      <img src="/logo.png" alt="logo" className={styles.logo} />

      <div className={styles.chatWindow}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.message} ${
              msg.sender === "user" ? styles.user : styles.bot
            }`}
          >
            <p>{msg.text}</p>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <form className={styles.inputBox} onSubmit={handleSubmit}>
        <input
          placeholder="질문을 입력하세요..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">
          <img src="/search.png" alt="send" />
        </button>
      </form>
    </div>
  );
}

export default Chat;
