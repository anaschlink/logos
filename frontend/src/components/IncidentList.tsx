import type { Incident } from "../api/types";
import { IncidentRow } from "./IncidentRow";

type Props = { incidents: Incident[]; selectedId: number | null; onSelect: (id: number) => void };

export function IncidentList({ incidents, selectedId, onSelect }: Props) {
  return (
    <ul className="list">
      {incidents.map((i) => (
        <IncidentRow key={i.id} incident={i} selected={i.id === selectedId} onSelect={onSelect} />
      ))}
    </ul>
  );
}