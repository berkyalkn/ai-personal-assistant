'use client';

import { useState, FormEvent, useRef, useEffect } from 'react';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    
    setIsLoading(true);
    setInput('');

    setTimeout(() => {
      const assistantResponse: Message = {
        sender: 'assistant',
        text: `This is a simulated reply to: "${userMessage.text}"`,
      };
      setMessages((prevMessages) => [...prevMessages, assistantResponse]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs md:max-w-md p-3 rounded-lg text-white ${msg.sender === 'user' ? 'bg-blue-500' : 'bg-gray-700'}`}>
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs md:max-w-md p-3 rounded-lg text-white bg-gray-700">
              <p className="animate-pulse">Assistant is thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-white border-t">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your assistant..."
            disabled={isLoading}
            className="flex-1 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-md disabled:bg-blue-300"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}