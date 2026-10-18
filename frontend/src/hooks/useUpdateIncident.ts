import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { ApiError } from "../api/client";
import { patchIncident } from "../api/incidents";
import type { Incident, IncidentChanges } from "../api/types";
import { incidentKeys } from "./useIncidents";

type Vars = { incident: Incident; analyst: string; changes: IncidentChanges };
type Ctx = { previous?: Incident };

export function useUpdateIncident() {
  const qc = useQueryClient();

  return useMutation<Incident, ApiError, Vars, Ctx>({
    mutationFn: ({ incident, analyst, changes }) =>
      patchIncident(incident.id, analyst, { expected_version: incident.version, ...changes }),

    // Antes da resposta: mostra o resultado esperado e guarda o estado anterior.
    onMutate: async ({ incident, analyst, changes }) => {
      const key = incidentKeys.detail(incident.id);
      await qc.cancelQueries({ queryKey: incidentKeys.all }); // um poll em voo não pode sobrescrever o otimista
      const previous = qc.getQueryData<Incident>(key);
      const assigned_to =
        changes.status === "Em Investigação" ? analyst
        : changes.status === "Aberto" ? null
        : incident.assigned_to;
      qc.setQueryData<Incident>(key, { ...incident, ...changes, assigned_to, allowed_transitions: [] });
      return { previous };
    },

    onError: (err, { incident }, ctx) => {
      const key = incidentKeys.detail(incident.id);
      if (err.code === "version_conflict" && err.current) {
        qc.setQueryData(key, err.current as Incident); // o dado novo já vem no 409
      } else if (ctx?.previous) {
        qc.setQueryData(key, ctx.previous); // rollback
      }
    },

    onSuccess: (saved) => qc.setQueryData(incidentKeys.detail(saved.id), saved),

    // Sempre recarrega do servidor: a verdade é dele, não do cache.
    onSettled: () => qc.invalidateQueries({ queryKey: incidentKeys.all }),
  });
}