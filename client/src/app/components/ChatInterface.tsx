'use client';

import { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (messageText: string) => {
    const userMessage: Message = { sender: 'user', text: messageText };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, thread_id: 'berky-web-session' }),
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      const assistantResponse: Message = { sender: 'assistant', text: data.reply };
      setMessages((prev) => [...prev, assistantResponse]);
    } catch (error) {
      console.error("Error fetching from backend:", error);
      const errorResponse: Message = { sender: 'assistant', text: "Sorry, I'm having trouble connecting." };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-100 shadow-xl">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => (
          <MessageBubble key={index} sender={msg.sender} text={msg.text} />
        ))}
        {isLoading && (
          <div className="flex justify-start">
             <div className="max-w-xs p-3 rounded-lg text-gray-600 bg-gray-200">
               <p className="animate-pulse">Assistant is thinking...</p>
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}