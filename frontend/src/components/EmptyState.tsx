export function EmptyState({ filtered, onClear }: { filtered: boolean; onClear: () => void }) {
  return (
    <div className="state">
      <p><strong>{filtered ? "Nenhum incidente com esses filtros." : "Nenhum incidente ativo."}</strong></p>
      {filtered && <button className="btn" onClick={onClear}>Limpar filtros</button>}
    </div>
  );
}