const API_URL = "http://localhost:8000";

const columns = [
  { status: "planned", title: "В планах" },
  { status: "in_progress", title: "В процессе" },
  { status: "done", title: "Выполнено" },
];

const $ = selector => document.querySelector(selector);

const authScreen = $("#auth-screen");
const workspace = $("#workspace");
const authForm = $("#auth-form");
const authError = $("#auth-error");
const authTitle = $("#auth-title");
const authSubtitle = $("#auth-subtitle");
const authSubmit = $("#auth-submit");
const loginTab = $("#login-tab");
const registerTab = $("#register-tab");

const boardsList = $("#boards-list");
const currentBoardName = $("#current-board-name");
const boardTitle = $("#board-title");
const boardSubtitle = $("#board-subtitle");
const boardElement = $("#board");
const boardContent = $("#board-content");
const boardEmpty = $("#board-empty");
const errorBox = $("#error");
const taskForm = $("#task-form");

let token = null;
let userEmail = "";
let isRegisterMode = false;
let boards = [];
let currentBoard = null;
let tasks = [];
let loadingTasks = false;

// Все API-запросы проходят через одну функцию.
async function api(path, method = "GET", options = {}) {
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
      // Ответ сервера может быть не в формате JSON.
    }

    if (response.status === 401 && token) {
      logout();
      throw new Error("Сессия завершена. Войди в аккаунт снова.");
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function showError(message = "") {
  errorBox.textContent = message;
  errorBox.hidden = !message;
}

function showAuthError(message = "") {
  authError.textContent = message;
  authError.hidden = !message;
}

function getErrorMessage(error, fallback) {
  return error instanceof Error ? error.message : fallback;
}

// Переключение между формами входа и регистрации.
function setAuthMode(register) {
  isRegisterMode = register;

  loginTab.classList.toggle("active", !register);
  registerTab.classList.toggle("active", register);

  authTitle.textContent = register
    ? "Создай аккаунт"
    : "С возвращением!";

  authSubtitle.textContent = register
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

loginTab.addEventListener("click", () => setAuthMode(false));
registerTab.addEventListener("click", () => setAuthMode(true));

// Авторизация.
// Предполагается OAuth2PasswordRequestForm для /auth/login.
authForm.addEventListener("submit", async event => {
  event.preventDefault();

  const email = $("#auth-email").value.trim();
  const password = $("#auth-password").value;

  showAuthError();
  authSubmit.disabled = true;
  authSubmit.textContent = "Подождите...";

  try {
    let data;

    if (isRegisterMode) {
      data = await api("/auth/register", "POST", {
        body: JSON.stringify({ email, password }),
      });

      // Регистрация может сразу возвращать токен.
      if (data?.access_token) {
        token = data.access_token;
      } else {
        // Если регистрация не авторизует автоматически,
        // выполняем обычный вход.
        token = null;
        data = await login(email, password);
      }
    } else {
      data = await login(email, password);
    }

    if (!data?.access_token) {
      throw new Error("Сервер не вернул access_token.");
    }

    token = data.access_token;
    userEmail = email;

    // Токен пока хранится только в памяти.
    // При обновлении страницы пользователь войдёт заново.
    await enterWorkspace();
  } catch (error) {
    token = null;
    showAuthError(
      getErrorMessage(error, "Не удалось выполнить авторизацию")
    );
  } finally {
    authSubmit.disabled = false;
    authSubmit.textContent = isRegisterMode
      ? "Создать аккаунт"
      : "Войти в аккаунт";
  }
});

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

function logout() {
  token = null;
  userEmail = "";
  boards = [];
  currentBoard = null;
  tasks = [];

  authScreen.hidden = false;
  workspace.hidden = true;

  authForm.reset();
  showAuthError();
  showError();
  setAuthMode(false);
}

$("#logout").addEventListener("click", logout);

// Переход в рабочее пространство.
async function enterWorkspace() {
  authScreen.hidden = true;
  workspace.hidden = false;

  $("#user-email").textContent = userEmail;
  $("#user-avatar").textContent =
    userEmail.charAt(0).toUpperCase() || "U";

  await loadBoards();
}

// Загрузка досок, доступных текущему пользователю.
async function loadBoards() {
  boardsList.replaceChildren();

  const loading = document.createElement("p");
  loading.className = "sidebar-muted";
  loading.textContent = "Загрузка досок...";
  boardsList.append(loading);

  try {
    const data = await api("/boards");

    boards = Array.isArray(data) ? data : data.boards;

    if (!Array.isArray(boards)) {
      throw new Error("API должен возвращать список досок.");
    }

    renderBoards();

    if (currentBoard) {
      const updatedBoard = boards.find(
        board => board.id === currentBoard.id
      );

      if (updatedBoard) {
        currentBoard = updatedBoard;
      } else {
        currentBoard = null;
        tasks = [];
      }
    }

    if (currentBoard) {
      await selectBoard(currentBoard.id);
    } else if (boards.length > 0) {
      await selectBoard(boards[0].id);
    } else {
      showEmptyState();
    }
  } catch (error) {
    boardsList.replaceChildren();

    const message = document.createElement("p");
    message.className = "sidebar-muted";
    message.textContent = "Не удалось загрузить доски.";
    boardsList.append(message);

    showError(getErrorMessage(error, "Ошибка загрузки досок"));
  }
}

function getBoardName(board) {
  return board.title ?? board.name ?? "Без названия";
}

function renderBoards() {
  boardsList.replaceChildren();

  if (boards.length === 0) {
    const empty = document.createElement("p");
    empty.className = "sidebar-muted";
    empty.textContent = "Пока нет досок";
    boardsList.append(empty);
    return;
  }

  for (const item of boards) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "board-link";

    if (currentBoard?.id === item.id) {
      button.classList.add("active");
    }

    const icon = document.createElement("span");
    icon.className = "board-link-icon";
    icon.textContent = "▦";

    const name = document.createElement("span");
    name.className = "board-link-name";
    name.textContent = getBoardName(item);

    button.append(icon, name);
    button.addEventListener("click", () => selectBoard(item.id));

    boardsList.append(button);
  }
}

function showEmptyState() {
  currentBoard = null;
  tasks = [];

  boardContent.hidden = true;
  boardEmpty.hidden = false;

  currentBoardName.textContent = "Нет досок";

  renderBoards();
}

// Выбор доски.
async function selectBoard(boardId) {
  const selected = boards.find(board => board.id === boardId);

  if (!selected) {
    showError("Доска не найдена или недоступна.");
    return;
  }

  currentBoard = selected;
  tasks = [];

  const name = getBoardName(selected);

  currentBoardName.textContent = name;
  boardTitle.textContent = name;
  boardSubtitle.textContent = "Планируй, выполняй, достигай.";

  boardEmpty.hidden = true;
  boardContent.hidden = false;

  showError();
  renderBoards();
  renderTasks();

  await loadTasks();
}

// Загрузка задач только выбранной доски.
async function loadTasks() {
  if (!currentBoard || loadingTasks) return;

  const boardId = currentBoard.id;
  loadingTasks = true;

  $("#refresh").disabled = true;

  try {
    showError();

    const data = await api(
      `/boards/${encodeURIComponent(boardId)}/tasks`
    );

    // Пользователь мог переключить доску во время запроса.
    if (currentBoard?.id !== boardId) return;

    tasks = Array.isArray(data) ? data : data.tasks;

    if (!Array.isArray(tasks)) {
      throw new Error("API должен возвращать список задач.");
    }

    renderTasks();
  } catch (error) {
    if (currentBoard?.id === boardId) {
      showError(getErrorMessage(error, "Не удалось загрузить задачи"));
    }
  } finally {
    loadingTasks = false;
    $("#refresh").disabled = false;
  }
}

// Отрисовка колонок.
function renderTasks() {
  boardElement.replaceChildren();

  for (const column of columns) {
    const columnTasks = tasks.filter(
      task => task.status === column.status
    );

    const section = document.createElement("section");
    section.className = "column";
    section.dataset.status = column.status;

    const heading = document.createElement("div");
    heading.className = "column-heading";

    const indicator = document.createElement("span");
    indicator.className = "column-indicator";

    const title = document.createElement("h2");
    title.textContent = column.title;

    const count = document.createElement("span");
    count.className = "count";
    count.textContent = columnTasks.length;

    heading.append(indicator, title, count);

    const cards = document.createElement("div");
    cards.className = "cards";

    if (columnTasks.length === 0) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "Здесь пока пусто";
      cards.append(empty);
    }

    for (const task of columnTasks) {
      cards.append(createCard(task));
    }

    section.append(heading, cards);
    boardElement.append(section);
  }

  $("#task-total").textContent = tasks.length;
}

