import type { ConfiguredAccount } from "../types";

interface Props {
  accounts: ConfiguredAccount[];
  onAddPractice: () => void;
  onOpenAccount: (account: ConfiguredAccount) => void;
  onRemoveAccount: (npi: string) => void;
}

function formatCompleted(iso: string) {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

function snippet(text: string, max = 72) {
  const line = text.replace(/\s+/g, " ").trim();
  if (line.length <= max) return line;
  return `${line.slice(0, max - 1)}…`;
}

export default function AccountsHome({
  accounts,
  onAddPractice,
  onOpenAccount,
  onRemoveAccount,
}: Props) {
  const hasAccounts = accounts.length > 0;

  return (
    <div className="accounts-home">
      <div className="accounts-home-head">
        <h2>Your practices</h2>
        {hasAccounts && (
          <>
            <p className="sub">
              Open a card for the summary, or add another practice below.
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={onAddPractice}
            >
              Configure a practice
            </button>
          </>
        )}
      </div>

      {accounts.length === 0 ? (
        <div className="accounts-empty card">
          <p className="accounts-empty-title">No accounts yet</p>
          <p className="sub">
            Look up an NPI and walk through the AI steps. Nothing is stored until
            you reach the setup complete screen.
          </p>
          <button type="button" className="btn btn-primary" onClick={onAddPractice}>
            Configure a practice
          </button>
        </div>
      ) : (
        <div className="accounts-grid" role="list">
          {accounts.map((acc) => (
            <article
              key={acc.npi}
              className="account-card"
              role="listitem"
            >
              <button
                type="button"
                className="account-card-main"
                onClick={() => onOpenAccount(acc)}
              >
                <span className="account-card-badge">Configured</span>
                <h3>{acc.practice_name}</h3>
                <p className="account-card-meta">
                  NPI {acc.npi} · {acc.specialty}
                </p>
                <p className="account-card-address">{acc.address}</p>
                <p className="account-card-snippet">{snippet(acc.summaryText)}</p>
                <time className="account-card-date" dateTime={acc.completedAt}>
                  {formatCompleted(acc.completedAt)}
                </time>
              </button>
              <button
                type="button"
                className="account-card-remove"
                title="Remove from this list"
                aria-label={`Remove ${acc.practice_name}`}
                onClick={(e) => {
                  e.stopPropagation();
                  if (
                    window.confirm(
                      `Remove “${acc.practice_name}” from your saved list? This only clears this browser.`,
                    )
                  ) {
                    onRemoveAccount(acc.npi);
                  }
                }}
              >
                Remove
              </button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
