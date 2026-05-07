# Supabase Daily Usage Setup

This table stores per-user daily planner usage so limits are consistent across devices.

Run this SQL in Supabase SQL Editor:

```sql
create table if not exists public.user_daily_usage (
  user_id uuid not null references auth.users(id) on delete cascade,
  usage_date date not null,
  count integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (user_id, usage_date)
);

alter table public.user_daily_usage enable row level security;

create policy "users_can_read_own_usage"
on public.user_daily_usage
for select
to authenticated
using (auth.uid() = user_id);

create policy "users_can_insert_own_usage"
on public.user_daily_usage
for insert
to authenticated
with check (auth.uid() = user_id);

create policy "users_can_update_own_usage"
on public.user_daily_usage
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);
```

Notes:
- Guest usage remains local (browser storage).
- Signed-in usage now reads/writes this table.
- If table/policies are missing, frontend falls back to local counters.
