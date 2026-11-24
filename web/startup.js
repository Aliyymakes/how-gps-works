// One start-up path for every section: the same progress words, the same failure words
// and one shared "Try again" button. Each section calls whenPythonReady once.
// bridge.js is imported inside attempt(), not at the top: if that file fails to download,
// a top-level import would stop this whole file, and the page would wait forever.
let callPython = null; // set once the bridge has loaded

const FAILURE_WORDS = "Python could not be downloaded, so nothing here can calculate yet. Check your internet connection, then press Try again.";

const sections = []; // one { statusNode, onReady, hasControls, retryButton, done } per section
let state = "loading"; // "loading", "failed" or "ready"
let started = false;
let latestProgress = "";

export function whenPythonReady(statusNode, onReady, { hasControls = true } = {}) {
  const section = { statusNode, onReady, hasControls, retryButton: null, done: false };
  sections.push(section);
  if (!started) {
    started = true;
    attempt();
  } else if (state === "ready") {
    finish(section);
  } else if (state === "failed") {
    showFailure(section);
  } else {
    showProgress(section);
  }
}

function attempt() {
  state = "loading";
  for (const section of sections) removeRetryButton(section);
  loadBridge().then(
    () => {
      state = "ready";
      for (const section of sections) finish(section);
    },
    (error) => {
      console.error(error);
      state = "failed";
      for (const section of sections) showFailure(section);
    },
  );
}

async function loadBridge() {
  const bridge = await import("./bridge.js");
  callPython = bridge.callPython;
  await bridge.loadMechanism(onProgress);
}

function onProgress(text) {
  latestProgress = text;
  if (state !== "loading") return;
  for (const section of sections) showProgress(section);
}

function showProgress(section) {
  const prefix = section.hasControls ? "The controls switch on when this finishes. " : "";
  section.statusNode.textContent = prefix + latestProgress;
}

function finish(section) {
  if (section.done) return;
  section.done = true;
  section.statusNode.textContent = "";
  removeRetryButton(section);
  section.onReady(callPython);
}

function showFailure(section) {
  section.statusNode.textContent = FAILURE_WORDS;
  if (section.retryButton) return;
  const button = document.createElement("button");
  button.className = "btn";
  button.type = "button";
  button.textContent = "Try again";
  button.addEventListener("click", () => attempt()); // restarts the load for every section
  section.statusNode.after(button);
  section.retryButton = button;
}

function removeRetryButton(section) {
  if (!section.retryButton) return;
  section.retryButton.remove();
  section.retryButton = null;
}
