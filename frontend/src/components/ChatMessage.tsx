import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import user_icon from '../../public/images/user.jpg'
import ai_icon from '../../public/images/logo.png'

interface ChatMessageProps {
  role: 'user' | 'ai';
  content: string;
  isStreaming?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content, isStreaming }) => {
  const [displayedContent, setDisplayedContent] = useState('');

  useEffect(() => {
    if (role === 'ai' && isStreaming) {
      setDisplayedContent(content);
    } else {
      setDisplayedContent(content);
    }
  }, [content, role, isStreaming]);

  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
      {role === 'ai' && (
        <div className="flex-shrink-0 mr-2">
          <Image src={ai_icon} alt="AI" className="w-8 h-8 rounded-full" />
        </div>
      )}
      <div className={`max-w-[80%] p-3 rounded-lg ${
        role === 'user' 
          ? 'bg-blue-500 text-white' 
          : 'bg-white text-gray-800 shadow'
      }`}>
        {role === 'user' ? (
          <p>{displayedContent}</p>
        ) : (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            className="markdown-body"
          >
            {displayedContent}
          </ReactMarkdown>
        )}
      </div>
      {role === 'user' && (
        <div className="flex-shrink-0 ml-2">
          <Image src={user_icon} alt="User" className="w-8 h-8 rounded-full" />
        </div>
      )}
    </div>
  );
}


export default ChatMessage;