function createCard(task) {
  const card = document.createElement("article");
  card.className = "card";

  const top = document.createElement("div");
  top.className = "card-top";

  const title = document.createElement("h3");
  title.textContent = task.name ?? task.title ?? "Без названия";

  const deleteButton = document.createElement("button");
  deleteButton.className = "delete";
  deleteButton.type = "button";
  deleteButton.textContent = "×";
  deleteButton.title = "Удалить";
  deleteButton.setAttribute(
    "aria-label",
    `Удалить: ${title.textContent}`
  );

  deleteButton.addEventListener("click", () => deleteTask(task.id));

  top.append(title, deleteButton);
  card.append(top);

  if (task.description) {
    const description = document.createElement("p");
    description.className = "description";
    description.textContent = task.description;
    card.append(description);
  }

  const label = document.createElement("label");
  label.className = "status-label";
  label.append(document.createTextNode("Статус"));

  const select = document.createElement("select");
  select.setAttribute("aria-label", `Статус: ${title.textContent}`);

  for (const option of columns) {
    const element = document.createElement("option");
    element.value = option.status;
    element.textContent = option.title;
    element.selected = task.status === option.status;
    select.append(element);
  }

  select.addEventListener("change", async () => {
    select.disabled = true;

    try {
      await changeStatus(task.id, select.value);
    } finally {
      select.disabled = false;
    }
  });

  label.append(select);
  card.append(label);

  return card;
}

