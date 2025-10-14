'use client';

import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from '@/app/components/SideBar';
import ChatInterface, { Message } from '@/app/components/ChatInterface';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [threads, setThreads] = useState<string[]>([]);

  useEffect(() => {
    const fetchThreads = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5001/api/threads');
        const data = await response.json();
        setThreads(data.threads || []);
      } catch (error) {
        console.error("Failed to fetch threads:", error);
      }
    };
    fetchThreads();
  }, []);

  const startNewChat = () => {
    const newThreadId = uuidv4();
    setMessages([]);
    setCurrentThreadId(newThreadId);
    if (!threads.includes(newThreadId)) {
      setThreads((prev) => [newThreadId, ...prev]);
    }
  };

  const handleSelectThread = async (threadId: string) => {
    setIsLoading(true);
    setCurrentThreadId(threadId);
    try {
      const response = await fetch(`http://127.0.0.1:5001/api/history/${threadId}`);
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error("Failed to fetch history:", error);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    let threadIdToUse = currentThreadId;

    if (!threadIdToUse) {
      const newThreadId = uuidv4();
      setCurrentThreadId(newThreadId);
      if (!threads.includes(newThreadId)) {
        setThreads((prev) => [newThreadId, ...prev]);
      }
      threadIdToUse = newThreadId;
    }

    const userMessage: Message = { sender: 'user', text: messageText };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, thread_id: threadIdToUse }),
      });
      const data = await response.json();
      const assistantResponse: Message = { sender: 'assistant', text: data.reply };
      setMessages((prev) => [...prev, assistantResponse]);
    } catch (error) {
      const errorResponse: Message = { sender: 'assistant', text: "Sorry, I'm having trouble connecting." };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex h-screen">
      <Sidebar 
        threads={threads}
        activeThreadId={currentThreadId}
        onNewChat={startNewChat}
        onSelectThread={handleSelectThread}
      />
      <ChatInterface 
        messages={messages} 
        isLoading={isLoading} 
        onSendMessage={handleSendMessage} 
      />
    </main>
  );
}