'use client';

interface MessageBubbleProps {
  sender: 'user' | 'assistant';
  text: string;
}

export default function MessageBubble({ sender, text }: MessageBubbleProps) {
  const isUser = sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs md:max-w-md lg:max-w-2xl px-4 py-3 rounded-lg text-white shadow-md ${isUser ? 'bg-blue-600' : 'bg-gray-700'}`}>
        <p className="text-sm">{text}</p>
      </div>
    </div>
  );
}