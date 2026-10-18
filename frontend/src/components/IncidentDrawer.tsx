import { useEffect } from "react";
import type { Analyst, Status } from "../api/types";
import { useIncident } from "../hooks/useIncidents";
import { useUpdateIncident } from "../hooks/useUpdateIncident";
import { CAT_ICON, SEV_ICON, actionLabel } from "../lib/meta";
import { ConflictBanner } from "./ConflictBanner";
import { ErrorState } from "./ErrorState";

type Props = { id: number; analyst: Analyst; onClose: () => void };

// Use com key={id} no pai: trocar de incidente remonta o drawer e zera o erro da mutação.
export function IncidentDrawer({ id, analyst, onClose }: Props) {
  const { data: incident, isPending, error, refetch } = useIncident(id);
  const update = useUpdateIncident();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const move = (status: Status) => incident && update.mutate({ incident, analyst, changes: { status } });
  const err = update.error;

  const lockedByOther =
  !!incident &&
  incident.status === "Em Investigação" &&
  incident.assigned_to !== null &&
  incident.assigned_to !== analyst;


  return (
    <aside className="drawer" role="dialog" aria-label="Detalhes do incidente">
      <button className="btn" onClick={onClose}>Fechar ✕</button>

      {isPending && <p className="muted">Carregando…</p>}
      {error && !incident && <ErrorState error={error} onRetry={() => refetch()} />}

      {incident && (
        <div data-sev={incident.severity}>
          <h2>{incident.title}</h2>
          <span className="badge"><span aria-hidden>{SEV_ICON[incident.severity]}</span> {incident.severity}</span>

          <dl>
            <dt>Categoria</dt><dd><span aria-hidden>{CAT_ICON[incident.category]}</span> {incident.category}</dd>
            <dt>Status</dt><dd>{incident.status}</dd>
            <dt>Responsável</dt><dd>{incident.assigned_to ?? "—"}</dd>
            <dt>Local</dt><dd>{incident.location}</dd>
            <dt>Veículo</dt><dd>{incident.vehicle_id}</dd>
            <dt>Descrição</dt><dd>{incident.description}</dd>
          </dl>

          {err?.code === "version_conflict" && <ConflictBanner incident={incident} />}
          {err && err.code !== "version_conflict" && (
            <p className="alert" role="alert">
              {err.status === 0
                ? "Falha de rede. Recarregamos o incidente: confira o estado antes de tentar de novo."
                : err.message}
            </p>
          )}
          {update.isPending && <p className="muted" aria-live="polite">Salvando…</p>}

          {lockedByOther ? (
            <p className="muted" role="status">
              Em investigação por {incident.assigned_to}. Só o responsável pode alterar.
            </p>
          ) : (
            <div className="actions">
              {incident.allowed_transitions.map((s) => (
                <button key={s} className="btn primary" disabled={update.isPending} onClick={() => move(s)}>
                  {actionLabel(incident.status, s)}
                </button>
              ))}
              {incident.allowed_transitions.length === 0 && !update.isPending && (
                <span className="muted">Nenhuma ação disponível neste status.</span>
              )}
            </div>
          )}
        </div>
      )}
    </aside>
  );
}