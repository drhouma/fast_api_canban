export const API_URL = "http://localhost:8000";

let token = null;

export function setToken(value) {
  token = value;
}

export function getToken() {
  return token;
}

export async function api(path, method = "GET", options = {}) {
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    method,
    headers,
  });

  if (!response.ok) {
    let message = `Ошибка API: ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || data.message || message;
    } catch {
      // Сервер мог вернуть ответ не в JSON.
    }

    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}