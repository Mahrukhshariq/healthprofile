export type Result<T> =
  | { ok: true; status: number; data: T }
  | { ok: false; status: number; error: string };

function getCookie(name: string): string {
  const match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
  return match ? decodeURIComponent(match[1]) : "";
}

function send(path: string, method: string, body?: unknown) {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (method !== "GET") {
    // Django CSRF: echo the csrftoken cookie in a header (needed for admin writes).
    const token = getCookie("csrftoken");
    if (token) headers["X-CSRFToken"] = token;
  }
  return fetch(`/api${path}`, {
    method,
    headers,
    credentials: "include",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

function messageFrom(data: unknown): string {
  if (data && typeof data === "object") {
    const parts: string[] = [];
    for (const [key, value] of Object.entries(data as Record<string, unknown>)) {
      const text = Array.isArray(value) ? value.join(" ") : String(value);
      parts.push(key === "detail" ? text : `${key}: ${text}`);
    }
    if (parts.length) return parts.join(" | ");
  }
  return "Something went wrong.";
}

/**
 * refreshOn401: for user (JWT) calls. If the 15-minute access token expired,
 * try POST /auth/refresh once, then retry the original request.
 */
export async function request<T>(
  path: string,
  method = "GET",
  body?: unknown,
  refreshOn401 = false,
): Promise<Result<T>> {
  let res = await send(path, method, body);
  if (res.status === 401 && refreshOn401) {
    const refreshed = await send("/auth/refresh", "POST");
    if (refreshed.ok) res = await send(path, method, body);
  }
  let data: unknown = null;
  try {
    data = await res.json();
  } catch {
    /* response had no JSON body */
  }
  if (!res.ok) return { ok: false, status: res.status, error: messageFrom(data) };
  return { ok: true, status: res.status, data: data as T };
}