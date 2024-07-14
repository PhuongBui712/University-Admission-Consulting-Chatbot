import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

interface Message {
  role: 'user' | 'ai';
  content: string;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <div className="flex-grow overflow-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <ChatMessage key={index} role={message.role} content={message.content} />
      ))}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-white text-gray-800 p-3 rounded-lg shadow">
            Thinking...
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};