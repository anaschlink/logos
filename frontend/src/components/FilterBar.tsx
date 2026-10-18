import { CATEGORIES, STATUSES, type Category, type Filters, type Status } from "../api/types";

type Props = { filters: Filters; onChange: (f: Filters) => void; onClear: () => void; canClear: boolean };

export function FilterBar({ filters, onChange, onClear, canClear }: Props) {
  return (
    <div className="filters">
      <input
        type="search"
        placeholder="Buscar por título, local ou veículo"
        aria-label="Buscar incidentes"
        maxLength={100}
        value={filters.q}
        onChange={(e) => onChange({ ...filters, q: e.target.value })}
      />
      <select
        aria-label="Categoria"
        value={filters.category[0] ?? ""}
        onChange={(e) => onChange({ ...filters, category: e.target.value ? [e.target.value as Category] : [] })}
      >
        <option value="">Todas as categorias</option>
        {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
      </select>
      <select
        aria-label="Status"
        value={filters.status[0] ?? ""}
        onChange={(e) => onChange({ ...filters, status: e.target.value ? [e.target.value as Status] : [] })}
      >
        <option value="">Status: ativos</option>
        {STATUSES.map((s) => <option key={s}>{s}</option>)}
      </select>
      <button className="btn" onClick={onClear} disabled={!canClear}>Limpar</button>
    </div>
  );
}