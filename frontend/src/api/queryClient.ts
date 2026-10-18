import { QueryClient } from "@tanstack/react-query";
import { isRetryable } from "./client";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failures, err) => isRetryable(err) && failures < 3,
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 8000),
      staleTime: 5_000,
    },
    mutations: { retry: 0 }, // PATCH nunca é repetido sozinho
  },
});