// Создание доски.
async function createBoard() {
  const title = prompt("Название новой доски:");

  if (!title?.trim()) return;

  try {
    showError();

    const created = await api("/boards", "POST", {
      body: JSON.stringify({
        title: title.trim(),
      }),
    });

    const newBoard = created.board ?? created;

    if (newBoard.id == null) {
      throw new Error("Сервер не вернул ID созданной доски.");
    }

    await loadBoards();
    await selectBoard(newBoard.id);
  } catch (error) {
    showError(getErrorMessage(error, "Не удалось создать доску"));
  }
}

$("#create-board").addEventListener("click", createBoard);
$("#create-first-board").addEventListener("click", createBoard);

// Создание задачи.
taskForm.addEventListener("submit", async event => {
  event.preventDefault();

  if (!currentBoard) {
    showError("Сначала выбери доску.");
    return;
  }

  const boardId = currentBoard.id;
  const titleInput = $("#title");
  const descriptionInput = $("#description");
  const title = titleInput.value.trim();

  if (!title) return;

  const submitButton = $("#add-task");
  submitButton.disabled = true;

  try {
    showError();

    await api(
      `/boards/${encodeURIComponent(boardId)}/tasks`,
      "POST",
      {
        body: JSON.stringify({
          name: title,
          description: descriptionInput.value.trim() || null,
          status: "planned",
        }),
      }
    );

    taskForm.reset();

    if (currentBoard?.id === boardId) {
      await loadTasks();
    }
  } catch (error) {
    showError(getErrorMessage(error, "Не удалось создать задачу"));
  } finally {
    submitButton.disabled = false;
  }
});

// Изменение статуса задачи.
async function changeStatus(id, status) {
  const previousTasks = [...tasks];
  const task = tasks.find(item => item.id === id);

  if (!task) return;

  task.status = status;
  renderTasks();

  try {
    showError();

    await api(`/tasks/${encodeURIComponent(id)}`, "PUT", {
      body: JSON.stringify({
        new_status: status,
      }),
    });
  } catch (error) {
    tasks = previousTasks;
    renderTasks();
    showError(getErrorMessage(error, "Не удалось изменить статус"));
  }
}

// Удаление задачи.
async function deleteTask(id) {
  if (!confirm("Удалить эту задачу?")) return;

  const boardId = currentBoard?.id;

  try {
    showError();

    await api(`/tasks/${encodeURIComponent(id)}`, "DELETE");

    if (currentBoard?.id !== boardId) return;

    tasks = tasks.filter(task => task.id !== id);
    renderTasks();
  } catch (error) {
    showError(getErrorMessage(error, "Не удалось удалить задачу"));
  }
}

// Обновление досок и задач.
$("#refresh").addEventListener("click", loadBoards);

// При старте показываем только экран входа.
// Токен не сохраняем в localStorage.
logout();