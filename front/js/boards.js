import { api } from "./api.js";
import { $, showError, getErrorMessage } from "./ui.js";

let boards = [];
let currentBoard = null;

export function getCurrentBoard() {
  return currentBoard;
}

export function getBoardName(board) {
  return board.title ?? board.name ?? "Без названия";
}

function renderBoards() {
  const list = $("#boards-list");
  list.replaceChildren();

  if (boards.length === 0) {
    const empty = document.createElement("p");
    empty.className = "sidebar-muted";
    empty.textContent = "Пока нет досок";
    list.append(empty);
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

    button.addEventListener("click", () => {
      selectBoard(item.id);
    });

    list.append(button);
  }
}

function renderEmptyState() {
  currentBoard = null;

  $("#board-content").hidden = true;
  $("#board-empty").hidden = false;
  $("#current-board-name").textContent = "Нет досок";

  renderBoards();

  document.dispatchEvent(new Event("board:change"));
}

export async function selectBoard(boardId) {
  const selected = boards.find(board => board.id === boardId);

  if (!selected) {
    showError("Доска не найдена или недоступна.");
    return;
  }

  currentBoard = selected;

  const name = getBoardName(selected);

  $("#current-board-name").textContent = name;
  $("#board-title").textContent = name;
  $("#board-subtitle").textContent = "Планируй, выполняй, достигай.";

  $("#board-empty").hidden = true;
  $("#board-content").hidden = false;

  showError();
  renderBoards();

  document.dispatchEvent(new Event("board:change"));
}

export async function loadBoards() {
  const list = $("#boards-list");
  list.replaceChildren();

  const loading = document.createElement("p");
  loading.className = "sidebar-muted";
  loading.textContent = "Загрузка досок...";
  list.append(loading);

  try {
    const data = await api("/boards");

    boards = Array.isArray(data) ? data : data.boards;

    if (!Array.isArray(boards)) {
      throw new Error("API должен возвращать список досок.");
    }

    if (currentBoard) {
      currentBoard =
        boards.find(board => board.id === currentBoard.id) ?? null;
    }

    renderBoards();

    if (currentBoard) {
      await selectBoard(currentBoard.id);
    } else if (boards.length > 0) {
      await selectBoard(boards[0].id);
    } else {
      renderEmptyState();
    }
  } catch (error) {
    list.replaceChildren();

    const message = document.createElement("p");
    message.className = "sidebar-muted";
    message.textContent = "Не удалось загрузить доски.";
    list.append(message);

    showError(getErrorMessage(error, "Ошибка загрузки досок"));
  }
}

export async function createBoard() {
  const title = prompt("Название новой доски:");

  if (!title?.trim()) return;

  try {
    showError();

    const result = await api("/boards", "POST", {
      body: JSON.stringify({ title: title.trim() }),
    });

    const created = result.board ?? result;

    if (created.id == null) {
      throw new Error("Сервер не вернул ID созданной доски.");
    }

    await loadBoards();
    await selectBoard(created.id);
  } catch (error) {
    showError(getErrorMessage(error, "Не удалось создать доску"));
  }
}

export function initBoards() {
  $("#create-board").addEventListener("click", createBoard);
  $("#create-first-board").addEventListener("click", createBoard);
}