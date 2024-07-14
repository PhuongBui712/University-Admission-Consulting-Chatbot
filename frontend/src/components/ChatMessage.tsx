import React from 'react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import user_icon from '../../public/images/user.jpg'
import ai_icon from '../../public/images/logo.png'


interface ChatMessageProps {
  role: 'user' | 'ai';
  content: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  const userImage = '/path-to-user-image.jpg'; // Replace with the actual path to the user image
  const aiImage = '/path-to-ai-image.jpg'; // Replace with the actual path to the AI image

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
          <p>{content}</p>
        ) : (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            className="markdown-body"
          >
            {content}
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