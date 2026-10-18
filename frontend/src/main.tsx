import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import "@fontsource-variable/inter";
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/app.css";
import { queryClient } from "./api/queryClient";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
);