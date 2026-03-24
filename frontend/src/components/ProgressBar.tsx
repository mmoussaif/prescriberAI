const TOTAL_STEPS = 3;

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
