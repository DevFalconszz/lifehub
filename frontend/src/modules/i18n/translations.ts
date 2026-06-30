const en = {
  app: { name: 'LifeHub' },
  nav: { dashboard: 'Dashboard', projects: 'Projects', tasks: 'Tasks', notes: 'Notes', finances: 'Finances', calendar: 'Calendar', readings: 'Readings', ai: 'AI Chat' },
  auth: { signIn: 'Sign In', register: 'Create Account', registerLink: "Don't have an account?", signInLink: 'Already have an account?', name: 'Name', email: 'Email', password: 'Password', registerBtn: 'Register', logout: 'Logout', registerHere: 'Register', signInHere: 'Sign In' },
  common: { add: 'Add', create: 'Create', update: 'Update', edit: 'Edit', new: 'New', del: 'Del', delete: 'Delete', cancel: 'Cancel', save: 'Save', archive: 'Archive', activate: 'Activate', noItems: 'No items', search: 'Search', settings: 'Settings', theme: 'Theme', language: 'Language', light: 'Light', dark: 'Dark', optional: 'optional' },
  dashboard: { title: 'Dashboard', monthlySummary: 'Monthly Summary', income: 'Income', expenses: 'Expenses', balance: 'Balance', recentTasks: 'Recent Tasks', upcomingEvents: 'Upcoming Events' },
  projects: { title: 'Projects', name: 'Project name', description: 'Description (optional)', category: 'Category', priority_low: 'Low', priority_medium: 'Medium', priority_high: 'High', priority_urgent: 'Urgent', progress: 'Progress', startDate: 'Start', targetDate: 'Target', url: 'URL (external link)', link: 'Link', status_active: 'Active', status_paused: 'Paused', status_completed: 'Completed', status_archived: 'Archived', noProjects: 'No projects yet' },
  tasks: { title: 'Tasks', taskTitle: 'Task title', selectProject: 'Select project', noTasks: 'No tasks yet' },
  notes: { title: 'Notes', noteTitle: 'Note title', content: 'Content (markdown)...', noNotes: 'No notes yet' },
  finances: { title: 'Finances', addTransaction: 'Add Transaction', description: 'Description', amount: 'Amount', category: 'Category', expense: 'Expense', income: 'Income', setBudget: 'Set Budget', general: 'General', limit: 'Limit', transactions: 'Transactions', noTransactions: 'No transactions', budgets: 'Budgets' },
  calendar: { title: 'Calendar', eventTitle: 'Event title', description: 'Description (optional)', allDay: 'All day', noEvents: 'No events' },
  readings: { title: 'Readings', title_: 'Title', author: 'Author (optional)', url: 'URL (optional)', noReadings: 'No reading items yet' },
  ai: { title: 'AI Chat', placeholder: 'Type a message...', thinking: 'Thinking...', send: 'Send', intro: 'Ask me anything! I can manage your projects, tasks, notes, finances, events, and reading list.' },
};

const ptBR: typeof en = {
  app: { name: 'LifeHub' },
  nav: { dashboard: 'Painel', projects: 'Projetos', tasks: 'Tarefas', notes: 'Notas', finances: 'Finanças', calendar: 'Agenda', readings: 'Leituras', ai: 'Chat IA' },
  auth: { signIn: 'Entrar', register: 'Criar Conta', registerLink: 'Não tem uma conta?', signInLink: 'Já tem uma conta?', name: 'Nome', email: 'Email', password: 'Senha', registerBtn: 'Cadastrar', logout: 'Sair', registerHere: 'Cadastre-se', signInHere: 'Entrar' },
  common: { add: 'Adicionar', create: 'Criar', update: 'Atualizar', edit: 'Editar', new: 'Novo', del: 'Del', delete: 'Excluir', cancel: 'Cancelar', save: 'Salvar', archive: 'Arquivar', activate: 'Ativar', noItems: 'Nenhum item', search: 'Buscar', settings: 'Configurações', theme: 'Tema', language: 'Idioma', light: 'Claro', dark: 'Escuro', optional: 'opcional' },
  dashboard: { title: 'Painel', monthlySummary: 'Resumo Mensal', income: 'Receitas', expenses: 'Despesas', balance: 'Saldo', recentTasks: 'Tarefas Recentes', upcomingEvents: 'Próximos Eventos' },
  projects: { title: 'Projetos', name: 'Nome do projeto', description: 'Descrição (opcional)', category: 'Categoria', priority_low: 'Baixa', priority_medium: 'Média', priority_high: 'Alta', priority_urgent: 'Urgente', progress: 'Progresso', startDate: 'Início', targetDate: 'Meta', url: 'URL (link externo)', link: 'Link', status_active: 'Ativo', status_paused: 'Pausado', status_completed: 'Concluído', status_archived: 'Arquivado', noProjects: 'Nenhum projeto ainda' },
  tasks: { title: 'Tarefas', taskTitle: 'Título da tarefa', selectProject: 'Selecione o projeto', noTasks: 'Nenhuma tarefa ainda' },
  notes: { title: 'Notas', noteTitle: 'Título da nota', content: 'Conteúdo (markdown)...', noNotes: 'Nenhuma nota ainda' },
  finances: { title: 'Finanças', addTransaction: 'Adicionar Transação', description: 'Descrição', amount: 'Valor', category: 'Categoria', expense: 'Despesa', income: 'Receita', setBudget: 'Definir Orçamento', general: 'Geral', limit: 'Limite', transactions: 'Transações', noTransactions: 'Nenhuma transação', budgets: 'Orçamentos' },
  calendar: { title: 'Agenda', eventTitle: 'Título do evento', description: 'Descrição (opcional)', allDay: 'Dia inteiro', noEvents: 'Nenhum evento' },
  readings: { title: 'Leituras', title_: 'Título', author: 'Autor (opcional)', url: 'URL (opcional)', noReadings: 'Nenhum item de leitura ainda' },
  ai: { title: 'Chat IA', placeholder: 'Digite uma mensagem...', thinking: 'Pensando...', send: 'Enviar', intro: 'Pergunte qualquer coisa! Posso gerenciar seus projetos, tarefas, notas, finanças, eventos e lista de leitura.' },
};

export type Lang = keyof typeof translations;
export type Translations = typeof en;

export const translations = { en, 'pt-BR': ptBR } as const;

export const languages: { code: Lang; label: string }[] = [
  { code: 'en', label: 'English' },
  { code: 'pt-BR', label: 'Português (BR)' },
];
