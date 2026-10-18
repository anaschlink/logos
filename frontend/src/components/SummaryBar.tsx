import { SEVERITIES, type Severity, type Summary } from "../api/types";
import { SEV_ICON } from "../lib/meta";

type Props = { summary?: Summary; active: Severity[]; onToggle: (s: Severity) => void };

export function SummaryBar({ summary, active, onToggle }: Props) {
  return (
    <div className="chips" role="group" aria-label="Filtrar por criticidade">
      {SEVERITIES.map((s) => (
        <button key={s} className="chip" data-sev={s} aria-pressed={active.includes(s)} onClick={() => onToggle(s)}>
          <span aria-hidden>{SEV_ICON[s]}</span> {s} <strong>{summary ? summary.by_severity[s] : "–"}</strong>
        </button>
      ))}
      {summary && <span className="muted">{summary.total} ativos</span>}
    </div>
  );
}