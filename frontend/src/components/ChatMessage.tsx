import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessageProps {
  role: 'user' | 'ai';
  content: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => (
  <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
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
  </div>
);

export default ChatMessage