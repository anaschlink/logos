export const SEVERITIES = ["Alta", "Média", "Baixa"] as const;
export const CATEGORIES = [
  "Acidente com Veículo",
  "Acidente com Vítimas",
  "Condição Climática Atípica na Pista",
  "Problema Mecânico",
  "Bloqueio de Pista",
] as const;
export const STATUSES = ["Aberto", "Em Investigação", "Inconclusivo", "Fechado"] as const;
export const ANALYSTS = ["Ana Silva", "Carlos Souza", "Mariana Costa", "Pedro Oliveira"] as const;

export type Severity = (typeof SEVERITIES)[number];
export type Category = (typeof CATEGORIES)[number];
export type Status = (typeof STATUSES)[number];
export type Analyst = (typeof ANALYSTS)[number];

export interface Incident {
  id: number;
  category: Category;
  severity: Severity;
  status: Status;
  title: string;
  description: string;
  location: string;
  vehicle_id: string;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
  version: number;
  allowed_transitions: Status[];
}

export interface Summary {
  total: number;
  by_severity: Record<Severity, number>;
}

export interface Filters {
  severity: Severity[];
  category: Category[];
  status: Status[];
  q: string;
}

export const EMPTY_FILTERS: Filters = { severity: [], category: [], status: [], q: "" };

export type IncidentChanges = Partial<
  Pick<Incident, "category" | "severity" | "title" | "description" | "location" | "vehicle_id" | "status">
>;