import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getIncident, getSummary, listIncidents } from "../api/incidents";
import type { Filters } from "../api/types";

const POLL_MS = 10_000;

export const incidentKeys = {
  all: ["incidents"] as const,
  list: (f: Filters) => ["incidents", "list", f] as const,
  summary: ["incidents", "summary"] as const,
  detail: (id: number) => ["incidents", "detail", id] as const,
};

export function useIncidents(filters: Filters) {
  return useQuery({
    queryKey: incidentKeys.list(filters),
    queryFn: ({ signal }) => listIncidents(filters, signal),
    placeholderData: keepPreviousData,
    refetchInterval: POLL_MS,
  });
}

export function useSummary() {
  return useQuery({
    queryKey: incidentKeys.summary,
    queryFn: ({ signal }) => getSummary(signal),
    refetchInterval: POLL_MS,
  });
}

export function useIncident(id: number) {
  return useQuery({
    queryKey: incidentKeys.detail(id),
    queryFn: ({ signal }) => getIncident(id, signal),
    refetchInterval: POLL_MS,
  });
}