"use client"

import { useState, useEffect } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { RemoteRunnable } from '@langchain/core/runnables/remote';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

const genAI = new GoogleGenerativeAI(process.env.NEXT_PUBLIC_GEMINI_API_KEY!);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash-latest" });
const remoteChain = new RemoteRunnable({ url: 'http://localhost:8000/hcmus-ai-assistant/'})

interface Message {
  role: 'user' | 'ai';
  content: string;
  isStreaming?: boolean;
}

const GENERATION_DELAY = 500;

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = async (input: string) => {
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setIsGenerating(true);

    try {
      // const result = await model.generateContentStream(input);
      const result = await remoteChain.stream({
        chat_history: [],
        text: input,
        type: ''
      });
      console.log(result)
      
      let isFirstChunk = true;
      let aiMessage = { role: 'ai' as const, content: '', isStreaming: true };
      setMessages(prev => [...prev, aiMessage]);
      
      // for await (const chunk of result.stream) {
      //   await new Promise(resolve => setTimeout(resolve, GENERATION_DELAY));
      //   console.log(chunk)
      //   const chunkText = chunk.text();
      //   if (isFirstChunk) {
      //     aiMessage.content = chunkText;
      //     isFirstChunk = false;
      //   } else {
      //     aiMessage.content += chunkText;
      //   }
      //   setMessages(prev => [...prev]);
      // }

      for await (const chunk of result) {
        console.log(chunk)
        await new Promise(resolve => setTimeout(resolve, GENERATION_DELAY));
        const chunkText = chunk;
        if (isFirstChunk) {
          aiMessage.content = chunkText;
          isFirstChunk = false;
        } else {
          aiMessage.content += chunkText;
        }
        setMessages(prev => [...prev]);
      }
      
      aiMessage.isStreaming = false;
      setMessages(prev => [...prev]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, an error occurred.' }]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-full flex-col max-w-4xl mx-auto">
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} />
      </div>
      <div className="relative z-10 p-4 bg-white">
        <ChatInput onSubmit={handleSubmit} isGenerating={isGenerating} />
      </div>
    </div>
  );
};

export default ChatInterface;