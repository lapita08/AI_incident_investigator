import type { Evidence, Hypothesis, Incident, RecommendedAction, TimelineEvent } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return (await response.json()) as T;
}

export const api = {
  incidents: () => request<Incident[]>("/api/v1/incidents"),
  incident: (id: string) => request<Incident>(`/api/v1/incidents/${id}`),
  createIncident: (payload: Partial<Incident>) =>
    request<Incident>("/api/v1/incidents", { method: "POST", body: JSON.stringify(payload) }),
  loadSample: (scenarioId: string) => request<Incident>(`/api/v1/incidents/sample/${scenarioId}`, { method: "POST" }),
  evidence: (incidentId: string) => request<Evidence[]>(`/api/v1/incidents/${incidentId}/evidence`),
  addEvidence: (incidentId: string, payload: Record<string, unknown>) =>
    request(`/api/v1/incidents/${incidentId}/evidence`, { method: "POST", body: JSON.stringify(payload) }),
  analyze: (incidentId: string) => request<{ status: string; report: Record<string, unknown> }>(`/api/v1/incidents/${incidentId}/analyze`, { method: "POST" }),
  timeline: (incidentId: string) => request<TimelineEvent[]>(`/api/v1/incidents/${incidentId}/timeline`),
  hypotheses: (incidentId: string) => request<Hypothesis[]>(`/api/v1/incidents/${incidentId}/hypotheses`),
  updateHypothesis: (incidentId: string, hypothesisId: string, status: string) =>
    request<Hypothesis>(`/api/v1/incidents/${incidentId}/hypotheses/${hypothesisId}`, { method: "PATCH", body: JSON.stringify({ status }) }),
  actions: (incidentId: string) => request<RecommendedAction[]>(`/api/v1/incidents/${incidentId}/actions`),
  communications: (incidentId: string) => request<Record<string, string | boolean>>(`/api/v1/incidents/${incidentId}/communications`, { method: "POST" }),
  postmortem: (incidentId: string) => request<Record<string, unknown>>(`/api/v1/incidents/${incidentId}/postmortem`, { method: "POST" }),
  exportJson: (incidentId: string) => request<Record<string, unknown>>(`/api/v1/incidents/${incidentId}/export`)
};

