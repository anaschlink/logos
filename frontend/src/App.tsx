import { useMemo, useState } from "react";
import { EMPTY_FILTERS, type Filters, type Severity } from "./api/types";
import { EmptyState } from "./components/EmptyState";
import { ErrorState } from "./components/ErrorState";
import { FilterBar } from "./components/FilterBar";
import { Header } from "./components/Header";
import { IncidentDrawer } from "./components/IncidentDrawer";
import { IncidentList } from "./components/IncidentList";
import { SkeletonList } from "./components/SkeletonList";
import { SummaryBar } from "./components/SummaryBar";
import { useAnalyst } from "./hooks/useAnalyst";
import { useDebounced } from "./hooks/useDebounced";
import { useIncidents, useSummary } from "./hooks/useIncidents";
import { useTheme } from "./hooks/useTheme";

export default function App() {
  const { theme, toggle } = useTheme();
  const [analyst, setAnalyst] = useAnalyst();
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const q = useDebounced(filters.q, 300);
  const applied = useMemo(() => ({ ...filters, q }), [filters, q]);
  const list = useIncidents(applied);
  const summary = useSummary();

  const canClear =
    filters.q !== "" || filters.severity.length > 0 || filters.category.length > 0 || filters.status.length > 0;
  const clear = () => setFilters(EMPTY_FILTERS);
  const toggleSeverity = (s: Severity) =>
    setFilters((f) => ({
      ...f,
      severity: f.severity.includes(s) ? f.severity.filter((x) => x !== s) : [...f.severity, s],
    }));

  const data = list.data;
  let content;
  if (!data) {
    content = list.isError ? <ErrorState error={list.error} onRetry={() => list.refetch()} /> : <SkeletonList />;
  } else if (data.length === 0) {
    content = <EmptyState filtered={canClear} onClear={clear} />;
  } else {
    content = <IncidentList incidents={data} selectedId={selectedId} onSelect={setSelectedId} />;
  }

  return (
    <div className="app">
      <Header analyst={analyst} onAnalyst={setAnalyst} theme={theme} onToggleTheme={toggle} />
      <SummaryBar summary={summary.data} active={filters.severity} onToggle={toggleSeverity} />
      <FilterBar filters={filters} onChange={setFilters} onClear={clear} canClear={canClear} />

      {list.isError && data && (
        <div className="alert" role="alert">
          <span>Sem conexão com o servidor. Mostrando os últimos dados recebidos.</span>
          <button className="btn" onClick={() => list.refetch()}>Tentar de novo</button>
        </div>
      )}

      <main aria-busy={list.isFetching}>{content}</main>

      {selectedId !== null && (
        <IncidentDrawer key={selectedId} id={selectedId} analyst={analyst} onClose={() => setSelectedId(null)} />
      )}
    </div>
  );
}