import { useState } from "react";
import { getSpecialistPhone } from "../specialistPhone";

type Props = {
  label: string;
  /** If set, used for `tel:` when env phone is unset (e.g. escalation banner). */
  dialPhone?: string;
  variant?: "sm" | "md";
};

/** Prefer <a href="tel:…"> so clicks work in more environments than programmatic navigation. */
export default function ScheduleCallLink({
  label,
  dialPhone,
  variant = "md",
}: Props) {
  const [showHint, setShowHint] = useState(false);
  const fromProp = dialPhone?.replace(/\s/g, "").trim() ?? "";
  const phone =
    fromProp.length > 0 ? fromProp : getSpecialistPhone();
  const btnClass =
    variant === "sm" ? "btn btn-outline btn-sm" : "btn btn-outline";

  if (phone) {
    return (
      <div className="schedule-call-wrap">
        <a href={`tel:${phone}`} className={btnClass}>
          {label}
        </a>
      </div>
    );
  }

  return (
    <div className="schedule-call-wrap">
      <button
        type="button"
        className={btnClass}
        onClick={() => setShowHint((v) => !v)}
      >
        {label}
      </button>
      {showHint && (
        <p className="schedule-call-hint" role="status">
          Add <code>frontend/.env</code> with{" "}
          <code>VITE_SPECIALIST_PHONE=+15551234567</code> (your real number), then
          restart <code>npm run dev</code>. Plain <code>alert()</code> is hidden in
          some embedded browsers, so we show this message here instead.
        </p>
      )}
    </div>
  );
}
