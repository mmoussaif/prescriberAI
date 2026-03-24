const TOTAL_STEPS = 3;

/** `current` is the count of completed segments (0–3). When current === TOTAL_STEPS, every bar is “done” (e.g. summary / setup complete). */
export default function ProgressBar({ current }: { current: number }) {
  return (
    <div className="progress">
      {Array.from({ length: TOTAL_STEPS }, (_, i) => (
        <div
          key={i}
          className={`step${i < current ? " done" : i === current ? " active" : ""}`}
        />
      ))}
    </div>
  );
}
