export type Question = {
  id: string;
  type: "single_select" | "multi_select" | "scale";
  label: string;
  options?: string[];
  min?: number;
  max?: number;
  required?: boolean;
};

export type Protocol = {
  id: string;
  label: string;
  specialty: string;
  questions: Question[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function fetchProtocol(protocolId: string): Promise<Protocol> {
  const res = await fetch(`${API_BASE}/protocols/${protocolId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to load protocol ${protocolId}`);
  }
  return (await res.json()) as Protocol;
}

export async function submitIntake(payload: {
  patient_id: string;
  chief_complaint: string;
  answers: Record<string, unknown>;
}) {
  const res = await fetch(`${API_BASE}/intake/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error("Intake submission failed");
  }
  return res.json();
}
