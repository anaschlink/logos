import type { ApiError } from "../api/client";

export function ErrorState({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  const msg = (error as ApiError)?.message ?? "Erro inesperado.";
  return (
    <div className="state" role="alert">
      <p><strong>Não foi possível carregar os incidentes.</strong></p>
      <p className="muted">{msg}</p>
      <button className="btn primary" onClick={onRetry}>Tentar de novo</button>
    </div>
  );
}