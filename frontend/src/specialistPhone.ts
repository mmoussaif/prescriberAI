/** Normalized E.164-ish value from Vite env, or null if unset. */
export function getSpecialistPhone(): string | null {
  const raw = import.meta.env.VITE_SPECIALIST_PHONE as string | undefined;
  const phone = raw?.replace(/\s/g, "").trim() ?? "";
  return phone.length > 0 ? phone : null;
}
