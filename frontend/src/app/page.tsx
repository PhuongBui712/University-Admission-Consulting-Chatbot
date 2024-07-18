import ChatInterface from '../components/ChatInterface';

export default function Home() {
  return (
    <div className="flex flex-col h-full bg-white">
      <main className="flex-grow overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  );
}