import { ANALYSTS, type Analyst } from "../api/types";
import type { Theme } from "../hooks/useTheme";

type Props = { analyst: Analyst; onAnalyst: (a: Analyst) => void; theme: Theme; onToggleTheme: () => void };

export function Header({ analyst, onAnalyst, theme, onToggleTheme }: Props) {
  return (
    <header className="header">
      <h1>Logos <span className="muted">· Central de incidentes</span></h1>
      <div className="controls">
        <label className="muted" htmlFor="analyst">Analista</label>
        <select id="analyst" value={analyst} onChange={(e) => onAnalyst(e.target.value as Analyst)}>
          {ANALYSTS.map((a) => <option key={a}>{a}</option>)}
        </select>
        <button className="btn" onClick={onToggleTheme} aria-label="Alternar tema claro/escuro">
          {theme === "dark" ? "☀ Claro" : "☾ Escuro"}
        </button>
      </div>
    </header>
  );
}