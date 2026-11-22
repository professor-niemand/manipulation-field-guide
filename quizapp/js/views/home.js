/**
 * views/home.js: the first screen (SITE COPY, fixed to one library).
 *
 * Shows the Manipulation techniques library with Study and History, plus Back up and
 * Restore for the quiz history. There is no import and no delete: this copy only
 * uses the guide's own library. Opens: "setup", "history". Registered as "home".
 */
import { h, mount, toast, download, plural } from "../ui.js";
import { icon } from "../icons.js";
import { go, register } from "../router.js";
import * as db from "../db.js";
import { syncLibrary } from "../library.js";

const STORAGE_TEXT = {
  protected: "Your browser will not clear your quiz history automatically. Back up now and then anyway.",
  unprotected: "Your browser may clear your quiz history if the device runs low on space. Back up if you want to keep it.",
  unknown: "Back up now and then if you want to keep your quiz history.",
};

function actionRow(iconName, title, hint, onclick) {
  return h("button", { type: "button", class: "action", onclick },
    h("span", { class: "action-icon" }, icon(iconName)),
    h("span", { class: "action-text" }, h("strong", {}, title), h("span", { class: "hint" }, hint)));
}

async function home() {
  const lib = await syncLibrary();
  const [sessions, storage] = await Promise.all([db.allSessions(), db.storageStatus()]);
  const mine = lib ? sessions.filter((s) => s.libraryId === lib.id).sort((a, b) => b.date - a.date) : [];

  const restoreInput = h("input", { type: "file", accept: ".json", hidden: true, onchange: async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    try { await db.importAll(await f.text()); toast("Backup restored"); home(); } catch (err) { toast(err.message); }
  } });

  const card = lib
    ? h("div", { class: "lib" },
        h("div", { class: "lib-head" },
          h("strong", { class: "lib-name" }, lib.name),
          mine.length ? h("span", { class: "pill", title: "Score of your most recent quiz" }, `Last quiz ${mine[0].percent}%`) : null),
        h("p", { class: "muted" }, `${plural(lib.rows.length, "card")}, from the Manipulation Field Guide.`),
        h("div", { class: "lib-actions" },
          h("button", { type: "button", class: "primary", onclick: () => go("setup", lib) }, icon("play", 18), "Start a quiz"),
          h("button", { type: "button", onclick: () => go("history", lib) }, icon("chart", 18), "History")))
    : h("div", { class: "panel" },
        h("h2", {}, "The quiz could not load its questions"),
        h("p", { class: "muted" }, "Open this page once while you are online. After that it works offline."),
        h("button", { type: "button", class: "primary", onclick: () => home() }, "Try again"));

  mount(
    h("h1", {}, "Manipulation techniques quiz"),
    h("p", { class: "lead" }, "Test yourself on the 51 techniques in the guide. Everything stays on this device."),
    card,
    h("section", { "aria-label": "Quiz history" },
      h("div", { class: "actions" },
        actionRow("download", "Back up history", "Save your quiz results to one file.",
          async () => { await download(`manipulation-quiz-backup-${new Date().toISOString().slice(0, 10)}.json`, await db.exportAll(), "application/json"); toast("Backup ready"); }),
        actionRow("restore", "Restore history", "Load a backup file to bring your results back.", () => restoreInput.click())),
      h("div", { class: "status" }, icon("shield", 16), h("p", {}, STORAGE_TEXT[storage]))),
    restoreInput,
    h("p", { class: "footnote muted" }, "Quiz engine: Sheet2Quiz, open source, MIT licence. No accounts, no tracking.")
  );
}

register("home", home);
