import { useState } from "react";
import type { PracticeInfo } from "../types";
import { lookupNpi } from "../api";

const DEMO_NPIS = [
  { npi: "1234567890", label: "Family Med" },
  { npi: "9876543210", label: "Cardiology" },
  { npi: "5551234567", label: "Pediatrics" },
];

interface Props {
  onFound: (practice: PracticeInfo) => void;
}

export default function NpiLookup({ onFound }: Props) {
  const [npi, setNpi] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLookup() {
    if (!/^\d{10}$/.test(npi)) {
      setError("Enter a valid 10-digit NPI.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const practice = await lookupNpi(npi);
      onFound(practice);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection error.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h2>Identify Your Practice</h2>
      <p className="sub">
        Enter your NPI and we'll pull your details from the national registry.
      </p>

      <div className="input-row">
        <input
          type="text"
          value={npi}
          onChange={(e) => setNpi(e.target.value.replace(/\D/g, "").slice(0, 10))}
          onKeyDown={(e) => e.key === "Enter" && handleLookup()}
          placeholder="10-digit NPI number"
          maxLength={10}
          autoFocus
        />
        <button
          className="btn btn-primary"
          onClick={handleLookup}
          disabled={loading}
        >
          {loading ? "Looking up\u2026" : "Look Up"}
        </button>
      </div>

      <div className="hint">
        Demo:{" "}
        {DEMO_NPIS.map((d, i) => (
          <span key={d.npi}>
            {i > 0 && " · "}
            <code onClick={() => setNpi(d.npi)}>
              {d.npi}
            </code>{" "}
            {d.label}
          </span>
        ))}
      </div>

      {error && <div className="error">{error}</div>}
    </div>
  );
}
