import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { ChatSession, ChatMessage } from '../types';
import { glassCardClasses } from '../lib/utils';
import { Bot, Send, User, Settings, Search, FileText } from 'lucide-react';

export default function ChatView() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [modelConfig, setModelConfig] = useState('Llama-3-8B-Instruct.gguf');

  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    // ponytail: using simple abort flag since api might not take signal
    api.chatSessions().then(data => {
      if (controller.signal.aborted) return;
      setSessions(data || []);
      if (data && data.length > 0 && !activeSession) {
        setActiveSession(data[0].id);
        setMessages(data[0].messages || []);
      }
    }).catch(e => console.error('Failed to load sessions:', e));
    return () => controller.abort();
  }, []);

  const handleNewSession = async () => {
    try {
      const s = await api.createChatSession('New Conversation');
      setSessions(prev => [s, ...prev]);
      setActiveSession(s.id);
      setMessages([]);
    } catch (e) {
      console.error('Failed to create session:', e);
    }
  };

  const handleSelectSession = (s: ChatSession) => {
    abortRef.current?.abort();
    setActiveSession(s.id);
    setMessages(s.messages || []);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsStreaming(true);

    try {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      // Add empty assistant message to append to
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content: '' }]);
      
      const response = await api.ragStream(userMsg.content, activeSession ?? undefined, { signal: controller.signal });
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let currentResponse = '';
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        
        // ponytail: buffer stream chunks
        if (value) buffer += decoder.decode(value, { stream: !done });
        
        const lines = buffer.split('\n');
        buffer = done ? '' : (lines.pop() || '');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'token') {
                currentResponse += data.content;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  const last = newMsgs[newMsgs.length - 1];
                  if (last.role === 'assistant') {
                    newMsgs[newMsgs.length - 1] = { ...last, content: currentResponse };
                  }
                  return newMsgs;
                });
              } else if (data.type === 'sources' && data.sources?.length) {
                 // handle sources if we wanted to
              } else if (data.type === 'done') {
                 // Finished
              }
            } catch (err) {}
          }
        }
        if (done) break;
      }
    } catch (err) {
      console.error('Chat stream error:', err);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-72 border-r border-slate-200 dark:border-white/5 bg-slate-50/30 dark:bg-slate-900/30 flex flex-col">
        <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between">
          <h3 className="font-medium text-slate-900 dark:text-slate-200">Sessions</h3>
          <button onClick={handleNewSession} className="text-xs bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 px-2 py-1 rounded hover:bg-indigo-500/30 transition-colors">New +</button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {sessions.map(s => (
            <button key={s.id} onClick={() => handleSelectSession(s)} className={`w-full text-left px-3 py-3 rounded-lg transition-colors border ${activeSession === s.id ? 'bg-indigo-500/10 border-indigo-500/20' : 'hover:bg-slate-100 dark:bg-white/5 border-transparent hover:border-slate-200 dark:hover:border-white/5'}`}>
              <p className={`text-sm font-medium truncate ${activeSession === s.id ? 'text-indigo-700 dark:text-indigo-300' : 'text-slate-700 dark:text-slate-300'}`}>{s.title || 'Conversation'}</p>
              <p className="text-xs text-slate-500 mt-1">{new Date(s.updatedAt || Date.now()).toLocaleDateString()}</p>
            </button>
          ))}
        </div>
        
        {/* Model Config Panel */}
        <div className="p-4 border-t border-slate-200 dark:border-white/5 bg-white/50 dark:bg-slate-950/50 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400 flex items-center gap-1.5"><Settings className="w-3 h-3" /> Model Config</span>
          </div>
          <select aria-label="Model Config" value={modelConfig} onChange={(e) => setModelConfig(e.target.value)} className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-white/10 rounded-lg text-sm text-slate-900 dark:text-slate-200 p-2 outline-none">
            <option>Llama-3-8B-Instruct.gguf</option>
            <option>Mistral-7B-v0.2.gguf</option>
          </select>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Temp:</span>
            <input type="range" aria-label="Temperature" min="0" max="1" step="0.1" defaultValue="0.7" className="flex-1 accent-indigo-500" />
            <span className="text-xs text-slate-600 dark:text-slate-400">0.7</span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white/20 dark:bg-slate-950/20">
        <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between">
          <div className="flex flex-col">
            <h2 className="text-lg font-medium text-slate-900 dark:text-slate-200">Quantum Physics Explainer</h2>
            <span className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400"/> RAG Active</span>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-1.5 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-slate-200 bg-slate-100 dark:bg-white/5 rounded-lg border border-slate-300 dark:border-white/10 transition-colors" title="Web Search Enabled"><Search className="w-4 h-4" /></button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto">
              <Bot className="w-16 h-16 text-slate-700 mb-6" />
              <h3 className="text-xl font-medium text-slate-700 dark:text-slate-300 mb-2">How can I help you?</h3>
              <p className="text-sm text-slate-500 mb-8">Ask a question about your knowledge graph, analyze documents, or run web searches.</p>
              
              <div className="grid grid-cols-2 gap-3 w-full">
                <button className="text-left p-3 rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100 dark:bg-white/5 transition-colors text-sm text-slate-700 dark:text-slate-300">Summarize the latest research PDF</button>
                <button className="text-left p-3 rounded-xl border border-slate-200 dark:border-white/5 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100 dark:bg-white/5 transition-colors text-sm text-slate-700 dark:text-slate-300">Find connections to 'quantum field'</button>
              </div>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                    <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  </div>
                )}
                
                <div className={`max-w-[75%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-sm' : `${glassCardClasses} rounded-tl-sm text-slate-900 dark:text-slate-200`}`}>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                  
                  {msg.role === 'assistant' && (
                    <div className="mt-3 pt-3 border-t border-slate-300 dark:border-white/10 flex items-center gap-2">
                      <span className="text-xs text-slate-500">Sources:</span>
                      <span className="flex items-center gap-1 text-xs bg-slate-100 dark:bg-white/5 px-2 py-1 rounded border border-slate-300 dark:border-white/10 text-cyan-600 dark:text-cyan-400"><FileText className="w-3 h-3"/> research.pdf</span>
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 border border-slate-300 dark:border-white/10">
                    <User className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                  </div>
                )}
              </div>
            ))
          )}
          {isStreaming && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div className={`${glassCardClasses} rounded-2xl rounded-tl-sm p-4 flex items-center gap-2`}>
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse delay-75" />
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse delay-150" />
              </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-slate-50/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-white/5">
          <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-end">
            <textarea
              className="w-full bg-slate-100/50 dark:bg-slate-800/50 border border-slate-300 dark:border-white/10 rounded-xl px-4 py-3 pr-12 text-slate-900 dark:text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 resize-none min-h-[52px] max-h-32"
              placeholder="Message Uroboros..."
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e); } }}
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isStreaming}
              className="absolute right-2 bottom-2 p-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-2 text-xs text-slate-500">AI can make mistakes. Verify important information.</div>
        </div>
      </div>
    </div>
  );
}
