import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { ChatSession, ChatMessage } from '../types';
import { glassCardClasses } from '../lib/utils';
import { Bot, Send, User, Settings, Search, FileText, Copy, Check, Sparkles, Trash2, Globe, Plus, RefreshCw, Download, Zap, X } from 'lucide-react';
import { useToast } from '../components/Toast';

import { useApp } from '../store/AppContext';

export default function ChatView() {
  const { toast } = useToast();
  const { activeWorkspace } = useApp();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<any | null>(null);

  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [modelConfig, setModelConfig] = useState('auto');
  const [temperature, setTemperature] = useState<number>(0.7);
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeSessionObj = sessions.find(s => s.id === activeSession);

  const handlePreloadModel = async () => {
    try {
      toast('Model Warmup', `Warming up ${modelConfig} in VRAM...`, 'info');
      const res = await fetch('/api/system/preload-model', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelConfig === 'auto' ? 'qwen2.5:7b' : modelConfig })
      });
      const data = await res.json();
      if (data.status === 'success') {
        toast('Model Warmup', `${modelConfig} loaded into VRAM! Ready for instant responses.`, 'success');
      } else {
        toast('Model Warmup', data.message || 'Failed to preload model.', 'warning');
      }
    } catch {
      toast('Model Warmup', 'VRAM Warmup triggered.', 'info');
    }
  };

  const handleExportTranscript = () => {
    if (messages.length === 0) {
      toast('Export Chat', 'No messages in transcript to export.', 'warning');
      return;
    }
    const lines = messages.map(m => `### ${m.role === 'user' ? 'User' : 'Uroboros AI'}\n\n${m.content}\n`);
    const blob = new Blob([lines.join('\n---\n\n')], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_transcript_${activeSessionObj?.id || 'session'}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast('Export Chat', 'Chat transcript downloaded as Markdown!', 'success');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  useEffect(() => {
    // Intelligent automatic background model preloading
    fetch('/api/system/preload-model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: modelConfig === 'auto' ? 'qwen2.5:7b' : modelConfig })
    }).catch(() => {});
  }, [modelConfig]);

  useEffect(() => {
    const controller = new AbortController();
    api.chatSessions().then(data => {
      if (controller.signal.aborted) return;
      setSessions(data || []);
      if (data && data.length > 0 && !activeSession) {
        setActiveSession(data[0].id);
        setMessages(data[0].messages || []);
      }
    }).catch(e => console.error('Failed to load chat sessions:', e));
    return () => controller.abort();
  }, [activeWorkspace]);

  const handleNewSession = async () => {
    try {
      const s = await api.createChatSession('New Conversation');
      setSessions(prev => [s, ...prev]);
      setActiveSession(s.id);
      setMessages([]);
      toast('Session Created', 'New RAG chat session initialized', 'success');
    } catch (e) {
      console.error('Failed to create session:', e);
      toast('Session Error', 'Could not create session', 'error');
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.deleteChatSession(id);
      setSessions(prev => prev.filter(s => s.id !== id));
      if (activeSession === id) {
        const remaining = sessions.filter(s => s.id !== id);
        if (remaining.length > 0) {
          setActiveSession(remaining[0].id);
          setMessages(remaining[0].messages || []);
        } else {
          setActiveSession(null);
          setMessages([]);
        }
      }
      toast('Session Deleted', 'Chat session removed', 'info');
    } catch (err) {
      console.error('Failed to delete session:', err);
      toast('Delete Error', 'Could not delete session', 'error');
    }
  };

  const handleClearMessages = () => {
    setMessages([]);
    toast('Chat Cleared', 'Conversation history cleared', 'info');
  };

  const copyMessageText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    toast('Copied Message', 'Text copied to clipboard', 'info');
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleSelectSession = (s: ChatSession) => {
    if (activeSession === s.id) return;
    abortRef.current?.abort();
    setActiveSession(s.id);
    setMessages(s.messages || []);
  };

  const handleSendPromptText = (promptText: string) => {
    setInput(promptText);
    executeSend(promptText);
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    executeSend(input);
  };

  const executeSend = async (textToSend: string) => {
    const trimmed = textToSend.trim();
    if (!trimmed || isStreaming) return;

    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: trimmed };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsStreaming(true);

    try {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      // Add placeholder assistant message
      const assistantMsgId = (Date.now() + 1).toString();
      setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '', sources: [] }]);

      const response = await api.ragStream(trimmed, activeSession ?? undefined, {
        signal: controller.signal,
        web_search: webSearchEnabled,
        temperature: !isNaN(temperature) ? temperature : 0.7,
        model: modelConfig
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let currentResponse = '';
      let gatheredSources: Array<{ title?: string; path?: string; url?: string; snippet?: string }> = [];
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (value) buffer += decoder.decode(value, { stream: !done });

        const lines = buffer.split('\n');
        buffer = done ? '' : (lines.pop() || '');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'token' && data.content) {
                currentResponse += data.content;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  const idx = newMsgs.findIndex(m => m.id === assistantMsgId);
                  if (idx !== -1) {
                    newMsgs[idx] = { ...newMsgs[idx], content: currentResponse, sources: gatheredSources };
                  }
                  return newMsgs;
                });
              } else if (data.type === 'sources' || data.type === 'citations') {
                const rawSources = data.sources || data.local_citations || data.web_sources || [];
                gatheredSources = rawSources.map((src: any) => ({
                  title: src.title || src.filename || src.path || 'Document Context',
                  path: src.path || src.filepath || '',
                  url: src.url || src.link || '',
                  snippet: src.snippet || src.text || src.citation || '',
                  confidence_score: src.confidence_score
                }));
                setMessages(prev => {
                  const newMsgs = [...prev];
                  const idx = newMsgs.findIndex(m => m.id === assistantMsgId);
                  if (idx !== -1) {
                    newMsgs[idx] = { ...newMsgs[idx], sources: gatheredSources };
                  }
                  return newMsgs;
                });
              } else if (data.type === 'done') {
                setMessages(prev => {
                  const newMsgs = [...prev];
                  const idx = newMsgs.findIndex(m => m.id === assistantMsgId);
                  if (idx !== -1) {
                    newMsgs[idx] = {
                      ...newMsgs[idx],
                      metrics: {
                        model: data.model,
                        tier: data.tier,
                        tokens_generated: data.tokens_generated,
                        tokens_per_sec: data.tokens_per_sec,
                        duration_sec: data.duration_sec
                      }
                    };
                  }
                  return newMsgs;
                });
              }
            } catch (err) {
              // Ignore malformed SSE chunk line
            }
          }
        }
        if (done) break;
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Chat stream error:', err);
        toast('Stream Error', 'Failed to complete RAG response stream', 'error');
      }
    } finally {
      setIsStreaming(false);
    }
  };

  const renderFormattedContent = (content: string, msgId: string, isCurrentlyStreaming: boolean = false) => {
    if (!content.includes('```')) {
      return (
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {content}
          {isCurrentlyStreaming && <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-500 animate-pulse align-middle rounded-sm" />}
        </p>
      );
    }

    const parts = content.split(/(```[\s\S]*?```)/g);
    return (
      <div className="space-y-3">
        {parts.map((part, index) => {
          if (part.startsWith('```') && part.endsWith('```')) {
            const match = part.match(/^```(\w+)?\n?([\s\S]*?)```$/);
            const lang = match ? match[1] || 'code' : 'code';
            const codeText = match ? match[2].trim() : part.slice(3, -3).trim();
            const codeBlockId = `${msgId}-code-${index}`;

            return (
              <div key={index} className="my-2 rounded-xl overflow-hidden border border-slate-700/50 bg-slate-900/90 text-slate-100 text-xs font-mono shadow-md">
                <div className="flex items-center justify-between px-3 py-1.5 bg-slate-800/80 border-b border-slate-700/50 text-slate-400 text-[11px]">
                  <span className="font-semibold uppercase tracking-wider text-indigo-400">{lang}</span>
                  <button
                    onClick={() => copyMessageText(codeBlockId, codeText)}
                    className="flex items-center gap-1 hover:text-slate-200 transition-colors px-2 py-0.5 rounded bg-white/5 hover:bg-white/10"
                  >
                    {copiedMsgId === codeBlockId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedMsgId === codeBlockId ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <pre className="p-3 overflow-x-auto whitespace-pre leading-relaxed">{codeText}</pre>
              </div>
            );
          }
          return part ? (
            <p key={index} className="text-sm leading-relaxed whitespace-pre-wrap">
              {part}
              {isCurrentlyStreaming && index === parts.length - 1 && (
                <span className="inline-block w-1.5 h-4 ml-1 bg-indigo-500 animate-pulse align-middle rounded-sm" />
              )}
            </p>
          ) : null;
        })}
      </div>
    );
  };

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <div className="w-72 border-r border-slate-200 dark:border-white/5 bg-slate-50/30 dark:bg-slate-900/30 flex flex-col">
        <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between">
          <h3 className="font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
            <Bot className="w-4 h-4 text-indigo-500" /> Chat Sessions
          </h3>
          <button
            onClick={handleNewSession}
            className="text-xs bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 px-2.5 py-1 rounded-lg hover:bg-indigo-500/30 transition-colors flex items-center gap-1 font-medium"
          >
            <Plus className="w-3.5 h-3.5" /> New
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">No active sessions. Click "New" to start.</div>
          ) : (
            sessions.map(s => (
              <div
                key={s.id}
                onClick={() => handleSelectSession(s)}
                className={`group w-full text-left px-3 py-2.5 rounded-lg transition-colors border flex items-center justify-between cursor-pointer ${
                  activeSession === s.id
                    ? 'bg-indigo-500/10 border-indigo-500/30 dark:border-indigo-500/20'
                    : 'hover:bg-slate-100 dark:hover:bg-white/5 border-transparent hover:border-slate-200 dark:hover:border-white/5'
                }`}
              >
                <div className="min-w-0 flex-1 pr-2">
                  <p className={`text-sm font-medium truncate ${activeSession === s.id ? 'text-indigo-700 dark:text-indigo-300' : 'text-slate-700 dark:text-slate-300'}`}>
                    {s.title || 'Conversation'}
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {new Date(s.updatedAt || Date.now()).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 rounded transition-all"
                  title="Delete Session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>

        {/* Model & Temperature Config Panel */}
        <div className="p-4 border-t border-slate-200 dark:border-white/5 bg-white/50 dark:bg-slate-950/50 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
              <Settings className="w-3.5 h-3.5 text-indigo-500" /> Model Config
            </span>
          </div>
          <select
            aria-label="Model Config"
            value={modelConfig}
            onChange={(e) => setModelConfig(e.target.value)}
            className="w-full bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-white/10 rounded-lg text-xs text-slate-900 dark:text-slate-200 p-2 outline-none focus:border-indigo-500/50"
          >
            <option value="auto">Auto (4-Tier Neural Router)</option>
            <option value="qwen2.5:7b">qwen2.5:7b (Master RAG)</option>
            <option value="qwen2.5-coder:14b">qwen2.5-coder:14b (Expert Coder)</option>
            <option value="qwen2.5-coder:7b">qwen2.5-coder:7b (Fast Coder)</option>
            <option value="qwen2.5:0.5b">qwen2.5:0.5b (Micro Speed)</option>
            <option value="phi4-mini:latest">phi4-mini:latest (128k Long Doc)</option>
          </select>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Temp:</span>
            <input
              type="range"
              aria-label="Temperature"
              min="0"
              max="1"
              step="0.1"
              value={!isNaN(temperature) ? temperature : 0.7}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="flex-1 accent-indigo-500 cursor-pointer"
            />
            <span className="text-xs font-mono text-slate-600 dark:text-slate-400 w-6 text-right">
              {!isNaN(temperature) ? temperature.toFixed(1) : '0.7'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-white/20 dark:bg-slate-950/20">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-white/5 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50 backdrop-blur-sm">
          <div className="flex flex-col">
            <h2 className="text-base font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-500" />
              {activeSessionObj?.title || 'Neuro RAG Chat Assistant'}
            </h2>
            <span className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {webSearchEnabled ? 'RAG + Web Search Active' : 'Vault RAG Active'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Model Selector Dropdown */}
            <select
              value={modelConfig}
              onChange={(e) => setModelConfig(e.target.value)}
              className="text-xs bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-white/10 text-slate-800 dark:text-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none cursor-pointer"
            >
              <option value="qwen2.5:7b">⚡ Qwen 2.5 7B (Local Ollama)</option>
              <option value="llama3:8b">🦙 Llama 3 8B (Local)</option>
              <option value="gpt-4o">🧠 GPT-4o (OpenAI)</option>
              <option value="claude-3-5-sonnet">🎭 Claude 3.5 Sonnet (Anthropic)</option>
            </select>

            <button
              onClick={() => setWebSearchEnabled(!webSearchEnabled)}
              className={`p-2 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition-all ${
                webSearchEnabled
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-sm shadow-indigo-500/30'
                  : 'bg-slate-100 dark:bg-white/5 border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
              title={webSearchEnabled ? 'Web Search Enabled (Grounding + Web)' : 'Web Search Disabled (Local Vault RAG)'}
            >
              <Search className="w-3.5 h-3.5" />
              <span>Web Search</span>
            </button>

            <button
              onClick={handlePreloadModel}
              className="p-2 text-amber-600 dark:text-amber-400 hover:text-amber-500 bg-amber-500/10 rounded-lg border border-amber-500/20 transition-colors flex items-center gap-1 text-xs font-medium"
              title="Preload Model into GPU VRAM for instant responses"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Warmup VRAM</span>
            </button>

            <button
              onClick={handleExportTranscript}
              className="p-2 text-slate-600 dark:text-slate-300 hover:text-indigo-500 bg-slate-100 dark:bg-white/5 hover:bg-indigo-500/10 rounded-lg border border-slate-300 dark:border-white/10 transition-colors flex items-center gap-1 text-xs"
              title="Export Chat Transcript (.md)"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
            </button>

            <button
              onClick={handleClearMessages}
              className="p-2 text-slate-500 hover:text-rose-500 bg-slate-100 dark:bg-white/5 hover:bg-rose-500/10 rounded-lg border border-slate-300 dark:border-white/10 transition-colors"
              title="Clear Messages"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-6">
                <Bot className="w-8 h-8 text-indigo-500" />
              </div>
              <h3 className="text-lg font-medium text-slate-800 dark:text-slate-200 mb-2">
                How can I assist your vault research today?
              </h3>
              <p className="text-xs text-slate-500 max-w-sm mb-8">
                Ask questions about your local knowledge base, discover semantic connections, or query live web search.
              </p>

              <div className="grid grid-cols-2 gap-3 w-full">
                <button
                  onClick={() => handleSendPromptText('Summarize the latest research document in the vault')}
                  className="text-left p-3.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-indigo-500/5 hover:border-indigo-500/30 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group"
                >
                  <span className="font-medium text-slate-900 dark:text-slate-200 group-hover:text-indigo-500 transition-colors">Summarize Research</span>
                  <span className="text-[11px] text-slate-500">Synthesize documents in local storage</span>
                </button>

                <button
                  onClick={() => handleSendPromptText("Find connections to 'quantum computing'") }
                  className="text-left p-3.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-indigo-500/5 hover:border-indigo-500/30 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group"
                >
                  <span className="font-medium text-slate-900 dark:text-slate-200 group-hover:text-indigo-500 transition-colors">Discover Connections</span>
                  <span className="text-[11px] text-slate-500">Explore multi-hop knowledge graph</span>
                </button>

                <button
                  onClick={() => handleSendPromptText('Explain vector ColBERT MaxSim reranking')}
                  className="text-left p-3.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-indigo-500/5 hover:border-indigo-500/30 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group"
                >
                  <span className="font-medium text-slate-900 dark:text-slate-200 group-hover:text-indigo-500 transition-colors">Explain Algorithms</span>
                  <span className="text-[11px] text-slate-500">Break down retrieval paradigms</span>
                </button>

                <button
                  onClick={() => handleSendPromptText('Search the web for recent accounting standards updates')}
                  className="text-left p-3.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-indigo-500/5 hover:border-indigo-500/30 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group"
                >
                  <span className="font-medium text-slate-900 dark:text-slate-200 group-hover:text-indigo-500 transition-colors">Web Grounding</span>
                  <span className="text-[11px] text-slate-500">Query live search with WebSearchFetcher</span>
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={msg.id} className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                    <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  </div>
                )}

                <div className={`group relative max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-sm' : `${glassCardClasses} rounded-tl-sm text-slate-900 dark:text-slate-200`}`}>
                  {/* Message Actions */}
                  <button
                    onClick={() => copyMessageText(msg.id, msg.content)}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-slate-200 bg-slate-800/40 rounded transition-all"
                    title="Copy Text"
                  >
                    {copiedMsgId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>

                  {/* Formatted Content */}
                  {renderFormattedContent(msg.content, msg.id, isStreaming && idx === messages.length - 1)}

                  {/* Performance Metrics */}
                  {msg.role === 'assistant' && msg.metrics && (
                    <div className="flex items-center gap-2 mt-2.5 pt-2 border-t border-slate-200/40 dark:border-white/5 text-[10px] text-slate-400 font-mono">
                      <span className="px-1.5 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 font-semibold uppercase tracking-wider">
                        {msg.metrics.tier || 'Master'}: {msg.metrics.model}
                      </span>
                      {msg.metrics.tokens_per_sec && <span>• {msg.metrics.tokens_per_sec} tok/s</span>}
                      {msg.metrics.duration_sec && <span>• {msg.metrics.duration_sec}s</span>}
                    </div>
                  )}

                  {/* Grounded Sources */}
                  {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-200/80 dark:border-white/10 space-y-1.5">
                      <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider block">Grounded Sources ({msg.sources.length}):</span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.sources.map((src, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => setSelectedCitation(src)}
                            className="inline-flex items-center gap-1 text-[11px] bg-slate-100 dark:bg-white/5 hover:bg-indigo-500/20 hover:border-indigo-500/30 px-2 py-1 rounded-md border border-slate-300 dark:border-white/10 text-cyan-700 dark:text-cyan-400 max-w-xs truncate transition-colors cursor-pointer"
                            title="Click to view full grounded excerpt"
                          >
                            {src.url ? <Globe className="w-3 h-3 flex-shrink-0 text-indigo-400" /> : <FileText className="w-3 h-3 flex-shrink-0" />}
                            <span className="truncate">{src.title || src.path || src.url}</span>
                          </button>
                        ))}
                      </div>
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

          {/* Streaming Indicator */}
          {isStreaming && (
            <div className="flex gap-3.5 justify-start">
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 border border-indigo-500/30">
                <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div className={`${glassCardClasses} rounded-2xl rounded-tl-sm p-4 flex items-center gap-2`}>
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse delay-75" />
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse delay-150" />
                <span className="text-xs text-slate-500 ml-1">Streaming RAG response...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-4 bg-slate-50/80 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200 dark:border-white/5">
          <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-end">
            <textarea
              className="w-full bg-slate-100/50 dark:bg-slate-800/50 border border-slate-300 dark:border-white/10 rounded-xl px-4 py-3 pr-12 text-slate-900 dark:text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 resize-none min-h-[52px] max-h-32 text-sm leading-relaxed"
              placeholder="Message Uroboros Knowledge Engine..."
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="absolute right-2 bottom-2 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700/50 disabled:text-slate-500 text-white rounded-lg transition-colors shadow-sm cursor-pointer"
              title="Send Message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-2 text-[11px] text-slate-500">
            Neuro Knowledge Engine v2.0 • Grounded Vault RAG + Web Grounding
          </div>
        </div>
      </div>

      {/* Citation Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className={`${glassCardClasses} w-full max-w-xl rounded-2xl p-6 shadow-2xl border border-slate-700/50 space-y-4 max-h-[80vh] flex flex-col`}>
            <div className="flex items-center justify-between border-b border-slate-700/50 pb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                <h3 className="text-sm font-semibold text-slate-100 truncate max-w-md">
                  {selectedCitation.title || selectedCitation.filename || 'Grounded Vault Context'}
                </h3>
              </div>
              <button
                onClick={() => setSelectedCitation(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="text-xs text-slate-400 font-mono break-all bg-slate-900/40 p-2 rounded-lg border border-white/5">
              {selectedCitation.path || selectedCitation.url || 'Internal Knowledge Base'}
            </div>
            <div className="flex-1 overflow-y-auto bg-slate-900/80 p-4 rounded-xl border border-slate-700/50 text-slate-200 text-xs font-mono leading-relaxed whitespace-pre-wrap">
              {selectedCitation.snippet || selectedCitation.citation || 'No preview text excerpt available for this source.'}
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => {
                  copyMessageText('cit', selectedCitation.snippet || selectedCitation.path || '');
                  toast('Copied', 'Citation excerpt copied to clipboard', 'info');
                }}
                className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Excerpt</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
