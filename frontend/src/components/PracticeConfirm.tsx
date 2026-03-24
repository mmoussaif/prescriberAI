import type { PracticeInfo } from "../types";

interface Props {
  practice: PracticeInfo;
  onConfirm: () => void;
  onBack: () => void;
}

export default function PracticeConfirm({ practice, onConfirm, onBack }: Props) {
  return (
    <div className="card">
      <h2>Confirm Your Practice</h2>
      <p className="sub">We found this in the NPI registry. Does it look right?</p>

      <div className="practice-card">
        <h3>{practice.practice_name}</h3>
        <div className="row">
          <span>Address:</span> {practice.address}
        </div>
        <div className="row">
          <span>Specialty:</span> {practice.specialty}
        </div>
        <div className="row">
          <span>NPI:</span> {practice.npi}
        </div>
        <div className="chips">
          {practice.providers.map((p) => (
            <span key={p.npi} className="chip">
              {p.name} · {p.role}
            </span>
          ))}
        </div>
      </div>

      <div className="actions">
        <button className="btn btn-primary" onClick={onConfirm}>
          Yes, that's us
        </button>
        <button className="btn btn-outline" onClick={onBack}>
          Try again
        </button>
      </div>
    </div>
  );
}
