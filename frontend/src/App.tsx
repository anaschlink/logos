
import { useEffect } from "react";
import { request } from "./api/client";

export default function App() {
  useEffect(() => {
    request("/incidents/summary").then(console.log, console.error);

    request("/incidents/999999").catch((e) => {
      console.log(e.status, e.code);
    });
  }, []);

  return (
    <main style={{ padding: "var(--space-5)" }}>
      <h1 style={{ fontSize: "var(--text-2xl)" }}>Logos</h1>
      <p style={{ color: "var(--text-muted)" }}>Central de incidentes</p>
    </main>
  );
}
