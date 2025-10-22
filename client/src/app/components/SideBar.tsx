'use client';

import { useState, KeyboardEvent, MouseEvent} from 'react';

export interface Thread {
  id: string;
  title: string | null;
}

interface SidebarProps {
  threads: Thread[];
  activeThreadId: string | null;
  onNewChat: () => void;
  onSelectThread: (threadId: string) => void;
  onRenameThread: (threadId: string, newTitle: string) => Promise<void>;
}

export default function Sidebar({ threads, activeThreadId, onNewChat, onSelectThread, onRenameThread }: SidebarProps) {
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [tempTitle, setTempTitle] = useState('');

  const handleRename = (thread: Thread) => {
    setEditingThreadId(thread.id);
    setTempTitle(thread.title || thread.id);
  };

  const handleSaveRename = async (threadId: string) => {
    if (tempTitle.trim() && tempTitle !== (threads.find(t => t.id === threadId)?.title || threadId)) {
      await onRenameThread(threadId, tempTitle.trim());
    }
    setEditingThreadId(null);
  };
  
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>, threadId: string) => {
    if (e.key === 'Enter') {
      handleSaveRename(threadId);
    } else if (e.key === 'Escape') {
      setEditingThreadId(null);
    }
  };

  return (
    <div className="w-64 text-white flex flex-col"
    style={{ backgroundColor: '#1f2937' }}
    >
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onNewChat}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200"
        >
          + New Chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        <h2 className="p-4 text-sm font-semibold text-gray-400">Previous Chats</h2>
        <ul>
          {threads.map((thread) => (
            <li key={thread.id} className="px-2 py-1 group relative">
              {editingThreadId === thread.id ? (
                <input
                  type="text"
                  value={tempTitle}
                  onChange={(e) => setTempTitle(e.target.value)}
                  onKeyDown={(e) => handleKeyDown(e, thread.id)}
                  onBlur={() => handleSaveRename(thread.id)}
                  className="w-full p-2 rounded bg-gray-600 text-white text-sm outline-none"
                  autoFocus
                />
              ) : (
                <div
                  onClick={() => onSelectThread(thread.id)}
                  className={`w-full text-left p-2 rounded truncate text-sm flex justify-between items-center cursor-pointer transition-colors duration-150 ${
                    activeThreadId === thread.id ? 'bg-gray-600 font-medium' : 'hover:bg-gray-700'
                  }`}
                >
                  <span className="text-gray-300"> 
                    {thread.title || thread.id.substring(0, 12) + '...'}
                  </span>

                  <button onClick={(e : MouseEvent<HTMLButtonElement>) => {
                    e.stopPropagation();
                    handleRename(thread)
                    }}
                    className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white p-1 transition-opacity duration-150">
                    ✏️
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      <div className="p-4 border-t border-gray-700">
        <p className="text-xs text-gray-500">AI Personal Assistant v1.0</p>
      </div>
    </div>
  );
}