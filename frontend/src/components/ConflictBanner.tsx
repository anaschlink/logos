import type { Incident } from "../api/types";

export function ConflictBanner({ incident }: { incident: Incident }) {
  return (
    <div className="notice" role="alert">
      <strong>Este incidente foi atualizado por outra pessoa.</strong> Seus dados foram substituídos
      pelos atuais: status <em>{incident.status}</em>, responsável {incident.assigned_to ?? "ninguém"}.
      Confira e repita a ação, se ainda fizer sentido.
    </div>
  );
}