import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api, getToken } from '../api/client';
import { useT } from '../modules/i18n/store';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export default function AiChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const t = useT();

  const loadSessions = useCallback(async () => {
    try {
      const data = await api.listSessions();
      setSessions(data || []);
      if (data?.length > 0) {
        setCurrentSessionId(data[0].id);
        const session = await api.getSession(data[0].id);
        setMessages(
          (session.messages || []).map((m: any) => ({ role: m.role, content: m.content })),
        );
      } else {
        const s = await api.createSession();
        setCurrentSessionId(s.id);
        setSessions([{ id: s.id, title: s.title, created_at: s.created_at, updated_at: s.updated_at, message_count: 0 }]);
      }
    } catch {}
  }, []);

  useEffect(() => { loadSessions(); }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const persistMessages = async (msgs: Message[], sessionId: string) => {
    try {
      for (const msg of msgs.slice(-2)) {
        await api.saveMessage(sessionId, [msg]);
      }
      loadSessions();
    } catch {}
  };

  const switchSession = async (id: string) => {
    setCurrentSessionId(id);
    try {
      const session = await api.getSession(id);
      setMessages(
        (session.messages || []).map((m: any) => ({ role: m.role, content: m.content })),
      );
    } catch {}
  };

  const newSession = async () => {
    const s = await api.createSession();
    setCurrentSessionId(s.id);
    setMessages([]);
    setSessions((prev) => [{ id: s.id, title: s.title, created_at: s.created_at, updated_at: s.updated_at, message_count: 0 }, ...prev]);
  };

  const deleteSession = async (id: string) => {
    try {
      await api.deleteSession(id);
      const updated = sessions.filter((s) => s.id !== id);
      setSessions(updated);
      if (currentSessionId === id) {
        if (updated.length > 0) {
          switchSession(updated[0].id);
        } else {
          newSession();
        }
      }
    } catch {}
  };

  const sendStream = async () => {
    if (!currentSessionId) return;
    const userMsg: Message = { role: 'user', content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setStreaming(true);

    const assistantMsg: Message = { role: 'assistant', content: '' };
    setMessages((m) => [...m, assistantMsg]);

    try {
      const token = getToken();
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ messages: newMessages, stream: true, session_id: currentSessionId }),
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value);
          const lines = text.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') continue;
              try {
                const parsed = JSON.parse(data);
                const chunk = parsed.choices?.[0]?.delta?.content || '';
                if (chunk) fullContent += chunk;
                setMessages((m) => {
                  const updated = [...m];
                  const last = updated[updated.length - 1];
                  updated[updated.length - 1] = { ...last, content: last.content + chunk };
                  return updated;
                });
              } catch {}
            }
          }
        }
      }

      if (fullContent) {
        persistMessages(
          [...newMessages, { role: 'assistant', content: fullContent }],
          currentSessionId,
        );
      }
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: `Error: ${err}` }]);
    }

    setStreaming(false);
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;
    sendStream();
  };

  const formatDate = (d: string) => {
    const date = new Date(d);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex h-full gap-4">
      <div className="w-56 flex-shrink-0">
        <button onClick={newSession}
          className="w-full mb-3 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium">
          + {t('common.new')} Chat
        </button>
        <div className="space-y-1 overflow-auto max-h-[calc(100vh-12rem)]">
          {sessions.map((s) => (
            <div key={s.id}
              className={`group flex items-center justify-between px-2 py-1.5 rounded-lg text-sm cursor-pointer transition-colors ${
                currentSessionId === s.id
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
              onClick={() => switchSession(s.id)}
            >
              <span className="truncate text-xs">{s.title === 'New Chat' ? formatDate(s.created_at) : s.title}</span>
              <button onClick={(e) => { e.stopPropagation(); deleteSession(s.id); }}
                className="text-xs text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 ml-1">×</button>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-auto mb-4 space-y-4">
          {messages.length === 0 && (
            <p className="text-gray-400 dark:text-gray-500 text-center py-12">
              {t('ai.intro')}
            </p>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] p-3 rounded-lg text-sm ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow'
              }`}>
                {msg.role === 'assistant' && msg.content ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        const isInline = !match;
                        if (isInline) {
                          return <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm" {...props}>{children}</code>;
                        }
                        return (
                          <pre className="bg-gray-900 dark:bg-gray-950 text-gray-100 p-3 rounded-lg overflow-x-auto my-2 text-sm">
                            <code className={className} {...props}>{children}</code>
                          </pre>
                        );
                      },
                      a({ href, children }) {
                        return <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary-600 dark:text-primary-400 underline">{children}</a>;
                      },
                      ul({ children }) {
                        return <ul className="list-disc list-inside space-y-1">{children}</ul>;
                      },
                      ol({ children }) {
                        return <ol className="list-decimal list-inside space-y-1">{children}</ol>;
                      },
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  msg.content || <span className="text-gray-400 italic">{t('ai.thinking')}</span>
                )}
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </div>

        <form onSubmit={handleSend} className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('ai.placeholder')}
            disabled={streaming}
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button type="submit" disabled={streaming}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
            {streaming ? '...' : t('ai.send')}
          </button>
        </form>
      </div>
    </div>
  );
}
