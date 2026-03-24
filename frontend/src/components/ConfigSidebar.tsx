import { CONFIG_AREAS } from "../types";

interface Props {
  activePhase: string;
  completedPhases: Map<string, string>;
  loading: boolean;
  onRevise: (phaseKey: string, phaseLabel: string) => void;
}

export default function ConfigSidebar({ activePhase, completedPhases, loading, onRevise }: Props) {
  return (
    <div className="config-sidebar">
      <h3 className="sidebar-title">Configuration</h3>
      <div className="config-list">
        {CONFIG_AREAS.map(({ key, label }) => {
          const done = completedPhases.has(key);
          const active = key === activePhase && !done;
          const value = completedPhases.get(key);
          const canRevise = done && !loading;

          return (
            <div
              key={key}
              className={`config-item${done ? " done" : ""}${active ? " active" : ""}${canRevise ? " revisable" : ""}`}
              onClick={canRevise ? () => onRevise(key, label) : undefined}
              title={canRevise ? `Click to revise ${label}` : undefined}
            >
              <div className="config-indicator">
                {done ? (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="7" r="7" fill="var(--success)" />
                    <path d="M4 7l2 2 4-4" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : active ? (
                  <div className="indicator-active" />
                ) : (
                  <div className="indicator-pending" />
                )}
              </div>
              <div className="config-content">
                <div className="config-label">
                  {label}
                  {canRevise && <span className="revise-hint">edit</span>}
                </div>
                {done && value && (
                  <div className="config-value">{value}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
