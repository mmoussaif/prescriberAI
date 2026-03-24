import type { ConfiguredAccount } from "./types";

const STORAGE_KEY = "prescriberpoint_onboarding_accounts_v1";

function safeParse(raw: string | null): ConfiguredAccount[] {
  if (!raw) return [];
  try {
    const data = JSON.parse(raw) as unknown;
    if (!Array.isArray(data)) return [];
    return data.filter(isConfiguredAccount);
  } catch {
    return [];
  }
}

function isConfiguredAccount(x: unknown): x is ConfiguredAccount {
  if (!x || typeof x !== "object") return false;
  const o = x as Record<string, unknown>;
  return (
    typeof o.npi === "string" &&
    typeof o.practice_name === "string" &&
    typeof o.completedAt === "string" &&
    typeof o.summaryText === "string" &&
    Array.isArray(o.providers)
  );
}

export function loadConfiguredAccounts(): ConfiguredAccount[] {
  return safeParse(localStorage.getItem(STORAGE_KEY)).sort(
    (a, b) =>
      new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime(),
  );
}

export function saveConfiguredAccount(account: ConfiguredAccount): void {
  const list = loadConfiguredAccounts().filter((a) => a.npi !== account.npi);
  list.push(account);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  } catch {
    /* quota or private mode */
  }
}

export function removeConfiguredAccount(npi: string): void {
  const list = loadConfiguredAccounts().filter((a) => a.npi !== npi);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}