import type { Category, Severity, Status } from "../api/types";

export const SEV_ICON: Record<Severity, string> = { Alta: "▲", Média: "◆", Baixa: "●" };

export const CAT_ICON: Record<Category, string> = {
  "Acidente com Veículo": "🚗",
  "Acidente com Vítimas": "🚑",
  "Condição Climática Atípica na Pista": "🌧️",
  "Problema Mecânico": "🔧",
  "Bloqueio de Pista": "🚧",
};

export function timeAgo(iso: string): string {
  const min = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  return h < 24 ? `${h} h ${min % 60} min` : `${Math.floor(h / 24)} d`;
}

export function actionLabel(from: Status, to: Status): string {
  if (to === "Em Investigação") return from === "Inconclusivo" ? "Retomar investigação" : "Assumir";
  if (to === "Aberto") return "Devolver à fila";
  if (to === "Fechado") return "Fechar";
  return "Marcar inconclusivo";
}