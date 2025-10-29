'use client';

import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Sidebar, { Thread } from '@/app/components/SideBar';
import ChatInterface, { Message } from '@/app/components/ChatInterface';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [threads, setThreads] = useState<Thread[]>([]);

  const loadThreads = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/threads');
      const data = await response.json();
      setThreads(data.threads || []);
    } catch (error) {
      console.error("Failed to fetch threads:", error);
    }
  };

  useEffect(() => {
    loadThreads(); 
  }, []);

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
    
    const newThread: Thread = { id: newThreadId, title: "New Chat" };
    setThreads((prevThreads) => [newThread, ...prevThreads]);

    handleRenameThread(newThreadId, "New Chat");
  };
  
  const handleRenameThread = async (threadId: string, newTitle: string) => {
    setThreads(threads.map(t => t.id === threadId ? { ...t, title: newTitle } : t));
    try {
      await fetch(`http://127.0.0.1:5001/api/threads/${threadId}/title`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle }),
      });
    } catch (error) {
      console.error("Failed to rename thread:", error);
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
      const newTitle = messageText.substring(0, 25) + (messageText.length > 25 ? '...' : '');
      const newThread: Thread = { id: newThreadId, title: newTitle };

      setThreads((prev) => [newThread, ...prev]);
      if (newThread.title) {
        handleRenameThread(newThreadId, newThread.title);
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

  const handleDeleteThread = async (threadId: string) => {
    setThreads((prevThreads) => prevThreads.filter(t => t.id !== threadId));

    if (currentThreadId === threadId) {
      setCurrentThreadId(null); 
      setMessages([]);        
    }

    try {
      const response = await fetch(`http://127.0.0.1:5001/api/threads/${threadId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        console.error("Failed to delete thread on server, rolling back UI.");
        loadThreads();
      }
      
    } catch (error) {
      console.error("Error deleting thread:", error);
      loadThreads();
    }
  };

  return (
    <main className="flex h-screen justify-center items-center"
    style={{ backgroundColor: '#f3f4f7' }}
    >
      <div
      className="flex h-[90vh] w-[90vw] max-w-6xl shadow-xl rounded-lg overflow-hidden"
      style={{ backgroundColor: 'white' }}
      >
        <Sidebar 
          threads={threads}
          activeThreadId={currentThreadId}
          onNewChat={startNewChat}
          onSelectThread={handleSelectThread}
          onRenameThread={handleRenameThread}
          onDeleteThread={handleDeleteThread}
        />
        <ChatInterface 
          messages={messages} 
          isLoading={isLoading} 
          onSendMessage={handleSendMessage} 
        />
        </div>
    </main>
  );
}