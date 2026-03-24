import { useEffect, useState } from "react";
import type { ConfiguredAccount, PracticeInfo, Step } from "./types";
import ProgressBar from "./components/ProgressBar";
import NpiLookup from "./components/NpiLookup";
import PracticeConfirm from "./components/PracticeConfirm";
import Chat from "./components/Chat";
import Summary from "./components/Summary";
import AccountsHome from "./components/AccountsHome";
import {
  loadConfiguredAccounts,
  removeConfiguredAccount,
  saveConfiguredAccount,
} from "./configuredAccountsStorage";

/** Segment i is green when i < current; blue when i === current. Summary is done, so use 3 so all 3 bars are green (indices 0–2). */
const WIZARD_PROGRESS: Record<Exclude<Step, "home">, number> = {
  npi: 0,
  confirm: 1,
  chat: 1,
  summary: 3,
};

export default function App() {
  const [step, setStep] = useState<Step>("home");
  const [practice, setPractice] = useState<PracticeInfo | null>(null);
  const [summaryText, setSummaryText] = useState("");
  const [accounts, setAccounts] = useState<ConfiguredAccount[]>(() =>
    loadConfiguredAccounts(),
  );

  useEffect(() => {
    if (step === "home") setAccounts(loadConfiguredAccounts());
  }, [step]);

  function goDashboard() {
    setStep("home");
    setPractice(null);
    setSummaryText("");
  }

  function openStoredAccount(acc: ConfiguredAccount) {
    setPractice({
      npi: acc.npi,
      practice_name: acc.practice_name,
      address: acc.address,
      specialty: acc.specialty,
      providers: acc.providers,
    });
    setSummaryText(acc.summaryText);
    setStep("summary");
  }

  function handleRemoveAccount(npi: string) {
    removeConfiguredAccount(npi);
    setAccounts(loadConfiguredAccounts());
  }

  const wideLayout = step === "chat" || step === "home";

  return (
    <div className={`container${wideLayout ? " container-wide" : ""}`}>
      <header className="header">
        <div className="header-top">
          <div className="brand">PrescriberPoint</div>
          {step !== "home" && (
            <button
              type="button"
              className="header-dashboard-link"
              onClick={goDashboard}
            >
              Dashboard
            </button>
          )}
        </div>
        {step === "home" ? (
          <h1>Dashboard</h1>
        ) : (
          <>
            <h1>AI Practice Onboarding</h1>
            <p>Get your practice configured and running in minutes, not days.</p>
          </>
        )}
      </header>

      {step !== "home" && (
        <ProgressBar current={WIZARD_PROGRESS[step as Exclude<Step, "home">]} />
      )}

      {step === "home" && (
        <AccountsHome
          accounts={accounts}
          onAddPractice={() => {
            setPractice(null);
            setSummaryText("");
            setStep("npi");
          }}
          onOpenAccount={openStoredAccount}
          onRemoveAccount={handleRemoveAccount}
        />
      )}

      {step === "npi" && (
        <NpiLookup
          onFound={(p) => {
            setPractice(p);
            setStep("confirm");
          }}
        />
      )}

      {step === "confirm" && practice && (
        <PracticeConfirm
          practice={practice}
          onConfirm={() => setStep("chat")}
          onBack={() => {
            setPractice(null);
            setStep("npi");
          }}
        />
      )}

      {step === "chat" && practice && (
        <Chat
          practice={practice}
          onComplete={(text) => {
            setSummaryText(text);
            saveConfiguredAccount({
              ...practice,
              completedAt: new Date().toISOString(),
              summaryText: text,
            });
            setStep("summary");
          }}
        />
      )}

      {step === "summary" && practice && (
        <Summary
          practice={practice}
          summaryText={summaryText}
          onGoDashboard={goDashboard}
        />
      )}
    </div>
  );
}
