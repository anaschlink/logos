import { buildQuery, request } from "./client";
import type { Filters, Incident, IncidentChanges, Summary } from "./types";

export const listIncidents = (f: Filters, signal?: AbortSignal) =>
  request<Incident[]>(
    `/incidents${buildQuery({
      severity: f.severity,
      category: f.category,
      status: f.status,
      q: f.q.trim().slice(0, 100),
    })}`,
    { signal },
  );

export const getSummary = (signal?: AbortSignal) =>
  request<Summary>("/incidents/summary", { signal });

export const getIncident = (id: number, signal?: AbortSignal) =>
  request<Incident>(`/incidents/${id}`, { signal });

export const patchIncident = (
  id: number,
  analyst: string,
  body: IncidentChanges & { expected_version: number },
) => request<Incident>(`/incidents/${id}`, { method: "PATCH", body, analyst });