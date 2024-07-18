import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

interface Message {
  role: 'user' | 'ai';
  content: string;
  isStreaming?: boolean;
}

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div 
      ref={containerRef} 
      className="h-full overflow-y-auto p-4 space-y-4"
    >
      {messages.map((message, index) => (
        <ChatMessage key={index} role={message.role} content={message.content} isStreaming={message.isStreaming} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};