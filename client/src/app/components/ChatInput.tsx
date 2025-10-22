'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import TextareaAutosize from 'react-textarea-autosize'; 

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-4 bg-gray-50 border-t border-gray-200"> 
      <div className="flex items-end space-x-3 bg-white rounded-xl border border-gray-300 p-2 shadow-sm"> 
        <TextareaAutosize
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask your assistant..."
          disabled={isLoading}
          rows={1}
          maxRows={5} 
          className="flex-1 bg-transparent p-2 border-none resize-none focus:outline-none focus:ring-0 text-sm text-gray-800 placeholder-gray-500" 
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()} 
          className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
            (isLoading || !input.trim())
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700' 
          }`}
        >
          
          <svg className="w-5 h-5 transform rotate-90" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10.894 2.553a1 1 0 00-1.789 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 16.571V11a1 1 0 112 0v5.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
        </button>
      </div>
    </div>
  );
}