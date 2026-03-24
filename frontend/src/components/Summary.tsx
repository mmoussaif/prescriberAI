import type { PracticeInfo } from "../types";
import ScheduleCallLink from "./ScheduleCallLink";

interface Props {
  practice: PracticeInfo;
  summaryText: string;
}

function extractSummary(text: string) {
  const idx = text.toUpperCase().indexOf("CONFIGURATION COMPLETE");
  return idx >= 0 ? text.substring(idx) : text;
}

function stripBold(text: string) {
  return text.replace(/\*\*(.*?)\*\*/g, "$1");
}

export default function Summary({ practice, summaryText }: Props) {
  const config = stripBold(extractSummary(summaryText));

  return (
    <div className="card">
      <h2>&#x2713; Setup Complete</h2>
      <p className="sub">
        Your PrescriberPoint account is configured and ready.
      </p>

      <div className="practice-card" style={{ marginBottom: 12 }}>
        <h3>{practice.practice_name}</h3>
        <div className="row">
          <span>Specialty:</span> {practice.specialty}
        </div>
        <div className="row">
          <span>Providers:</span> {practice.providers.length}
        </div>
      </div>

      <div className="summary-box">
        <h3>Configuration Summary</h3>
        <pre>{config}</pre>
      </div>

      <div className="actions">
        <button
          className="btn btn-success"
          onClick={() =>
            alert("In production: launches the PrescriberPoint dashboard.")
          }
        >
          Go to Dashboard
        </button>
        <ScheduleCallLink label="Schedule Walkthrough" variant="md" />
      </div>
    </div>
  );
}
