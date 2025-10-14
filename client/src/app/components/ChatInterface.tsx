'use client';

import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { useRef, useEffect } from 'react';

export interface Message {
  sender: 'user' | 'assistant';
  text: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (messageText: string) => void;
}

export default function ChatInterface({ messages, isLoading, onSendMessage }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen flex-1">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
        <h1 className="text-xl font-bold text-gray-800">AI Personal Assistant</h1>
        <div className={`flex items-center space-x-2 ${isLoading ? 'animate-pulse' : ''}`}>
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <p className="text-sm text-gray-500">{isLoading ? 'Typing...' : 'Online'}</p>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-6 space-y-5 bg-gray-100">
        {messages.map((msg, index) => (
          <MessageBubble key={index} sender={msg.sender} text={msg.text} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  );
}