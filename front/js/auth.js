import { api, setToken } from "./api.js";
import { $, showAuthError, getErrorMessage } from "./ui.js";

let isRegisterMode = false;

const authScreen = $("#auth-screen");
const workspace = $("#workspace");
const authForm = $("#auth-form");
const authSubmit = $("#auth-submit");
const usernameField = $("#username-field");
const usernameInput = $("#auth-username");

function setAuthMode(register) {
  isRegisterMode = register;

  $("#login-tab").classList.toggle("active", !register);
  $("#register-tab").classList.toggle("active", register);
  $("#auth-title").textContent = register ? "Создай аккаунт" : "С возвращением!";
  $("#auth-subtitle").textContent = register
    ? "Зарегистрируйся, чтобы управлять своими досками."
    : "Войди, чтобы продолжить работу.";
  authSubmit.textContent = register ? "Создать аккаунт" : "Войти в аккаунт";

  usernameField.hidden = !register;
  usernameInput.required = register;
  $("#auth-password").autocomplete = register ? "new-password" : "current-password";
  showAuthError();
}

async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  return api("/auth/login", "POST", {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

async function showWorkspace(user) {
  authScreen.hidden = true;
  workspace.hidden = false;

  const email = user.email || "";
  const displayName = user.username || email || "Пользователь";
  $("#user-email").textContent = displayName;
  $("#user-avatar").textContent = displayName.charAt(0).toUpperCase() || "U";

  document.dispatchEvent(new Event("auth:login"));
}

async function handleSubmit(event) {
  event.preventDefault();

  const email = $("#auth-email").value.trim();
  const password = $("#auth-password").value;
  const username = usernameInput.value.trim();

  showAuthError();
  authSubmit.disabled = true;

  try {
    let data;

    if (isRegisterMode) {
      await api("/auth/register", "POST", {
        body: JSON.stringify({ username, email, password }),
      });
      data = await login(email, password);
    } else {
      data = await login(email, password);
    }

    if (!data?.access_token) throw new Error("Сервер не вернул access_token.");

    setToken(data.access_token);
    const user = await api("/auth/me");
    await showWorkspace(user);
  } catch (error) {
    showAuthError(getErrorMessage(error, "Не удалось выполнить авторизацию"));
  } finally {
    authSubmit.disabled = false;
    authSubmit.textContent = isRegisterMode ? "Создать аккаунт" : "Войти в аккаунт";
  }
}

export function logout() {
  setToken(null);
  authScreen.hidden = false;
  workspace.hidden = true;
  authForm.reset();
  setAuthMode(false);
  document.dispatchEvent(new Event("auth:logout"));
}

export function initAuth() {
  $("#login-tab").addEventListener("click", () => setAuthMode(false));
  $("#register-tab").addEventListener("click", () => setAuthMode(true));
  authForm.addEventListener("submit", handleSubmit);
  $("#logout").addEventListener("click", logout);
  logout();
}
