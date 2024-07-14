"use client"

import { useState } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

const genAI = new GoogleGenerativeAI(process.env.NEXT_PUBLIC_GEMINI_API_KEY!);
const model = genAI.getGenerativeModel({ model: "gemini-pro" });

interface Message {
  role: 'user' | 'ai';
  content: string;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = async (input: string) => {
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setIsLoading(true);
    setIsGenerating(true);

    try {
      const result = await model.generateContent(input);
      const response = await result.response;
      const text = response.text();
      
      setMessages(prev => [...prev, { role: 'ai', content: text }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, an error occurred.' }]);
    } finally {
      setIsLoading(false);
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-full flex flex-col">
      <MessageList messages={messages} isLoading={isLoading} />
      <div className="p-4 bg-white">
        <ChatInput onSubmit={handleSubmit} isGenerating={isGenerating} />
      </div>
    </div>
  );
};


export default ChatInterface