// Адрес FastAPI
const API_URL = "http://localhost:8000";

const columns = [
  { status: "planned", title: "В планах" },
  { status: "in_progress", title: "В процессе" },
  { status: "done", title: "Выполнено" },
];

const board = document.querySelector("#board");
const errorBox = document.querySelector("#error");
const form = document.querySelector("#task-form");

let tasks = [];

// Метод запроса передаётся явно
async function api(path, method = "GET", options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    method: method,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(
      `Ошибка API: ${response.status} ${message || response.statusText}`
    );
  }

  if (response.status === 204) return null;

  return response.json();
}

function showError(message = "") {
  errorBox.textContent = message;
  errorBox.hidden = !message;
}

async function loadTasks() {
  try {
    showError();

    const data = await api("/tasks", "GET");

    tasks = Array.isArray(data) ? data : data.tasks;

    if (!Array.isArray(tasks)) {
      throw new Error("API должен возвращать список задач");
    }

    render();
  } catch (error) {
    showError(error.message || "Не удалось загрузить задачи");
  }
}

function render() {
  board.replaceChildren();

  for (const column of columns) {
    const columnTasks = tasks.filter(
      task => task.status === column.status
    );

    const section = document.createElement("section");
    section.className = "column";

    const heading = document.createElement("div");
    heading.className = "column-heading";

    const title = document.createElement("h2");
    title.textContent = column.title;

    const count = document.createElement("span");
    count.className = "count";
    count.textContent = columnTasks.length;

    heading.append(title, count);

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
    board.append(section);
  }
}

function createCard(task) {
  const card = document.createElement("article");
  card.className = "card";

  const top = document.createElement("div");
  top.className = "card-top";

  const title = document.createElement("h3");
  title.textContent = task.name;

  const deleteButton = document.createElement("button");
  deleteButton.className = "delete";
  deleteButton.type = "button";
  deleteButton.textContent = "×";
  deleteButton.title = "Удалить";
  deleteButton.setAttribute("aria-label", `Удалить: ${task.name}`);
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
  select.setAttribute("aria-label", `Статус задачи ${task.name}`);

  for (const option of columns) {
    const element = document.createElement("option");
    element.value = option.status;
    element.textContent = option.title;
    element.selected = task.status === option.status;
    select.append(element);
  }

  select.addEventListener("change", () => {
    changeStatus(task.id, select.value);
  });

  label.append(select);
  card.append(label);

  return card;
}
// Создание задачи
form.addEventListener("submit", async event => {
  event.preventDefault();

  const titleInput = document.querySelector("#title");
  const descriptionInput = document.querySelector("#description");

  const title = titleInput.value.trim();

  if (!title) return;

  try {
    showError();

    await api("/tasks", "POST", {
      body: JSON.stringify({
        name,
        description: descriptionInput.value.trim() || null,
        status: "planned",
      }),
    });

    form.reset();
    await loadTasks();
  } catch (error) {
    showError(error.message || "Не удалось добавить задачу");
  }
});

// Изменение статуса
async function changeStatus(id, status) {
  try {
    showError();

    await api(`/tasks/${encodeURIComponent(id)}`, "PATCH", {
      body: JSON.stringify({ status }),
    });

    await loadTasks();
  } catch (error) {
    showError(error.message || "Не удалось изменить статус");
    await loadTasks();
  }
}

// Удаление задачи
async function deleteTask(id) {
  if (!confirm("Удалить эту задачу?")) return;

  try {
    showError();

    await api(`/tasks/${encodeURIComponent(id)}`, "DELETE");

    tasks = tasks.filter(task => task.id !== id);
    render();
  } catch (error) {
    showError(error.message || "Не удалось удалить задачу");
  }
}

// Обновление списка
document.querySelector("#refresh").addEventListener("click", loadTasks);

// Первичная загрузка
loadTasks();
