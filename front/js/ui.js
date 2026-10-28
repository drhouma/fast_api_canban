export const $ = selector => document.querySelector(selector);

export function showError(message = "") {
  const box = $("#error");
  if (!box) return;

  box.textContent = message;
  box.hidden = !message;
}

export function showAuthError(message = "") {
  const box = $("#auth-error");
  if (!box) return;

  box.textContent = message;
  box.hidden = !message;
}

export function getErrorMessage(error, fallback) {
  return error instanceof Error ? error.message : fallback;
}