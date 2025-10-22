'use client';


const AssistantAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center mr-3 flex-shrink-0"> 
    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
  </div>
);

const UserAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center ml-3 flex-shrink-0">
    <span className="text-xs font-semibold text-white">BA</span> 
  </div>
);

interface MessageBubbleProps {
  sender: 'user' | 'assistant';
  text: string;
}

export default function MessageBubble({ sender, text }: MessageBubbleProps) {
  const isUser = sender === 'user';

  return (
    <div className={`flex items-end ${isUser ? 'justify-end' : 'justify-start'}`}>
      
      {!isUser && <AssistantAvatar />}
      
      <div 
        className={`max-w-xs md:max-w-md lg:max-w-xl px-4 py-3 rounded-2xl shadow ${ 
          isUser 
            ? 'bg-blue-600 text-white rounded-br-none ml-3'
            : 'bg-white text-gray-800 rounded-bl-none mr-3' 
        }`}
      >
        <p className="text-sm break-words">{text}</p>
      </div>

      {isUser && <UserAvatar />}
      
    </div>
  );
}