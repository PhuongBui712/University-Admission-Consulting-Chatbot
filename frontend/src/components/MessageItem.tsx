import React from 'react';

interface MessageItemProps {
  role: 'user' | 'ai';
  content: string;
}

const MessageItem: React.FC<MessageItemProps> = ({ role, content }) => {
  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] ${role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'} rounded-lg p-3`}>
        {role === 'ai' && (
          <div className="flex items-center mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span className="font-bold">AI</span>
          </div>
        )}
        <p>{content}</p>
      </div>
    </div>
  );
};

export default MessageItem;