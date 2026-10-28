import { initAuth } from "./auth.js";
import { initBoards, loadBoards } from "./boards.js";
import { initTasks } from "./tasks.js";

initTasks();
initBoards();
initAuth();

document.addEventListener("auth:login", () => {
  loadBoards();
});

document.addEventListener("auth:logout", () => {
  // Очищаем состояние задач при выходе.
  document.dispatchEvent(new Event("board:change"));
});