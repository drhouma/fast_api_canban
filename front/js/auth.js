import { api, setToken } from "./api.js";
import { $, showAuthError, getErrorMessage } from "./ui.js";

let userEmail = "";
let isRegisterMode = false;

const authScreen = $("#auth-screen");
const workspace = $("#workspace");
const authForm = $("#auth-form");
const authSubmit = $("#auth-submit");

function setAuthMode(register) {
  isRegisterMode = register;

  $("#login-tab").classList.toggle("active", !register);
  $("#register-tab").classList.toggle("active", register);

  $("#auth-title").textContent = register
    ? "Создай аккаунт"
    : "С возвращением!";

  $("#auth-subtitle").textContent = register
    ? "Зарегистрируйся, чтобы управлять своими проектами."
    : "Войди, чтобы продолжить работу над проектами.";

  authSubmit.textContent = register
    ? "Создать аккаунт"
    : "Войти в аккаунт";

  $("#auth-password").autocomplete = register
    ? "new-password"
    : "current-password";

  showAuthError();
}

async function login(email, password) {
  const body = new URLSearchParams({
    username: email,
    password,
  });

  return api("/auth/login", "POST", {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });
}

async function handleSubmit(event) {
  event.preventDefault();

  const email = $("#auth-email").value.trim();
  const password = $("#auth-password").value;

  showAuthError();
  authSubmit.disabled = true;

  try {
    let data;

    if (isRegisterMode) {
      data = await api("/auth/register", "POST", {
        body: JSON.stringify({ email, password }),
      });

      if (!data?.access_token) {
        data = await login(email, password);
      }
    } else {
      data = await login(email, password);
    }

    if (!data?.access_token) {
      throw new Error("Сервер не вернул access_token.");
    }

    setToken(data.access_token);
    userEmail = email;

    authScreen.hidden = true;
    workspace.hidden = false;

    $("#user-email").textContent = userEmail;
    $("#user-avatar").textContent =
      userEmail.charAt(0).toUpperCase() || "U";

    // app.js подпишется на событие успешной авторизации.
    document.dispatchEvent(new Event("auth:login"));
  } catch (error) {
    showAuthError(
      getErrorMessage(error, "Не удалось выполнить авторизацию")
    );
  } finally {
    authSubmit.disabled = false;
    authSubmit.textContent = isRegisterMode
      ? "Создать аккаунт"
      : "Войти в аккаунт";
  }
}

export function logout() {
  setToken(null);
  userEmail = "";

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

  // При старте показываем форму авторизации.
  logout();
}