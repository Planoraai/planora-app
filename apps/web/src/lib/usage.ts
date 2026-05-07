export type AuthSession = {
  email: string;
  userId?: string;
};

const USAGE_KEY = "planora.usage.daily";
const GUEST_DAILY_LIMIT = 2;
const AUTH_DAILY_LIMIT = 5;
const USER_DAILY_USAGE_TABLE = "user_daily_usage";

type UsageRecord = {
  date: string;
  guestUsed: number;
  userUsed: Record<string, number>;
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function todayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

function readUsage(): UsageRecord {
  if (!isBrowser()) {
    return { date: todayKey(), guestUsed: 0, userUsed: {} };
  }
  try {
    const raw = window.localStorage.getItem(USAGE_KEY);
    if (!raw) {
      return { date: todayKey(), guestUsed: 0, userUsed: {} };
    }
    const parsed = JSON.parse(raw) as UsageRecord;
    if (parsed.date !== todayKey()) {
      return { date: todayKey(), guestUsed: 0, userUsed: {} };
    }
    return parsed;
  } catch {
    return { date: todayKey(), guestUsed: 0, userUsed: {} };
  }
}

function writeUsage(record: UsageRecord): void {
  if (!isBrowser()) return;
  window.localStorage.setItem(USAGE_KEY, JSON.stringify(record));
}

async function getSupabaseClient() {
  const { supabase } = await import("@/lib/supabase");
  return supabase;
}

function getLocalSignedInRemaining(email: string): number {
  const usage = readUsage();
  const used = usage.userUsed[email] || 0;
  return Math.max(0, AUTH_DAILY_LIMIT - used);
}

function consumeLocalSignedInPlan(email: string): number {
  const usage = readUsage();
  usage.userUsed[email] = (usage.userUsed[email] || 0) + 1;
  writeUsage(usage);
  return Math.max(0, AUTH_DAILY_LIMIT - usage.userUsed[email]);
}

export function getAuthSession(): AuthSession | null {
  return null;
}

export function setAuthSession(email: string): void {
  void email;
}

export function clearAuthSession(): void {
  // Supabase session is handled by auth client; no local auth record to clear.
}

export function getRemainingPlans(session: AuthSession | null): number {
  const usage = readUsage();
  if (!session) {
    return Math.max(0, GUEST_DAILY_LIMIT - usage.guestUsed);
  }
  return getLocalSignedInRemaining(session.email);
}

export function consumePlan(session: AuthSession | null): number {
  const usage = readUsage();
  if (!session) {
    usage.guestUsed += 1;
    writeUsage(usage);
    return Math.max(0, GUEST_DAILY_LIMIT - usage.guestUsed);
  }
  return consumeLocalSignedInPlan(session.email);
}

export function getLimitMessage(session: AuthSession | null): string {
  const remaining = getRemainingPlans(session);
  if (!session) {
    return `Guest: ${remaining}/${GUEST_DAILY_LIMIT} plans left`;
  }
  return `${session.email} · ${remaining}/${AUTH_DAILY_LIMIT} plans left today`;
}

export async function getRemainingPlansAsync(session: AuthSession | null): Promise<number> {
  if (!session) {
    return getRemainingPlans(null);
  }
  if (!session.userId) {
    return getLocalSignedInRemaining(session.email);
  }

  try {
    const supabase = await getSupabaseClient();
    const { data, error } = await supabase
      .from(USER_DAILY_USAGE_TABLE)
      .select("count")
      .eq("user_id", session.userId)
      .eq("usage_date", todayKey())
      .maybeSingle();

    if (error) {
      return getLocalSignedInRemaining(session.email);
    }

    const used = data?.count ?? 0;
    return Math.max(0, AUTH_DAILY_LIMIT - used);
  } catch {
    return getLocalSignedInRemaining(session.email);
  }
}

export async function consumePlanAsync(session: AuthSession | null): Promise<number> {
  if (!session) {
    return consumePlan(null);
  }
  if (!session.userId) {
    return consumeLocalSignedInPlan(session.email);
  }

  try {
    const supabase = await getSupabaseClient();
    const { data, error } = await supabase
      .from(USER_DAILY_USAGE_TABLE)
      .select("count")
      .eq("user_id", session.userId)
      .eq("usage_date", todayKey())
      .maybeSingle();

    if (error) {
      return consumeLocalSignedInPlan(session.email);
    }

    const nextCount = (data?.count ?? 0) + 1;
    const { error: upsertError } = await supabase.from(USER_DAILY_USAGE_TABLE).upsert(
      {
        user_id: session.userId,
        usage_date: todayKey(),
        count: nextCount,
      },
      { onConflict: "user_id,usage_date" },
    );

    if (upsertError) {
      return consumeLocalSignedInPlan(session.email);
    }

    return Math.max(0, AUTH_DAILY_LIMIT - nextCount);
  } catch {
    return consumeLocalSignedInPlan(session.email);
  }
}
