'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const AssistantAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center mr-3 flex-shrink-0 shadow-sm"> 
    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  </div>
);

const UserAvatar = () => (
  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center ml-3 flex-shrink-0 shadow-sm">
    <span className="text-xs font-semibold text-white">You</span> 
  </div>
);

interface MessageBubbleProps {
  sender: 'user' | 'assistant';
  text: string;
}

export default function MessageBubble({ sender, text }: MessageBubbleProps) {
  const isUser = sender === 'user';

  return (
    <div className={`flex items-start my-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && <AssistantAvatar />}
      
      <div 
        className={`max-w-[85%] md:max-w-2xl lg:max-w-3xl px-4 py-3 rounded-2xl shadow-sm border ${ 
          isUser 
            ? 'bg-blue-600 text-white border-blue-600 rounded-br-none ml-2'
            : 'bg-white text-gray-800 border-gray-100 rounded-bl-none mr-2' 
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{text}</p>
        ) : (
          <div className="text-sm leading-relaxed space-y-2 overflow-hidden break-words text-gray-800">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => (
                  <h1 className="text-lg font-bold text-gray-900 mt-3 mb-2 pb-1 border-b border-gray-200">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-base font-bold text-gray-900 mt-3 mb-1.5 pb-0.5 border-b border-gray-100">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm font-semibold text-gray-900 mt-2 mb-1">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0 leading-relaxed text-gray-700">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside space-y-1 my-2 pl-2 text-gray-700">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside space-y-1 my-2 pl-2 text-gray-700">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed">
                    {children}
                  </li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900">
                    {children}
                  </strong>
                ),
                em: ({ children }) => (
                  <em className="italic text-gray-800">
                    {children}
                  </em>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-indigo-500 bg-indigo-50/50 pl-3 py-1 my-2 italic text-gray-700 rounded-r">
                    {children}
                  </blockquote>
                ),
                code: ({ className, children, ...props }) => {
                  const isInline = !className && !String(children).includes('\n');
                  if (isInline) {
                    return (
                      <code className="bg-gray-100 text-pink-600 font-mono text-xs px-1.5 py-0.5 rounded border border-gray-200" {...props}>
                        {children}
                      </code>
                    );
                  }
                  return (
                    <div className="my-2 rounded-lg overflow-hidden border border-gray-700 bg-gray-900 text-gray-100">
                      <pre className="p-3 overflow-x-auto text-xs font-mono">
                        <code {...props}>{children}</code>
                      </pre>
                    </div>
                  );
                },
                table: ({ children }) => (
                  <div className="overflow-x-auto my-3 border border-gray-200 rounded-lg shadow-xs">
                    <table className="min-w-full divide-y divide-gray-200 text-xs text-left">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-gray-50 font-semibold text-gray-700">
                    {children}
                  </thead>
                ),
                tbody: ({ children }) => (
                  <tbody className="divide-y divide-gray-100 bg-white">
                    {children}
                  </tbody>
                ),
                tr: ({ children }) => (
                  <tr className="hover:bg-gray-50/80 transition-colors">
                    {children}
                  </tr>
                ),
                th: ({ children }) => (
                  <th className="px-3 py-2 font-semibold text-gray-800 border-b border-gray-200">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-3 py-2 text-gray-700">
                    {children}
                  </td>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-800 underline font-medium"
                  >
                    {children}
                  </a>
                ),
                hr: () => <hr className="my-3 border-gray-200" />
              }}
            >
              {text}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {isUser && <UserAvatar />}
    </div>
  );
}