'use client';

interface SidebarProps {
  threads: string[];
  activeThreadId: string | null;
  onNewChat: () => void;
  onSelectThread: (threadId: string) => void;
}

export default function Sidebar({ threads, activeThreadId, onNewChat, onSelectThread }: SidebarProps) {
  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col">
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
          {threads.map((threadId) => (
            <li key={threadId} className="px-2 py-1">
              <button
                onClick={() => onSelectThread(threadId)}
                className={`w-full text-left p-2 rounded truncate text-sm ${
                  activeThreadId === threadId
                    ? 'bg-gray-600'
                    : 'hover:bg-gray-700'
                }`}
              >
                {threadId}
              </button>
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