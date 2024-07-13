'use client';

import { useState, useRef, useEffect } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const genAI = new GoogleGenerativeAI(process.env.NEXT_PUBLIC_GEMINI_API_KEY!);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

export default function Home() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

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
      setInput('');
    }
  };

  return (
    <main className="flex-grow overflow-hidden">
      <div className="w-full mx-auto h-full flex flex-col">
        <div className="flex-grow overflow-auto p-10 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white text-gray-800 shadow'
              }`}>
                {message.role === 'user' ? (
                  <p>{message.content}</p>
                ) : (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    className="markdown-body"
                  >
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
            </div>
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

        <div className="p-4 shadow-md">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-grow border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
              placeholder="Type your message..."
            />
            <button 
              type="submit" 
              className={`px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                isGenerating 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}
              disabled={isGenerating}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}