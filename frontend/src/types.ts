export interface Provider {
  name: string;
  role: string;
  npi: string;
}

export interface PracticeInfo {
  npi: string;
  practice_name: string;
  address: string;
  specialty: string;
  providers: Provider[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatApiResponse {
  response: string;
  current_phase: string;
  needs_escalation: boolean;
}

export interface ConfigEntry {
  label: string;
  value: string;
}

export const CONFIG_AREAS: { key: string; label: string }[] = [
  { key: "patient_demographics", label: "Patient Demographics" },
  { key: "prescribing_focus", label: "Prescribing Focus" },
  { key: "prior_auth", label: "Prior Authorization" },
  { key: "sample_management", label: "Sample Management" },
  { key: "coverage_affordability", label: "Coverage & Affordability" },
  { key: "provider_roles", label: "Provider Roles" },
];

export type Step = "npi" | "confirm" | "chat" | "summary";
