-- Row Level Security Policies for LifeHub
-- This ensures data isolation at the database level

-- Enable RLS (already done in migration 001, but idempotent)
ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.reading_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.chat_messages ENABLE ROW LEVEL SECURITY;

-- Helper: Drop existing policies first
DO $$ DECLARE
  stmt text;
BEGIN
  SELECT string_agg(format('DROP POLICY IF EXISTS %I ON %I.%I;', policyname, schemaname, tablename), ' ')
  INTO stmt
  FROM pg_policies WHERE schemaname = 'public';
  IF stmt IS NOT NULL THEN
    EXECUTE stmt;
  END IF;
END $$;

-- Users: each user can only see/update their own record
CREATE POLICY "Users can view own record" ON public.users
  FOR SELECT USING (id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own record" ON public.users
  FOR UPDATE USING (id::text = current_setting('request.jwt.claims', true)::json->>'sub')
  WITH CHECK (id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Projects: user_id must match JWT sub
CREATE POLICY "Users can view own projects" ON public.projects
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own projects" ON public.projects
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own projects" ON public.projects
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own projects" ON public.projects
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Tasks
CREATE POLICY "Users can view own tasks" ON public.tasks
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own tasks" ON public.tasks
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own tasks" ON public.tasks
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own tasks" ON public.tasks
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Notes
CREATE POLICY "Users can view own notes" ON public.notes
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own notes" ON public.notes
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own notes" ON public.notes
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own notes" ON public.notes
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Transactions
CREATE POLICY "Users can view own transactions" ON public.transactions
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own transactions" ON public.transactions
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own transactions" ON public.transactions
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own transactions" ON public.transactions
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Budgets
CREATE POLICY "Users can view own budgets" ON public.budgets
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own budgets" ON public.budgets
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own budgets" ON public.budgets
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own budgets" ON public.budgets
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Events
CREATE POLICY "Users can view own events" ON public.events
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own events" ON public.events
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own events" ON public.events
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own events" ON public.events
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Reading items
CREATE POLICY "Users can view own reading items" ON public.reading_items
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own reading items" ON public.reading_items
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own reading items" ON public.reading_items
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own reading items" ON public.reading_items
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Chat sessions
CREATE POLICY "Users can view own chat sessions" ON public.chat_sessions
  FOR SELECT USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can create own chat sessions" ON public.chat_sessions
  FOR INSERT WITH CHECK (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own chat sessions" ON public.chat_sessions
  FOR UPDATE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own chat sessions" ON public.chat_sessions
  FOR DELETE USING (user_id::text = current_setting('request.jwt.claims', true)::json->>'sub');

-- Chat messages: access via session
CREATE POLICY "Users can view own chat messages" ON public.chat_messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions
      WHERE id = chat_messages.session_id
      AND user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    )
  );

CREATE POLICY "Users can create own chat messages" ON public.chat_messages
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.chat_sessions
      WHERE id = chat_messages.session_id
      AND user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    )
  );

CREATE POLICY "Users can delete own chat messages" ON public.chat_messages
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions
      WHERE id = chat_messages.session_id
      AND user_id::text = current_setting('request.jwt.claims', true)::json->>'sub'
    )
  );
