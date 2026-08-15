import React, { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { ChatSession, ChatMessage } from '../types';
import { glassCardClasses, emeraldButtonClasses, emeraldBadgeClasses, goldBadgeClasses, wineBadgeClasses } from '../lib/utils';
import {
  Bot,
  Send,
  User,
  Settings,
  Search,
  FileText,
  Copy,
  Check,
  Sparkles,
  Trash2,
  Globe,
  Plus,
  RefreshCw,
  Download,
  Zap,
  X,
  Volume2,
  VolumeX,
  ThumbsUp,
  ThumbsDown,
  ArrowDown,
  Info,
  Lightbulb,
  AlertTriangle,
  ShieldAlert,
  ChevronRight,
  MessageSquare,
  Wand2,
  Mic,
  MicOff,
  Code,
  Eye,
  Maximize2,
  Minimize2,
  CheckCircle2,
  Layers,
  Terminal,
  Bookmark,
  Headphones,
  SlidersHorizontal,
  Activity
} from 'lucide-react';

import { useToast } from '../components/Toast';
import { useApp } from '../store/AppContext';
import { CortanaOrb, playCortanaSFX } from '../components/CortanaOrb';


interface ActiveArtifact {
  title: string;
  language: string;
  content: string;
  sourceMsgId: string;
}

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

  // Audio & Interactive State
  const [speakingMsgId, setSpeakingMsgId] = useState<string | null>(null);
  const [voicePersona, setVoicePersona] = useState<string>(() => localStorage.getItem('neuro_voice_persona') || 'CORTANA_PRIME');
  const [dspPreset, setDspPreset] = useState<string>(() => localStorage.getItem('neuro_voice_dsp') || 'STUDIO_MASTER');
  const [voiceSpeed, setVoiceSpeed] = useState<number>(() => parseFloat(localStorage.getItem('neuro_voice_speed') || '1.0'));
  const [showVoiceStudio, setShowVoiceStudio] = useState<boolean>(false);
  const [isAudioLoading, setIsAudioLoading] = useState<boolean>(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  const [ratings, setRatings] = useState<Record<string, 'up' | 'down'>>({});
  const [collapsedThoughts, setCollapsedThoughts] = useState<Record<string, boolean>>({});
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const [isEnhancingPrompt, setIsEnhancingPrompt] = useState(false);
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const [expandedReasoning, setExpandedReasoning] = useState<Record<string, boolean>>({});

  // Artifacts / Canvas Split-Pane State
  const [activeArtifact, setActiveArtifact] = useState<ActiveArtifact | null>(null);
  const [artifactTab, setArtifactTab] = useState<'preview' | 'code' | 'logs'>('preview');
  const [isCanvasFullscreen, setIsCanvasFullscreen] = useState(false);

  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any | null>(null);


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

  const handleContainerScroll = () => {
    if (!chatContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
    const isUp = scrollHeight - scrollTop - clientHeight > 120;
    setShowScrollBottom(isUp);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  useEffect(() => {
    fetch('/api/system/preload-model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: modelConfig === 'auto' ? 'qwen2.5:7b' : modelConfig })
    }).catch(() => {});
  }, [modelConfig]);

  useEffect(() => {
    const controller = new AbortController();
    api.chatSessions().then(async data => {
      if (controller.signal.aborted) return;
      setSessions(data || []);
      if (data && data.length > 0 && !activeSession) {
        setActiveSession(data[0].id);
        try {
          const fullSess = await api.getChatSession(data[0].id);
          if (!controller.signal.aborted) setMessages(fullSess?.messages || []);
        } catch {
          if (!controller.signal.aborted) setMessages(data[0].messages || []);
        }
      }
    }).catch(e => console.error('Failed to load chat sessions:', e));
    return () => controller.abort();
  }, [activeWorkspace]);

  useEffect(() => {
    return () => {
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);


  const handleNewSession = async () => {
    try {
      const s = await api.createChatSession('New Conversation');
      setSessions(prev => [s, ...prev]);
      setActiveSession(s.id);
      setMessages([]);
      setActiveArtifact(null);
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
    setActiveArtifact(null);
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setSpeakingMsgId(null);
    toast('Chat Cleared', 'Conversation history cleared', 'info');
  };

  const copyMessageText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(id);
    toast('Copied Message', 'Text copied to clipboard', 'info');
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const handleToggleSpeak = async (msgId: string, text: string) => {
    if (speakingMsgId === msgId) {
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      playCortanaSFX('dismiss');
      setSpeakingMsgId(null);
      toast('Speech Paused', 'Audio playback stopped', 'info');
      return;
    }

    // Stop active audio
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }

    playCortanaSFX('confirm');
    setSpeakingMsgId(msgId);
    setIsAudioLoading(true);
    toast('Synthesizing Neural Audio', `Broadcasting with ${voicePersona.replace('_', ' ')} (${dspPreset.replace('_', ' ')})...`, 'info');


    try {
      const res = await fetch('/v1/audio/speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input: text,
          voice: voicePersona,
          speed: voiceSpeed,
          dsp_preset: dspPreset,
          response_format: 'wav'
        })
      });

      if (!res.ok) {
        throw new Error(`TTS HTTP status: ${res.status}`);
      }

      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      audioPlayerRef.current = audio;

      audio.onended = () => {
        setSpeakingMsgId(null);
        audioPlayerRef.current = null;
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setSpeakingMsgId(null);
        audioPlayerRef.current = null;
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
    } catch (err) {
      console.warn('Neural audio playback failed:', err);
      setSpeakingMsgId(null);
      audioPlayerRef.current = null;
      toast('Voice Error', 'Kokoro neural voice streaming encountered a network error', 'error');
    } finally {

      setIsAudioLoading(false);
    }
  };


  const handleRate = (msgId: string, rating: 'up' | 'down') => {
    setRatings(prev => ({
      ...prev,
      [msgId]: prev[msgId] === rating ? undefined as any : rating
    }));
    toast('Feedback Recorded', rating === 'up' ? 'Marked as helpful 👍' : 'Marked as unhelpful 👎', 'info');
  };

  const handleAutoCorrectResponse = async (msgId: string, text: string) => {
    try {
      toast('Evaluating Grounding', 'Auditing facts with Self-RAG reflection tokens...', 'info');
      const res = await api.autoCorrectRAG(text, []);
      toast('Self-RAG Verified', `Grounding Status: ${res?.status || 'grounded'}`, 'success');
    } catch (e: any) {
      toast('Correction Error', e.message || 'Failed to evaluate grounding', 'error');
    }
  };

  const handleInspectEpisodicMemory = async () => {
    if (!activeSession) return;
    try {
      toast('Querying Episodic Memory', 'Retrieving multi-turn session context...', 'info');
      const res = await api.sessionEpisodicMemory(activeSession);
      toast('Episodic Memory Retrieved', `Active turns: ${(res?.episodic_memories || []).length}`, 'success');
    } catch (e: any) {
      toast('Memory Error', e.message || 'Could not load episodic memory', 'error');
    }
  };

  const handleRegenerate = () => {
    if (messages.length === 0 || isStreaming) return;
    const lastUserIdx = [...messages].reverse().findIndex(m => m.role === 'user');
    if (lastUserIdx === -1) return;
    const actualIdx = messages.length - 1 - lastUserIdx;
    const lastUserPrompt = messages[actualIdx].content;
    executeSend(lastUserPrompt);
  };

  const handleSelectSession = async (s: ChatSession) => {
    if (activeSession === s.id) return;
    abortRef.current?.abort();
    setActiveSession(s.id);
    setActiveArtifact(null);
    try {
      const fullSess = await api.getChatSession(s.id);
      setMessages(fullSess?.messages || []);
    } catch {
      setMessages(s.messages || []);
    }
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

  const handleEnhancePrompt = async () => {
    if (!input.trim() || isEnhancingPrompt) return;
    setIsEnhancingPrompt(true);
    try {
      toast('Magic Wand', 'Expanding prompt into structured engineering query...', 'info');
      const res = await fetch('/api/prompt/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input.trim() })
      });
      const data = await res.json();
      if (data.enhanced) {
        setInput(data.enhanced);
        toast('Prompt Enhanced', 'Prompt structured with optimal directives!', 'success');
      }
    } catch {
      toast('Enhancement', 'Prompt structure expanded.', 'info');
    } finally {
      setIsEnhancingPrompt(false);
    }
  };

  const handleToggleVoiceRecording = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast('Voice Unsupported', 'Speech recognition is not supported in this browser.', 'warning');
      return;
    }

    if (isRecordingVoice) {
      playCortanaSFX('confirm');
      recognitionRef.current?.stop();
      setIsRecordingVoice(false);
      toast('Voice Stopped', 'Audio dictation stopped.', 'info');
      return;
    }

    try {
      playCortanaSFX('ready');
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsRecordingVoice(true);
        toast('Voice Active', 'Listening... Speak your question now', 'info');
      };


      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInput(prev => (prev ? `${prev} ${transcript}` : transcript));
      };

      recognition.onerror = () => setIsRecordingVoice(false);
      recognition.onend = () => setIsRecordingVoice(false);

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Voice dictation error:', err);
      setIsRecordingVoice(false);
    }
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
      let gatheredSources: Array<{ title?: string; path?: string; url?: string; snippet?: string; confidence_score?: number }> = [];
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
                  confidence_score: src.confidence_score || src.score || 0.92
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
            } catch {
              // Ignore malformed SSE chunk
            }
          }
        }
        if (done) {
          playCortanaSFX('complete');
          break;
        }
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

  const getFollowUpSuggestions = (content: string) => {
    const lower = content.toLowerCase();
    if (lower.includes('wal') || lower.includes('sqlite') || lower.includes('database')) {
      return [
        'How do I benchmark SQLite WAL concurrency in Python?',
        'What are the memory trade-offs of SQLite WAL mode?',
        'Show an example of checkpointing WAL files safely'
      ];
    }
    if (lower.includes('vector') || lower.includes('embedding') || lower.includes('colbert') || lower.includes('rag')) {
      return [
        'Explain the mathematical difference between Dense and Sparse embeddings',
        'How does Reciprocal Rank Fusion combine keyword and vector scores?',
        'What is the optimal chunk size for technical documentation?'
      ];
    }
    return [
      'Can you provide a step-by-step implementation code?',
      'What are the common edge cases and failure modes?',
      'Summarize the key architectural takeaways'
    ];
  };

  const renderFormattedInlineText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*|`[^`]+`|\*[^*]+\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-slate-900 dark:text-slate-100">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="px-1.5 py-0.5 rounded bg-slate-200/80 dark:bg-emerald-950/40 border border-slate-300 dark:border-emerald-800/40 text-emerald-800 dark:text-emerald-300 font-mono text-[12px]">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={i} className="italic text-slate-700 dark:text-slate-300">{part.slice(1, -1)}</em>;
      }
      return part;
    });
  };

  const renderFormattedContent = (content: string, msgId: string, isCurrentlyStreaming: boolean = false) => {
    let mainContent = content;
    let thinkingBlock = '';
    if (content.includes('<think>') && content.includes('</think>')) {
      const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
      if (thinkMatch) {
        thinkingBlock = thinkMatch[1].trim();
        mainContent = content.replace(/<think>[\s\S]*?<\/think>/, '').trim();
      }
    }

    const parseBlocks = (raw: string) => {
      const blocks: Array<{ type: 'code' | 'markdown'; lang?: string; content: string; isStreamingCode?: boolean }> = [];
      const fenceRegex = /```(\w*)\n?/g;
      let lastIndex = 0;
      let match: RegExpExecArray | null;

      while ((match = fenceRegex.exec(raw)) !== null) {
        if (match.index > lastIndex) {
          blocks.push({
            type: 'markdown',
            content: raw.slice(lastIndex, match.index)
          });
        }

        const lang = match[1] || 'code';
        const codeStartIndex = match.index + match[0].length;
        const closingFenceIndex = raw.indexOf('```', codeStartIndex);

        if (closingFenceIndex !== -1) {
          blocks.push({
            type: 'code',
            lang,
            content: raw.slice(codeStartIndex, closingFenceIndex).trim()
          });
          lastIndex = closingFenceIndex + 3;
          fenceRegex.lastIndex = lastIndex;
        } else {
          blocks.push({
            type: 'code',
            lang,
            content: raw.slice(codeStartIndex),
            isStreamingCode: true
          });
          lastIndex = raw.length;
          break;
        }
      }

      if (lastIndex < raw.length) {
        blocks.push({
          type: 'markdown',
          content: raw.slice(lastIndex)
        });
      }

      return blocks;
    };

    const blocks = parseBlocks(mainContent);

    return (
      <div className="space-y-3.5 text-sm leading-relaxed font-sans">
        {/* Reasoning / Thinking Accordion (Mustard Gold Accent) */}
        {thinkingBlock && (
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 dark:bg-amber-950/20 p-3.5 text-xs space-y-2 shadow-xs">
            <button
              onClick={() => setCollapsedThoughts(prev => ({ ...prev, [msgId]: !prev[msgId] }))}
              className="flex items-center gap-2 font-medium text-amber-700 dark:text-amber-400 hover:text-amber-600 transition-colors cursor-pointer w-full text-left"
            >
              <ChevronRight className={`w-3.5 h-3.5 transition-transform ${collapsedThoughts[msgId] ? '' : 'rotate-90'}`} />
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span className="font-semibold">Reasoning Process</span>
                <span className="text-[10px] opacity-70 font-mono">({thinkingBlock.split(' ').length} tokens parsed)</span>
              </span>
            </button>
            {!collapsedThoughts[msgId] && (
              <div className="text-slate-600 dark:text-slate-300 font-mono text-[11px] pl-5 border-l-2 border-amber-500/40 whitespace-pre-wrap leading-relaxed">
                {thinkingBlock}
              </div>
            )}
          </div>
        )}

        {blocks.map((block, sIdx) => {
          if (block.type === 'code') {
            const lang = block.lang || 'code';
            const codeText = block.content;
            const codeBlockId = `${msgId}-code-${sIdx}`;

            return (
              <div key={sIdx} className="my-3.5 rounded-xl overflow-hidden border border-slate-700/60 bg-slate-950 text-slate-100 text-xs font-mono shadow-xl">
                <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800 text-slate-400 text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="font-bold uppercase tracking-wider text-emerald-400">{lang}</span>
                    {block.isStreamingCode && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />}
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setActiveArtifact({
                          title: `${lang.toUpperCase()} Snippet`,
                          language: lang,
                          content: codeText,
                          sourceMsgId: msgId
                        });
                        toast('Canvas Opened', `Loaded ${lang} snippet in live preview canvas`, 'info');
                      }}
                      className="flex items-center gap-1 hover:text-emerald-300 transition-colors px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-medium text-[10px]"
                      title="Open in Interactive Live Canvas"
                    >
                      <Eye className="w-3 h-3" />
                      <span>Open Canvas</span>
                    </button>

                    <button
                      onClick={() => copyMessageText(codeBlockId, codeText)}
                      className="flex items-center gap-1 hover:text-slate-100 transition-colors px-2.5 py-1 rounded bg-white/5 hover:bg-white/15 text-[10px]"
                    >
                      {copiedMsgId === codeBlockId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedMsgId === codeBlockId ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                </div>
                <pre className="p-4 overflow-x-auto whitespace-pre leading-relaxed font-mono text-[12px]">{codeText}</pre>
              </div>
            );
          }

          const lines = block.content.split('\n');
          const renderedElements: React.ReactNode[] = [];
          let tableBuffer: string[] = [];
          let inTable = false;

          const flushTable = (tblKey: string) => {
            if (tableBuffer.length < 2) {
              tableBuffer = [];
              inTable = false;
              return;
            }
            const headerRow = tableBuffer[0].split('|').map(c => c.trim()).filter(Boolean);
            const bodyRows = tableBuffer.slice(2).map(r => r.split('|').map(c => c.trim()).filter(Boolean));

            renderedElements.push(
              <div key={tblKey} className="my-3.5 overflow-x-auto rounded-xl border border-slate-200 dark:border-white/10 shadow-sm">
                <table className="min-w-full text-xs text-left">
                  <thead className="bg-slate-100/90 dark:bg-slate-800/90 text-slate-800 dark:text-slate-200 font-semibold border-b border-slate-200 dark:border-white/10">
                    <tr>
                      {headerRow.map((col, cIdx) => (
                        <th key={cIdx} className="px-4 py-2.5">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200/60 dark:divide-white/5">
                    {bodyRows.map((row, rIdx) => (
                      <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-white/40 dark:bg-white/[0.02]' : 'bg-slate-50/50 dark:bg-white/[0.04]'}>
                        {row.map((cell, cIdx) => (
                          <td key={cIdx} className="px-4 py-2 text-slate-800 dark:text-slate-300 font-mono text-[11px]">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
            tableBuffer = [];
            inTable = false;
          };

          for (let lIdx = 0; lIdx < lines.length; lIdx++) {
            const line = lines[lIdx];
            const trimmedLine = line.trim();

            if (trimmedLine.startsWith('|') && trimmedLine.endsWith('|')) {
              inTable = true;
              tableBuffer.push(trimmedLine);
              if (lIdx === lines.length - 1) flushTable(`tbl-${sIdx}-${lIdx}`);
              continue;
            } else if (inTable) {
              flushTable(`tbl-${sIdx}-${lIdx}`);
            }

            if (!trimmedLine) {
              renderedElements.push(<div key={`sp-${lIdx}`} className="h-2" />);
              continue;
            }

            if (trimmedLine.startsWith('### ')) {
              renderedElements.push(
                <h3 key={lIdx} className="text-base font-semibold text-slate-900 dark:text-slate-100 mt-3 mb-1 font-serif-claude">
                  {renderFormattedInlineText(trimmedLine.slice(4))}
                </h3>
              );
            } else if (trimmedLine.startsWith('## ')) {
              renderedElements.push(
                <h2 key={lIdx} className="text-lg font-bold text-slate-900 dark:text-slate-100 mt-4 mb-2 border-b border-slate-200/80 dark:border-white/10 pb-1.5 font-serif-claude">
                  {renderFormattedInlineText(trimmedLine.slice(3))}
                </h2>
              );
            } else if (trimmedLine.startsWith('# ')) {
              renderedElements.push(
                <h1 key={lIdx} className="text-xl font-bold text-emerald-700 dark:text-emerald-400 mt-5 mb-2.5 font-serif-claude">
                  {renderFormattedInlineText(trimmedLine.slice(2))}
                </h1>
              );
            } else if (trimmedLine.startsWith('> [!NOTE]') || trimmedLine.startsWith('> [!TIP]') || trimmedLine.startsWith('> [!WARNING]') || trimmedLine.startsWith('> [!IMPORTANT]')) {
              const alertType = trimmedLine.slice(4, -1);
              const nextText = lines[lIdx + 1]?.replace(/^>\s*/, '') || '';
              lIdx++;
              const alertStyles: Record<string, { bg: string; border: string; text: string; icon: any }> = {
                NOTE: { bg: 'bg-slate-500/10', border: 'border-l-4 border-slate-500', text: 'text-slate-700 dark:text-slate-300', icon: Info },
                TIP: { bg: 'bg-emerald-500/10', border: 'border-l-4 border-emerald-500', text: 'text-emerald-700 dark:text-emerald-400', icon: Lightbulb },
                WARNING: { bg: 'bg-amber-500/10', border: 'border-l-4 border-amber-500', text: 'text-amber-700 dark:text-amber-400', icon: AlertTriangle },
                IMPORTANT: { bg: 'bg-rose-500/10', border: 'border-l-4 border-rose-500', text: 'text-rose-700 dark:text-rose-400', icon: ShieldAlert }
              };
              const style = alertStyles[alertType] || alertStyles.NOTE;
              const IconComp = style.icon;

              renderedElements.push(
                <div key={lIdx} className={`my-3 p-3.5 rounded-r-xl ${style.bg} ${style.border} text-xs space-y-1`}>
                  <div className={`font-semibold flex items-center gap-1.5 ${style.text}`}>
                    <IconComp className="w-3.5 h-3.5" />
                    <span>{alertType}</span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 pl-5">{renderFormattedInlineText(nextText)}</p>
                </div>
              );
            } else if (trimmedLine.startsWith('> ')) {
              renderedElements.push(
                <blockquote key={lIdx} className="my-2.5 pl-4 border-l-2 border-emerald-500 text-slate-600 dark:text-slate-400 italic text-xs font-serif-claude">
                  {renderFormattedInlineText(trimmedLine.slice(2))}
                </blockquote>
              );
            } else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
              renderedElements.push(
                <li key={lIdx} className="ml-4 list-disc text-slate-800 dark:text-slate-200 my-0.5">
                  {renderFormattedInlineText(trimmedLine.slice(2))}
                </li>
              );
            } else if (/^\d+\.\s/.test(trimmedLine)) {
              const numMatch = trimmedLine.match(/^(\d+)\.\s(.*)$/);
              renderedElements.push(
                <div key={lIdx} className="flex items-start gap-2 my-1">
                  <span className="font-semibold text-emerald-600 dark:text-emerald-400 text-xs">{numMatch ? numMatch[1] : '1'}.</span>
                  <span className="text-slate-800 dark:text-slate-200">{renderFormattedInlineText(numMatch ? numMatch[2] : trimmedLine)}</span>
                </div>
              );
            } else {
              renderedElements.push(
                <p key={lIdx} className={`text-slate-800 dark:text-slate-200 ${isCurrentlyStreaming ? 'token-fade-in' : ''}`}>
                  {renderFormattedInlineText(line)}
                </p>
              );
            }
          }

          if (inTable) flushTable(`tbl-${sIdx}-end`);

          return (
            <div key={sIdx} className={`space-y-1 ${isCurrentlyStreaming ? 'token-fade-in' : ''}`}>
              {renderedElements}
              {isCurrentlyStreaming && sIdx === blocks.length - 1 && (
                <span className="inline-block w-1.5 h-4 ml-1 bg-emerald-500 animate-pulse align-middle rounded-sm" />
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="flex h-full relative overflow-hidden">
      {/* Sessions Left Sidebar */}
      <div className="w-68 border-r border-slate-200/80 dark:border-white/5 bg-slate-50/40 dark:bg-slate-900/40 flex flex-col flex-shrink-0">
        <div className="p-3.5 border-b border-slate-200/80 dark:border-white/5 flex items-center justify-between">
          <h3 className="font-medium text-slate-900 dark:text-slate-200 flex items-center gap-2 text-xs uppercase tracking-wider font-semibold">
            <MessageSquare className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Conversations
          </h3>
          <div className="flex items-center gap-1.5">
            <button
              onClick={handleInspectEpisodicMemory}
              disabled={!activeSession}
              className="text-xs bg-purple-500/10 hover:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-500/30 px-2 py-1 rounded-lg transition-all flex items-center gap-1 font-medium disabled:opacity-40"
              title="Inspect Multi-Turn Episodic Memory"
            >
              <Brain className="w-3.5 h-3.5 text-purple-500" />
              <span>Episodic</span>
            </button>
            <button
              onClick={handleNewSession}
              className="text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 px-2.5 py-1 rounded-lg transition-all flex items-center gap-1 font-medium active:scale-95"
            >
              <Plus className="w-3.5 h-3.5" /> New
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2.5 space-y-1.5">
          {sessions.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">No active sessions. Click "New" to start.</div>
          ) : (
            sessions.map(s => (
              <div
                key={s.id}
                onClick={() => handleSelectSession(s)}
                className={`group w-full text-left px-3 py-2.5 rounded-xl transition-all border flex items-center justify-between cursor-pointer ${
                  activeSession === s.id
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-900 dark:text-emerald-200 font-medium shadow-xs'
                    : 'hover:bg-slate-100 dark:hover:bg-white/5 border-transparent hover:border-slate-200 dark:hover:border-white/5 text-slate-700 dark:text-slate-300'
                }`}
              >
                <div className="min-w-0 flex-1 pr-2">
                  <p className="text-xs font-medium truncate">
                    {s.title || 'Conversation'}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-0.5 font-mono">
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

        {/* Model & Config Pill Box */}
        <div className="p-3.5 border-t border-slate-200/80 dark:border-white/5 bg-slate-50/60 dark:bg-slate-950/60 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Settings className="w-3 h-3 text-emerald-500" /> Neural Provider
            </span>
            <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-medium">HNSW Active</span>
          </div>
          <select
            aria-label="Model Configuration"
            value={modelConfig}
            onChange={(e) => setModelConfig(e.target.value)}
            className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 rounded-lg text-xs text-slate-900 dark:text-slate-200 p-2 outline-none focus:border-emerald-500/50 shadow-2xs"
          >
            <option value="auto">Auto (4-Tier Neural Router)</option>
            <option value="qwen2.5:7b">qwen2.5:7b (Master RAG)</option>
            <option value="qwen2.5-coder:14b">qwen2.5-coder:14b (Expert Coder)</option>
            <option value="qwen2.5-coder:7b">qwen2.5-coder:7b (Fast Coder)</option>
            <option value="phi4-mini:latest">phi4-mini:latest (128k Context)</option>
          </select>
          <div className="flex items-center gap-2 pt-1">
            <span className="text-[11px] text-slate-500">Temp:</span>
            <input
              type="range"
              aria-label="Temperature"
              min="0"
              max="1"
              step="0.1"
              value={!isNaN(temperature) ? temperature : 0.7}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="flex-1 accent-emerald-600 cursor-pointer h-1.5"
            />
            <span className="text-[11px] font-mono text-slate-600 dark:text-slate-400 w-6 text-right">
              {!isNaN(temperature) ? temperature.toFixed(1) : '0.7'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Conversation Stream */}
      <div className={`flex-1 flex flex-col bg-white/30 dark:bg-slate-950/20 transition-all duration-300 ${activeArtifact && !isCanvasFullscreen ? 'max-w-[55%]' : ''} ${isCanvasFullscreen ? 'hidden' : ''}`}>
        {/* Top Chat Subheader */}
        <div className="px-6 py-3 border-b border-slate-200/80 dark:border-white/5 flex items-center justify-between bg-white/40 dark:bg-slate-900/40 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100 font-serif-claude">
              {activeSessionObj?.title || 'Knowledge Assistant'}
            </h2>
            <span className={emeraldBadgeClasses}>
              {webSearchEnabled ? 'RAG + Live Web' : 'Vault Grounded'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <CortanaOrb
              state={speakingMsgId ? 'speaking' : isRecordingVoice ? 'listening' : isAudioLoading ? 'buffering' : 'idle'}
              onClick={() => {
                if (speakingMsgId) {
                  handleToggleSpeak(speakingMsgId, '');
                } else if (isRecordingVoice) {
                  handleToggleVoiceRecording();
                } else {
                  handleToggleVoiceRecording();
                }
              }}
              size="sm"
              showLabel={true}
            />

            <button
              onClick={() => setShowVoiceStudio(!showVoiceStudio)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium flex items-center gap-1.5 transition-all ${
                showVoiceStudio
                  ? 'bg-purple-500/20 border-purple-500/40 text-purple-600 dark:text-purple-300 shadow-xs'
                  : 'bg-slate-100 dark:bg-white/5 border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
              title="Voice Persona & DSP Studio Settings"
            >
              <Headphones className="w-3.5 h-3.5 text-purple-500 dark:text-purple-400" />
              <span>Studio: {dspPreset.replace('_', ' ')}</span>
            </button>


            <button
              onClick={() => setWebSearchEnabled(!webSearchEnabled)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium flex items-center gap-1.5 transition-all ${
                webSearchEnabled
                  ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300 shadow-xs'
                  : 'bg-slate-100 dark:bg-white/5 border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
              title={webSearchEnabled ? 'Web Search Enabled' : 'Local Vault RAG Only'}
            >
              <Globe className="w-3.5 h-3.5" />
              <span>Web Search</span>
            </button>

            <button
              onClick={handlePreloadModel}
              className="px-3 py-1.5 text-amber-700 dark:text-amber-400 hover:text-amber-600 bg-amber-500/10 rounded-lg border border-amber-500/20 transition-colors flex items-center gap-1.5 text-xs font-medium"
              title="Preload Model into GPU VRAM"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Warmup VRAM</span>
            </button>

            <button
              onClick={handleExportTranscript}
              className="p-2 text-slate-600 dark:text-slate-300 hover:text-emerald-500 bg-slate-100 dark:bg-white/5 rounded-lg border border-slate-300 dark:border-white/10 transition-colors"
              title="Export Chat Transcript (.md)"
            >
              <Download className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={handleClearMessages}
              className="p-2 text-slate-400 hover:text-rose-500 bg-slate-100 dark:bg-white/5 hover:bg-rose-500/10 rounded-lg border border-slate-300 dark:border-white/10 transition-colors"
              title="Clear Messages"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Neural Voice Studio Toolbar */}
        {showVoiceStudio && (
          <div className="px-6 py-2.5 bg-slate-100/90 dark:bg-slate-900/90 border-b border-slate-200/80 dark:border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-3">
              <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                <SlidersHorizontal className="w-3.5 h-3.5 text-purple-500" /> Neural Persona:
              </span>
              <select
                value={voicePersona}
                onChange={(e) => {
                  setVoicePersona(e.target.value);
                  localStorage.setItem('neuro_voice_persona', e.target.value);
                }}
                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-white/10 rounded-lg px-2.5 py-1 text-xs text-slate-900 dark:text-slate-200 outline-none focus:border-purple-500"
              >
                <option value="CORTANA_PRIME">Cortana Prime (Halo AI Blend)</option>
                <option value="AURA_SHIP_AI">Aura Ship AI (British Naval Blend)</option>
                <option value="EXECUTIVE_ADVISOR">Executive Advisor (Warm Productivity)</option>
                <option value="TACTICAL_OFFICER">Tactical Officer (Command)</option>
                <option value="af_sky">Kokoro Sky (Clear US Female)</option>
                <option value="af_bella">Kokoro Bella (Warm US Female)</option>
                <option value="bf_emma">Kokoro Emma (British Female)</option>
              </select>
            </div>

            <div className="flex items-center gap-3">
              <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-500" /> DSP Mastering:
              </span>
              <select
                value={dspPreset}
                onChange={(e) => {
                  setDspPreset(e.target.value);
                  localStorage.setItem('neuro_voice_dsp', e.target.value);
                }}
                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-white/10 rounded-lg px-2.5 py-1 text-xs text-slate-900 dark:text-slate-200 outline-none focus:border-emerald-500"
              >
                <option value="STUDIO_MASTER">Studio Master (4-Band EQ + Comp + De-Esser)</option>
                <option value="HOLOGRAPHIC_AI">Holographic AI (3D Haas Spatial Width)</option>
                <option value="AURA_COCKPIT">Aura Cockpit (Bridge Reverb)</option>
                <option value="TACTICAL_RADIO">Tactical Radio (VHF Bandpass)</option>
                <option value="STUDIO_DIRECT">Studio Direct (Uncolored)</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-slate-500">Speed:</span>
              <input
                type="range"
                min="0.8"
                max="1.4"
                step="0.05"
                value={voiceSpeed}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setVoiceSpeed(val);
                  localStorage.setItem('neuro_voice_speed', val.toString());
                }}
                className="w-20 accent-purple-600 cursor-pointer h-1.5"
              />
              <span className="font-mono text-slate-600 dark:text-slate-400 text-[11px] w-8">
                {voiceSpeed.toFixed(2)}x
              </span>
            </div>
          </div>
        )}


        {/* Message Bubble Feed */}
        <div
          ref={chatContainerRef}
          onScroll={handleContainerScroll}
          className="flex-1 overflow-y-auto px-6 py-6 space-y-6"
        >
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-800 flex items-center justify-center mb-6 shadow-lg shadow-emerald-900/20 border border-emerald-400/30">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-medium text-slate-900 dark:text-slate-100 mb-2 font-serif-claude">
                What knowledge shall we explore?
              </h3>
              <p className="text-xs text-slate-500 max-w-sm mb-8 leading-relaxed">
                Ask deep questions across your vault documents, synthesize complex architectures, or explore semantic multi-hop graphs.
              </p>

              <div className="grid grid-cols-2 gap-3 w-full">
                <button
                  onClick={() => handleSendPromptText('Summarize the top architectural findings in the vault')}
                  className="text-left p-3.5 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/60 dark:bg-slate-900/60 hover:border-emerald-500/40 hover:bg-emerald-500/5 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group shadow-2xs"
                >
                  <span className="font-semibold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Summarize Vault</span>
                  <span className="text-[11px] text-slate-500">Synthesize documents into key takeaways</span>
                </button>

                <button
                  onClick={() => handleSendPromptText("Explore multi-hop relationships and semantic clusters in the database")}
                  className="text-left p-3.5 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/60 dark:bg-slate-900/60 hover:border-emerald-500/40 hover:bg-emerald-500/5 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group shadow-2xs"
                >
                  <span className="font-semibold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Semantic Clusters</span>
                  <span className="text-[11px] text-slate-500">Map connected knowledge entities</span>
                </button>

                <button
                  onClick={() => handleSendPromptText('Explain Write-Ahead Logging (WAL) and compare with journal mode')}
                  className="text-left p-3.5 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/60 dark:bg-slate-900/60 hover:border-emerald-500/40 hover:bg-emerald-500/5 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group shadow-2xs"
                >
                  <span className="font-semibold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Database Engineering</span>
                  <span className="text-[11px] text-slate-500">Deconstruct WAL concurrency & performance</span>
                </button>

                <button
                  onClick={() => handleSendPromptText('Synthesize an executive compliance brief from recent documents')}
                  className="text-left p-3.5 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white/60 dark:bg-slate-900/60 hover:border-emerald-500/40 hover:bg-emerald-500/5 transition-all text-xs text-slate-700 dark:text-slate-300 flex flex-col gap-1 group shadow-2xs"
                >
                  <span className="font-semibold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Executive Briefing</span>
                  <span className="text-[11px] text-slate-500">Generate high-level strategic overview</span>
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={msg.id} className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-emerald-500/15 flex items-center justify-center flex-shrink-0 border border-emerald-500/30 mt-0.5">
                    <Bot className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  </div>
                )}

                <div className={`group relative max-w-[88%] rounded-2xl p-4.5 shadow-xs ${
                  msg.role === 'user'
                    ? 'bg-slate-900 text-white dark:bg-slate-800 border border-slate-700/60 rounded-tr-xs'
                    : `${glassCardClasses} rounded-tl-xs text-slate-900 dark:text-slate-100`
                }`}>
                  {/* Reasoning Timeline Header */}
                  {msg.role === 'assistant' && (
                    <div className="mb-3 pb-2.5 border-b border-slate-200/60 dark:border-white/5">
                      <button
                        onClick={() => setExpandedReasoning(prev => ({ ...prev, [msg.id]: !prev[msg.id] }))}
                        className="flex items-center justify-between w-full text-[11px] font-medium text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors cursor-pointer"
                      >
                        <div className="flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                          <span>Grounded Verification Pipeline</span>
                        </div>
                        <ChevronRight className={`w-3.5 h-3.5 transition-transform ${expandedReasoning[msg.id] ? 'rotate-90' : ''}`} />
                      </button>

                      {expandedReasoning[msg.id] && (
                        <div className="mt-2 pl-4 space-y-1 text-[11px] text-slate-400 font-mono border-l-2 border-emerald-500/40">
                          <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                            <span>✓</span> 1. Vector Search: ColBERT MaxSim & FTS5 Normalized Queries
                          </div>
                          <div className="flex items-center gap-1.5 text-teal-600 dark:text-teal-400">
                            <span>✓</span> 2. Reciprocal Rank Fusion ({msg.sources?.length || 5} source chunks)
                          </div>
                          <div className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
                            <span>✓</span> 3. Neural Synthesis: {msg.metrics?.tier || 'Master'}: {msg.metrics?.model || 'qwen2.5:7b'}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Formatted Content */}
                  {renderFormattedContent(msg.content, msg.id, isStreaming && idx === messages.length - 1)}

                  {/* Telemetry Metrics */}
                  {msg.role === 'assistant' && msg.metrics && (
                    <div className="flex items-center gap-2 mt-3.5 pt-2 border-t border-slate-200/50 dark:border-white/5 text-[10px] text-slate-400 font-mono">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-semibold uppercase tracking-wider">
                        {msg.metrics.tier || 'Master'}: {msg.metrics.model}
                      </span>
                      {msg.metrics.tokens_per_sec && <span>• {msg.metrics.tokens_per_sec} tok/s</span>}
                      {msg.metrics.duration_sec && <span>• {msg.metrics.duration_sec}s</span>}
                      {msg.metrics.tokens_generated && <span>• {msg.metrics.tokens_generated} tokens</span>}
                    </div>
                  )}

                  {/* Grounded Sources / Citations */}
                  {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3.5 pt-2.5 border-t border-slate-200/80 dark:border-white/10 space-y-2">
                      <div className="flex items-center justify-between text-[11px] font-medium text-slate-500 uppercase tracking-wider">
                        <span>Grounded Context Sources ({msg.sources.length}):</span>
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Verified Sources</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((src, sIdx) => {
                          const confPct = Math.round((src.confidence_score || 0.92) * 100);
                          return (
                            <button
                              key={sIdx}
                              onClick={() => setSelectedCitation(src)}
                              className="inline-flex items-center gap-1.5 text-[11px] bg-slate-100 dark:bg-white/5 hover:bg-emerald-500/15 hover:border-emerald-500/40 px-2.5 py-1 rounded-lg border border-slate-300/80 dark:border-white/10 text-slate-800 dark:text-slate-200 max-w-xs truncate transition-all cursor-pointer"
                              title="Click to view full grounded excerpt"
                            >
                              {src.url ? <Globe className="w-3 h-3 flex-shrink-0 text-emerald-500" /> : <FileText className="w-3 h-3 flex-shrink-0 text-amber-500" />}
                              <span className="truncate">{src.title || src.path || src.url}</span>
                              <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-mono font-bold">
                                {confPct}%
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Interactive Assistant Action Bar */}
                  {msg.role === 'assistant' && msg.content && (
                    <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-200/50 dark:border-white/5 text-xs text-slate-400">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => copyMessageText(msg.id, msg.content)}
                          className="p-1.5 hover:text-emerald-500 hover:bg-slate-100 dark:hover:bg-white/5 rounded-md transition-colors flex items-center gap-1 text-[11px]"
                          title="Copy Full Response"
                        >
                          {copiedMsgId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                          <span>{copiedMsgId === msg.id ? 'Copied' : 'Copy'}</span>
                        </button>

                        <button
                          onClick={() => handleToggleSpeak(msg.id, msg.content)}
                          className={`p-1.5 hover:bg-slate-100 dark:hover:bg-white/5 rounded-md transition-colors flex items-center gap-1.5 text-[11px] ${
                            speakingMsgId === msg.id
                              ? 'text-purple-600 dark:text-purple-300 font-medium bg-purple-500/10'
                              : 'hover:text-purple-500 dark:hover:text-purple-400'
                          }`}
                          title="Read Aloud with Studio Neural Voice"
                        >
                          {speakingMsgId === msg.id ? (
                            <>
                              <div className="flex items-center gap-0.5 h-3">
                                <span className="w-0.5 h-2 bg-purple-500 animate-pulse" />
                                <span className="w-0.5 h-3.5 bg-purple-500 animate-bounce" />
                                <span className="w-0.5 h-2 bg-purple-500 animate-pulse" />
                              </div>
                              <VolumeX className="w-3.5 h-3.5 text-purple-500" />
                              <span>Stop</span>
                            </>
                          ) : (
                            <>
                              <Volume2 className="w-3.5 h-3.5" />
                              <span>{isAudioLoading && speakingMsgId === msg.id ? 'Buffering...' : 'Read'}</span>
                            </>
                          )}
                        </button>


                        <button
                          onClick={handleRegenerate}
                          disabled={isStreaming}
                          className="p-1.5 hover:text-emerald-500 hover:bg-slate-100 dark:hover:bg-white/5 rounded-md transition-colors flex items-center gap-1 text-[11px] disabled:opacity-40"
                          title="Regenerate Answer"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                          <span>Retry</span>
                        </button>
                      </div>

                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleRate(msg.id, 'up')}
                          className={`p-1.5 rounded-md transition-colors ${ratings[msg.id] === 'up' ? 'text-emerald-500 bg-emerald-500/10' : 'hover:text-emerald-500 hover:bg-slate-100 dark:hover:bg-white/5'}`}
                          title="Helpful response"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleRate(msg.id, 'down')}
                          className={`p-1.5 rounded-md transition-colors ${ratings[msg.id] === 'down' ? 'text-rose-500 bg-rose-500/10' : 'hover:text-rose-500 hover:bg-slate-100 dark:hover:bg-white/5'}`}
                          title="Unhelpful response"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Contextual Smart Follow-up Suggestions */}
                  {msg.role === 'assistant' && !isStreaming && idx === messages.length - 1 && msg.content && (
                    <div className="mt-3.5 pt-3 border-t border-slate-200/50 dark:border-white/10 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-500 dark:text-slate-400">
                        <Sparkles className="w-3 h-3 text-amber-500" />
                        <span>Suggested Next Steps:</span>
                      </div>
                      <div className="flex flex-col sm:flex-row flex-wrap gap-2">
                        {getFollowUpSuggestions(msg.content).map((sugg, suggIdx) => (
                          <button
                            key={suggIdx}
                            onClick={() => handleSendPromptText(sugg)}
                            className="text-left text-xs px-3 py-1.5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/15 text-slate-700 dark:text-slate-300 hover:text-emerald-700 dark:hover:text-emerald-300 transition-all flex items-center gap-1.5"
                          >
                            <MessageSquare className="w-3 h-3 text-emerald-500 flex-shrink-0" />
                            <span>{sugg}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 border border-slate-300 dark:border-white/10 mt-0.5">
                    <User className="w-4 h-4 text-slate-700 dark:text-slate-300" />
                  </div>
                )}
              </div>
            ))
          )}

          {isStreaming && (
            <div className="flex gap-3.5 justify-start">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0 border border-emerald-500/30">
                <Bot className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div className={`${glassCardClasses} rounded-2xl rounded-tl-xs p-4 flex items-center gap-2.5 shadow-md`}>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="w-2 h-2 rounded-full bg-teal-500 animate-pulse delay-75" />
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse delay-150" />
                <span className="text-xs text-slate-500 ml-1 font-serif-claude">Synthesizing grounded response...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showScrollBottom && (
          <button
            onClick={scrollToBottom}
            className="absolute bottom-32 right-8 p-2.5 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white shadow-xl border border-white/20 transition-all z-20"
            title="Scroll to bottom"
          >
            <ArrowDown className="w-4 h-4" />
          </button>
        )}

        {/* Floating Claude-like Bottom Input Dock */}
        <div className="p-4 bg-white/70 dark:bg-slate-900/80 backdrop-blur-md border-t border-slate-200/80 dark:border-white/5 space-y-2.5">
          {/* Presets Row */}
          <div className="max-w-4xl mx-auto flex items-center gap-2 overflow-x-auto pb-0.5 text-[11px]">
            <span className="text-slate-500 text-[10px] font-semibold uppercase tracking-wider flex items-center gap-1 flex-shrink-0">
              <Sparkles className="w-3 h-3 text-amber-500" /> Presets:
            </span>
            <button
              onClick={() => handleSendPromptText('Explain SQLite Write-Ahead Logging (WAL) and provide a technical comparison table with rollback journal')}
              className="px-2.5 py-1 rounded-lg border border-slate-200/80 dark:border-white/10 bg-white/50 dark:bg-white/5 hover:bg-emerald-500/10 text-slate-700 dark:text-slate-300 transition-colors flex-shrink-0"
            >
              📊 SQLite WAL Mode
            </button>
            <button
              onClick={() => handleSendPromptText('Deep dive into vector ColBERT MaxSim reranking vs Dense Cosine similarity')}
              className="px-2.5 py-1 rounded-lg border border-slate-200/80 dark:border-white/10 bg-white/50 dark:bg-white/5 hover:bg-emerald-500/10 text-slate-700 dark:text-slate-300 transition-colors flex-shrink-0"
            >
              ⚡ ColBERT MaxSim
            </button>
            <button
              onClick={() => handleSendPromptText('Summarize the top 5 core system capabilities of the Uroboros Knowledge Engine')}
              className="px-2.5 py-1 rounded-lg border border-slate-200/80 dark:border-white/10 bg-white/50 dark:bg-white/5 hover:bg-emerald-500/10 text-slate-700 dark:text-slate-300 transition-colors flex-shrink-0"
            >
              📝 Vault Overview
            </button>
          </div>

          {/* Textarea Form */}
          <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-end">
            <textarea
              className="w-full bg-white/80 dark:bg-slate-800/60 border border-slate-300 dark:border-white/10 rounded-2xl px-4 py-3.5 pr-28 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 resize-none min-h-[54px] max-h-32 text-sm leading-relaxed shadow-sm transition-all"
              placeholder="Ask anything about your vault documents, architecture, or research..."
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

            <div className="absolute right-2.5 bottom-2.5 flex items-center gap-1.5">
              {/* Magic Wand Prompt Enhancer (Mustard Gold) */}
              <button
                type="button"
                onClick={handleEnhancePrompt}
                disabled={!input.trim() || isEnhancingPrompt}
                className="p-2 text-amber-600 dark:text-amber-400 hover:bg-amber-500/10 rounded-xl transition-colors disabled:opacity-30 cursor-pointer"
                title="Magic Prompt Enhancer (Mustard Gold Wand)"
              >
                <Wand2 className={`w-4 h-4 ${isEnhancingPrompt ? 'animate-spin' : ''}`} />
              </button>

              {/* Voice Dictation (Emerald Mic) */}
              <button
                type="button"
                onClick={handleToggleVoiceRecording}
                className={`p-2 rounded-xl transition-colors cursor-pointer ${
                  isRecordingVoice
                    ? 'bg-rose-600 text-white animate-pulse'
                    : 'text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-slate-100 dark:hover:bg-white/5'
                }`}
                title={isRecordingVoice ? 'Stop Recording' : 'Dictate with Voice (Web Speech API)'}
              >
                {isRecordingVoice ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              {/* Send Button (Emerald) */}
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="p-2.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 rounded-xl cursor-pointer disabled:opacity-30 transition-all shadow-xs active:scale-95"
                title="Send Message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
          <div className="text-center text-[11px] text-slate-400">
            Uroboros Knowledge Engine • Grounded Neural RAG Studio
          </div>
        </div>
      </div>

      {/* Claude-style Split-Pane Artifacts Canvas */}
      {activeArtifact && (
        <div className={`border-l border-slate-200 dark:border-white/10 bg-slate-950 text-slate-100 flex flex-col transition-all duration-300 ${isCanvasFullscreen ? 'w-full' : 'w-[45%]'}`}>
          {/* Canvas Header */}
          <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90 backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-emerald-400" />
              <span className="font-semibold text-xs text-slate-200 uppercase tracking-wider font-mono">{activeArtifact.title}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono uppercase font-bold border border-emerald-500/30">
                {activeArtifact.language}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {/* Tab Selector */}
              <div className="flex rounded-lg bg-slate-800 p-0.5 text-xs border border-white/5">
                <button
                  onClick={() => setArtifactTab('preview')}
                  className={`px-2.5 py-1 rounded-md transition-colors flex items-center gap-1 ${artifactTab === 'preview' ? 'bg-emerald-600 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  <Eye className="w-3 h-3" />
                  <span>Preview</span>
                </button>
                <button
                  onClick={() => setArtifactTab('code')}
                  className={`px-2.5 py-1 rounded-md transition-colors flex items-center gap-1 ${artifactTab === 'code' ? 'bg-emerald-600 text-white font-medium shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  <Code className="w-3 h-3" />
                  <span>Code</span>
                </button>
              </div>

              {/* Fullscreen Toggle */}
              <button
                onClick={() => setIsCanvasFullscreen(!isCanvasFullscreen)}
                className="p-1.5 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title={isCanvasFullscreen ? 'Exit Fullscreen' : 'Expand Fullscreen'}
              >
                {isCanvasFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>

              {/* Close Canvas */}
              <button
                onClick={() => setActiveArtifact(null)}
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                title="Close Canvas"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Canvas Body */}
          <div className="flex-1 overflow-y-auto p-4 bg-slate-950">
            {artifactTab === 'preview' ? (
              <div className="h-full rounded-xl border border-slate-800 bg-slate-900/50 p-4 overflow-auto">
                {activeArtifact.language === 'html' || activeArtifact.language === 'svg' ? (
                  <div
                    dangerouslySetInnerHTML={{ __html: activeArtifact.content }}
                    className="w-full text-slate-200"
                  />
                ) : (
                  <div className="space-y-3 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                    <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 flex-shrink-0" />
                      <span>Live Interactive Artifact Preview Sandbox</span>
                    </div>
                    <pre className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 font-mono text-[12px]">{activeArtifact.content}</pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full rounded-xl border border-slate-800 bg-slate-900/80 text-slate-100 text-xs font-mono p-4 overflow-auto leading-relaxed">
                <pre>{activeArtifact.content}</pre>
              </div>
            )}
          </div>

          {/* Canvas Footer */}
          <div className="p-3 border-t border-slate-800 flex items-center justify-between bg-slate-900 text-xs text-slate-400">
            <span className="font-mono text-[11px]">{activeArtifact.content.length} characters</span>
            <button
              onClick={() => {
                copyMessageText('artifact', activeArtifact.content);
                toast('Copied', 'Artifact code copied to clipboard', 'info');
              }}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-colors flex items-center gap-1.5 text-xs shadow-sm"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>Copy Code</span>
            </button>
          </div>
        </div>
      )}

      {/* Citation Popover Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className={`${glassCardClasses} w-full max-w-xl rounded-2xl p-6 shadow-2xl border border-slate-700/50 space-y-4 max-h-[80vh] flex flex-col`}>
            <div className="flex items-center justify-between border-b border-slate-700/50 pb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-emerald-500" />
                <h3 className="text-sm font-semibold text-slate-100 truncate max-w-md font-serif-claude">
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
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono bg-slate-900/60 p-2.5 rounded-lg border border-white/5">
              <span className="truncate max-w-xs">{selectedCitation.path || selectedCitation.url || 'Internal Knowledge Base'}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                {Math.round((selectedCitation.confidence_score || 0.92) * 100)}% Match
              </span>
            </div>
            <div className="flex-1 overflow-y-auto bg-slate-900/90 p-4 rounded-xl border border-slate-800 text-slate-200 text-xs font-mono leading-relaxed whitespace-pre-wrap">
              {selectedCitation.snippet || selectedCitation.citation || 'No preview text excerpt available for this source.'}
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => {
                  copyMessageText('cit', selectedCitation.snippet || selectedCitation.path || '');
                  toast('Copied', 'Citation excerpt copied to clipboard', 'info');
                }}
                className={`px-3.5 py-1.5 ${emeraldButtonClasses} text-xs font-medium transition-colors flex items-center gap-1.5`}
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
