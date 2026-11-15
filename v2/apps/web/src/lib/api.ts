import { getToken } from "./auth";

function authHeaders(): Record<string, string> {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export const apiClient = {
  get: async (path: string) => {
    const res = await fetch(path, { headers: authHeaders() });
    return res;
  },
  post: async (path: string, body: unknown) => {
    const res = await fetch(path, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });
    return res;
  },
  put: async (path: string, body: unknown) => {
    const res = await fetch(path, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });
    return res;
  },
  del: async (path: string) => {
    const res = await fetch(path, {
      method: "DELETE",
      headers: authHeaders(),
    });
    return res;
  },
};
