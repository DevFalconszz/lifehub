const BASE = import.meta.env.VITE_API_URL || '/api';

let token: string | null = localStorage.getItem('token');

export function setToken(t: string | null) {
  token = t;
  if (t) localStorage.setItem('token', t);
  else localStorage.removeItem('token');
}

export function getToken() {
  if (!token) token = localStorage.getItem('token');
  return token;
}

async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  const t = getToken();
  if (t) headers['Authorization'] = `Bearer ${t}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    setToken(null);
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (res.status === 204) return null;

  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Unexpected response (${res.status})`);
  }
}

export const api = {
  // Auth
  register: (data: { name: string; email: string; password: string }) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/auth/me'),

  // Projects
  listProjects: () => request('/projects'),
  createProject: (data: any) => request('/projects', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id: string, data: any) => request(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteProject: (id: string) => request(`/projects/${id}`, { method: 'DELETE' }),

  // Tasks
  listTasks: () => request('/tasks'),
  createTask: (data: any) => request('/tasks', { method: 'POST', body: JSON.stringify(data) }),
  updateTask: (projectId: string, taskId: string, data: any) =>
    request(`/projects/${projectId}/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteTask: (projectId: string, taskId: string) =>
    request(`/projects/${projectId}/tasks/${taskId}`, { method: 'DELETE' }),

  // Notes
  listNotes: () => request('/notes'),
  createNote: (data: any) => request('/notes', { method: 'POST', body: JSON.stringify(data) }),
  updateNote: (id: string, data: any) => request(`/notes/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteNote: (id: string) => request(`/notes/${id}`, { method: 'DELETE' }),

  // Finances
  listTransactions: (params?: string) => request(`/finances/transactions${params ? '?' + params : ''}`),
  createTransaction: (data: any) => request('/finances/transactions', { method: 'POST', body: JSON.stringify(data) }),
  deleteTransaction: (id: string) => request(`/finances/transactions/${id}`, { method: 'DELETE' }),
  getFinanceSummary: (month: number, year: number) => request(`/finances/summary?month=${month}&year=${year}`),
  getBudgets: (month: number, year: number) => request(`/finances/budgets?month=${month}&year=${year}`),
  setBudget: (data: any) => request('/finances/budgets', { method: 'POST', body: JSON.stringify(data) }),

  // Calendar
  listEvents: (params?: string) => request(`/calendar/events${params ? '?' + params : ''}`),
  createEvent: (data: any) => request('/calendar/events', { method: 'POST', body: JSON.stringify(data) }),
  updateEvent: (id: string, data: any) => request(`/calendar/events/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteEvent: (id: string) => request(`/calendar/events/${id}`, { method: 'DELETE' }),

  // Readings
  listReadings: (params?: string) => request(`/readings${params ? '?' + params : ''}`),
  createReading: (data: any) => request('/readings', { method: 'POST', body: JSON.stringify(data) }),
  updateReading: (id: string, data: any) => request(`/readings/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteReading: (id: string) => request(`/readings/${id}`, { method: 'DELETE' }),

  // AI Chat
  chat: (messages: any[], stream = false, sessionId?: string) =>
    request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ messages, stream, session_id: sessionId }),
    }),

  // AI Sessions
  listSessions: () => request('/ai/sessions'),
  createSession: (title?: string) =>
    request('/ai/sessions', { method: 'POST', body: JSON.stringify({ title: title || 'New Chat' }) }),
  getSession: (id: string) => request(`/ai/sessions/${id}`),
  deleteSession: (id: string) => request(`/ai/sessions/${id}`, { method: 'DELETE' }),

  saveMessage: (sessionId: string, messages: any[]) =>
    request(`/ai/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ messages }),
    }),
};
