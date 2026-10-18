import { useState } from "react";
import { ANALYSTS, type Analyst } from "../api/types";

export function useAnalyst() {
  const [analyst, set] = useState<Analyst>(() => {
    const saved = localStorage.getItem("analyst");
    return (ANALYSTS as readonly string[]).includes(saved ?? "") ? (saved as Analyst) : ANALYSTS[0];
  });
  const setAnalyst = (a: Analyst) => {
    localStorage.setItem("analyst", a);
    set(a);
  };
  return [analyst, setAnalyst] as const;
}