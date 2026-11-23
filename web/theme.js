// Instrument theme helpers: pointer light on cards and a light/dark switch.
// Rules: docs/ui-guide.md section 2.

export function trackPointerLight(root = document) {
  root.addEventListener("pointermove", (event) => {
    const card = event.target.closest?.(".card");
    if (!card) return;
    const box = card.getBoundingClientRect();
    card.style.setProperty("--px", `${event.clientX - box.left}px`);
    card.style.setProperty("--py", `${event.clientY - box.top}px`);
  });
}

export function setTheme(name) {
  document.documentElement.dataset.theme = name;
  try { localStorage.setItem("theme", name); } catch (_) { /* storage can be blocked; the switch still works */ }
}

export function loadSavedTheme() {
  let saved = null;
  try { saved = localStorage.getItem("theme"); } catch (_) { /* ignore */ }
  setTheme(saved === "light" ? "light" : "dark");
}
