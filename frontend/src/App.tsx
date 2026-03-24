import { useState } from "react";
import type { PracticeInfo, Step } from "./types";
import ProgressBar from "./components/ProgressBar";
import NpiLookup from "./components/NpiLookup";
import PracticeConfirm from "./components/PracticeConfirm";
import Chat from "./components/Chat";
import Summary from "./components/Summary";

const STEP_INDEX: Record<Step, number> = {
  npi: 0,
  confirm: 1,
  chat: 1,
  summary: 2,
};

export default function App() {
  const [step, setStep] = useState<Step>("npi");
  const [practice, setPractice] = useState<PracticeInfo | null>(null);
  const [summaryText, setSummaryText] = useState("");

  return (
    <div className={`container${step === "chat" ? " container-wide" : ""}`}>
      <header className="header">
        <div className="brand">PrescriberPoint</div>
        <h1>AI Practice Onboarding</h1>
        <p>Get your practice configured and running in minutes, not days.</p>
      </header>

      <ProgressBar current={STEP_INDEX[step]} />

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
            setStep("summary");
          }}
        />
      )}

      {step === "summary" && practice && (
        <Summary practice={practice} summaryText={summaryText} />
      )}
    </div>
  );
}
