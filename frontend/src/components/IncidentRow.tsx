import { memo } from "react";
import type { Incident } from "../api/types";
import { CAT_ICON, SEV_ICON, timeAgo } from "../lib/meta";

type Props = { incident: Incident; selected: boolean; onSelect: (id: number) => void };

export const IncidentRow = memo(function IncidentRow({ incident: i, selected, onSelect }: Props) {
  return (
    <li>
      <button className="row" data-sev={i.severity} aria-current={selected} onClick={() => onSelect(i.id)}>
        <span className="bar" />
        <span className="badge"><span aria-hidden>{SEV_ICON[i.severity]}</span> {i.severity}</span>
        <span><span aria-hidden>{CAT_ICON[i.category]}</span> {i.title}</span>
        <span className="muted extra">{i.location}</span>
        <span className="muted extra">{timeAgo(i.created_at)}</span>
        <span>{i.status}</span>
        <span className="muted extra">{i.assigned_to ?? "—"}</span>
      </button>
    </li>
  );
});