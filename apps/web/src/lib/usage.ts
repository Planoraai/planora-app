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
export const GUEST_FREE_PLAN_LIMIT = 2;
export const DAILY_USER_PLAN_LIMIT = 5;

const AUTH_SESSION_KEY = "planora.auth.session";
const GUEST_USAGE_KEY = "planora.usage.guest.total";
const USER_USAGE_KEY = "planora.usage.user.daily";

export type AuthSession = {
  userId: string;
  email: string;
};

type UserUsageMap = Record<string, { date: string; count: number }>;

function todayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  const raw = window.localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function getAuthSession(): AuthSession | null {
  return readJson<AuthSession | null>(AUTH_SESSION_KEY, null);
}

export function setAuthSession(email: string): AuthSession {
  const normalized = email.trim().toLowerCase();
  const session: AuthSession = {
    email: normalized,
    userId: normalized,
  };
  writeJson(AUTH_SESSION_KEY, session);
  return session;
}

export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(AUTH_SESSION_KEY);
}

export function getGuestPlansUsed(): number {
  return readJson<number>(GUEST_USAGE_KEY, 0);
}

export function incrementGuestPlansUsed(): number {
  const next = getGuestPlansUsed() + 1;
  writeJson(GUEST_USAGE_KEY, next);
  return next;
}

export function getUserPlansUsedToday(userId: string): number {
  const usageMap = readJson<UserUsageMap>(USER_USAGE_KEY, {});
  const current = usageMap[userId];
  if (!current) return 0;
  if (current.date !== todayKey()) return 0;
  return current.count;
}

export function incrementUserPlansUsedToday(userId: string): number {
  const usageMap = readJson<UserUsageMap>(USER_USAGE_KEY, {});
  const count = getUserPlansUsedToday(userId) + 1;
  usageMap[userId] = { date: todayKey(), count };
  writeJson(USER_USAGE_KEY, usageMap);
  return count;
}

export function getRemainingPlans(session: AuthSession | null): number {
  if (!session) {
    return Math.max(0, GUEST_FREE_PLAN_LIMIT - getGuestPlansUsed());
  }
  return Math.max(0, DAILY_USER_PLAN_LIMIT - getUserPlansUsedToday(session.userId));
}

export function getLimitMessage(session: AuthSession | null): string {
  if (!session) {
    return `Free plans remaining: ${getRemainingPlans(null)} of ${GUEST_FREE_PLAN_LIMIT}`;
  }
  return `Daily plans remaining: ${getRemainingPlans(session)} of ${DAILY_USER_PLAN_LIMIT}`;
}

export function consumePlan(session: AuthSession | null): number {
  if (!session) {
    incrementGuestPlansUsed();
    return getRemainingPlans(null);
  }
  incrementUserPlansUsedToday(session.userId);
  return getRemainingPlans(session);
}
