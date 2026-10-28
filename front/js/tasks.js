import { api } from "./api.js";
import { $, showError, getErrorMessage } from "./ui.js";
import { getCurrentBoard } from "./boards.js";

const columns = [
  { status: "planned", title: "В планах" },
  { status: "in_progress", title: "В процессе" },
  { status: "done", title: "Выполнено" },
];

let tasks = [];
let loading = false;
let requestVersion = 0;

function renderTasks() {
  const board = $("#board");
  board.replaceChildren();

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
    board.append(section);
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

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "delete";
  remove.textContent = "×";
  remove.title = "Удалить";
  remove.setAttribute("aria-label", `Удалить: ${title.textContent}`);

  remove.addEventListener("click", () => deleteTask(task.id));

  top.append(title, remove);
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

  for (const column of columns) {
    const option = document.createElement("option");
    option.value = column.status;
    option.textContent = column.title;
    option.selected = task.status === column.status;
    select.append(option);
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

export async function loadTasks() {
  const board = getCurrentBoard();

  if (!board || loading) return;

  const boardId = board.id;
  const version = ++requestVersion;

  loading = true;
  $("#refresh").disabled = true;

  try {
    showError();

    const data = await api(
      `/boards/${encodeURIComponent(boardId)}/tasks`
    );

    if (
      version !== requestVersion ||
      getCurrentBoard()?.id !== boardId
    ) {
      return;
    }

    tasks = Array.isArray(data) ? data : data.tasks;

    if (!Array.isArray(tasks)) {
      throw new Error("API должен возвращать список задач.");
    }

    renderTasks();
  } catch (error) {
    if (version === requestVersion) {
      showError(getErrorMessage(error, "Не удалось загрузить задачи"));
    }
  } finally {
    if (version === requestVersion) {
      loading = false;
      $("#refresh").disabled = false;
    }
  }
}

async function createTask(event) {
  event.preventDefault();

  const board = getCurrentBoard();

  if (!board) {
    showError("Сначала выбери доску.");
    return;
  }

  const boardId = board.id;
  const title = $("#title").value.trim();
  const description = $("#description").value.trim();
  const button = $("#add-task");

  if (!title) return;

  button.disabled = true;

  try {
    showError();

    await api(
      `/boards/${encodeURIComponent(boardId)}/tasks`,
      "POST",
      {
        body: JSON.stringify({
          name: title,
          description: description || null,
          status: "planned",
        }),
      }
    );

    $("#task-form").reset();

    if (getCurrentBoard()?.id === boardId) {
      await loadTasks();
    }
  } catch (error) {
    showError(getErrorMessage(error, "Не удалось создать задачу"));
  } finally {
    button.disabled = false;
  }
}

async function changeStatus(id, status) {
  const boardId = getCurrentBoard()?.id;
  const task = tasks.find(item => item.id === id);

  if (!task) return;

  const previousStatus = task.status;
  task.status = status;
  renderTasks();

  try {
    showError();

    await api(`/tasks/${encodeURIComponent(id)}`, "PUT", {
      body: JSON.stringify({ new_status: status }),
    });
  } catch (error) {
    if (getCurrentBoard()?.id === boardId) {
      task.status = previousStatus;
      renderTasks();
      showError(getErrorMessage(error, "Не удалось изменить статус"));
    }
  }
}

async function deleteTask(id) {
  if (!confirm("Удалить эту задачу?")) return;

  const boardId = getCurrentBoard()?.id;

  try {
    showError();

    await api(`/tasks/${encodeURIComponent(id)}`, "DELETE");

    if (getCurrentBoard()?.id !== boardId) return;

    tasks = tasks.filter(task => task.id !== id);
    renderTasks();
  } catch (error) {
    showError(getErrorMessage(error, "Не удалось удалить задачу"));
  }
}

export function initTasks() {
  $("#task-form").addEventListener("submit", createTask);

  $("#refresh").addEventListener("click", async () => {
    const { loadBoards } = await import("./boards.js");
    await loadBoards();
  });

  document.addEventListener("board:change", () => {
    tasks = [];
    requestVersion++;
    loading = false;
    renderTasks();

    if (getCurrentBoard()) {
      loadTasks();
    }
  });
}