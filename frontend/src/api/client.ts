const BASE = "/api";

export type FieldError = { field: string; message: string };

export class ApiError extends Error {
  status: number;
  code: string;
  details?: FieldError[];
  current?: unknown;
  retryAfter?: number;

  constructor(init: {
    status: number;
    code: string;
    message: string;
    details?: FieldError[];
    current?: unknown;
    retryAfter?: number;
  }) {
    super(init.message);
    this.name = "ApiError";
    this.status = init.status;
    this.code = init.code;
    this.details = init.details;
    this.current = init.current;
    this.retryAfter = init.retryAfter;
  }
}

/** Falhas temporárias: sem resposta do servidor, ou gateway/serviço indisponível. */
export function isRetryable(err: unknown): boolean {
  return (
    err instanceof ApiError &&
    (err.status === 0 || [502, 503, 504].includes(err.status))
  );
}

type Params = Record<string, string | string[] | undefined>;

export function buildQuery(params: Params): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === "") continue;
    for (const v of Array.isArray(value) ? value : [value]) qs.append(key, v);
  }
  const s = qs.toString();
  return s ? `?${s}` : "";
}

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  analyst?: string;
  signal?: AbortSignal;
};

export async function request<T>(
  path: string,
  { method = "GET", body, analyst, signal }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (analyst) headers["X-Analyst"] = analyst;

  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ApiError({
      status: 0,
      code: "network_error",
      message: "Sem conexão com o servidor.",
    });
  }

  if (res.status === 204) return undefined as T;

  let payload: any = null;
  try {
    payload = await res.json();
  } catch {
    // corpo vazio ou não-JSON (ex.: HTML de um 502 do Render no cold start)
  }

  if (!res.ok) {
    const err = payload?.error;
    throw new ApiError({
      status: res.status,
      code: err?.code ?? "unexpected_response",
      message: err?.message ?? `Erro inesperado (HTTP ${res.status}).`,
      details: err?.details,
      current: err?.current,
      retryAfter: Number(res.headers.get("Retry-After")) || undefined,
    });
  }

  return payload as T;
}