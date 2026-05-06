export type AuthSession = {
  email: string;
};

const AUTH_KEY = "planora.auth.session";
const USAGE_KEY = "planora.usage.daily";
const GUEST_DAILY_LIMIT = 2;
const AUTH_DAILY_LIMIT = 5;

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

export function getAuthSession(): AuthSession | null {
  if (!isBrowser()) return null;
  try {
    const raw = window.localStorage.getItem(AUTH_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthSession;
    if (!parsed.email) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function setAuthSession(email: string): void {
  if (!isBrowser()) return;
  const session: AuthSession = { email: email.trim().toLowerCase() };
  window.localStorage.setItem(AUTH_KEY, JSON.stringify(session));
}

export function clearAuthSession(): void {
  if (!isBrowser()) return;
  window.localStorage.removeItem(AUTH_KEY);
}

export function getRemainingPlans(session: AuthSession | null): number {
  const usage = readUsage();
  if (!session) {
    return Math.max(0, GUEST_DAILY_LIMIT - usage.guestUsed);
  }
  const used = usage.userUsed[session.email] || 0;
  return Math.max(0, AUTH_DAILY_LIMIT - used);
}

export function consumePlan(session: AuthSession | null): number {
  const usage = readUsage();
  if (!session) {
    usage.guestUsed += 1;
    writeUsage(usage);
    return Math.max(0, GUEST_DAILY_LIMIT - usage.guestUsed);
  }
  usage.userUsed[session.email] = (usage.userUsed[session.email] || 0) + 1;
  writeUsage(usage);
  return Math.max(0, AUTH_DAILY_LIMIT - usage.userUsed[session.email]);
}

export function getLimitMessage(session: AuthSession | null): string {
  const remaining = getRemainingPlans(session);
  if (!session) {
    return `Guest: ${remaining}/${GUEST_DAILY_LIMIT} plans left`;
  }
  return `${session.email} · ${remaining}/${AUTH_DAILY_LIMIT} plans left today`;
}
