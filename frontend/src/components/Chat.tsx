import React, { useState, useEffect } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';

interface Message {
  content: string;
  from: string;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const apiKey = process.env.API_KEY;
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!apiKey) {
      console.error('Missing API_KEY in .env');
      return;
    }

    const genAI = new GoogleGenerativeAI(apiKey);
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

    const handleUserMessage = async (message: string) => {
      const response = await model.generateContent(message)
      setMessages([...messages, { content: message, from: 'User' }, { content: response.response.text(), from: 'AI' }]);
      setMessage(''); // Clear input field after sending
    };

    // Simulate initial greeting from AI
    handleUserMessage('Hello!');
  }, []);

  const handleSendMessage = () => {
    if (message.trim()) {
      handleUserMessage(message);
    }
  };

  return (
    <div className="chat-container">
      <h2>Chat with AI</h2>
      <ul>
        {messages.map((message) => (
          <li key={message.content}>
            {message.from === 'User' ? (
              <span className="user-message">{message.content}</span>
            ) : (
              <span className="ai-message">{message.content}</span>
            )}
          </li>
        ))}
      </ul>
      <form onSubmit={(e) => e.preventDefault()}>
        <input
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ color: 'black' }}
        />
        <button type="submit" onClick={handleSendMessage}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
