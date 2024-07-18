import React, { useState, useRef, useEffect } from 'react';
import component_styles from '../app/component.module.css'

interface ChatInputProps {
  onSubmit: (message: string) => void;
  isGenerating: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSubmit, isGenerating }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;
    onSubmit(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
      <form onSubmit={handleSubmit} className={`w-full p-[0.15rem] ${component_styles['gradient-border-wrapper']} rounded-[30px] $ bg-blue-300`}>
        <div className="relative flex items-center bg-gray-100 rounded-[30px] p-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-grow px-3 py-2 bg-transparent text-gray-700 focus:outline-none resize-none overflow-hidden"
            placeholder="Send a message..."
            rows={1}
            style={{ minHeight: '24px', maxHeight: '120px' }}
          />
          <button 
            type="submit" 
            className={`p-2 rounded-full ${
              isGenerating || !input.trim() 
                ? 'text-gray-400 cursor-not-allowed' 
                : 'bg-black text-white hover:bg-gray-800'
            }`}
            disabled={isGenerating || !input.trim()}
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </div>
      </form>
  );
};