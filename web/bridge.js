// Bridge between the page (JavaScript) and the Python mechanism (Pyodide).
// loadMechanism(onStatus) loads everything; callPython("module.function", [args]) calls it.
// Contract: docs/interface.md ("The page side").

// Pinned Pyodide version (ships Python 3.14.2). index.html repeats this address in its
// <link rel="modulepreload">: change both together.
const PYODIDE_BASE = 'https://cdn.jsdelivr.net/pyodide/v314.0.8/full/';

// Files of the `mechanism` package. A file that cannot be fetched makes the whole load fail.
const MECHANISM_FILES = [
  '__init__.py', 'constants.py', 'coords.py', 'scenario.py', 'solver.py',
  'mapview.py', 'geometry.py', 'signal.py', 'relativity.py',
];

const MECHANISM_DIR = '/home/pyodide/mechanism';

let pyodide = null;
let loading = null;
const listeners = []; // every status function passed to loadMechanism
let latestText = null; // the most recent progress message

// Every caller gets every progress message, also when another caller started the load.
export function loadMechanism(onStatus = () => {}) {
  if (!listeners.includes(onStatus)) listeners.push(onStatus);
  if (latestText !== null) onStatus(latestText);
  if (!loading) {
    loading = doLoad().catch((error) => {
      loading = null; // a failed load is not remembered: the next call tries again
      throw error;
    });
  }
  return loading;
}

function tell(text) {
  latestText = text;
  for (const listener of listeners) listener(text);
}

async function fetchText(name) {
  let response;
  try {
    response = await fetch(new URL('../mechanism/' + name, import.meta.url));
  } catch {
    response = null;
  }
  if (!response || !response.ok) throw new Error('could not load mechanism/' + name);
  return response.text();
}

async function doLoad() {
  tell('Step 1 of 2: downloading Python and numpy. This is the slow step on a first visit…');
  // Our own files download while Pyodide does; they are written into Python's file system later.
  const sources = Promise.all(MECHANISM_FILES.map(fetchText));
  sources.catch(() => {}); // the failure is reported where the result is awaited below
  const { loadPyodide } = await import(PYODIDE_BASE + 'pyodide.mjs');
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE, packages: ['numpy'] });

  tell('Step 2 of 2: loading our GPS code…');
  const texts = await sources;
  pyodide.FS.mkdirTree(MECHANISM_DIR);
  MECHANISM_FILES.forEach((name, i) => pyodide.FS.writeFile(MECHANISM_DIR + '/' + name, texts[i]));
  // The folder holding the package must be on sys.path.
  pyodide.runPython('import sys\nif "/home/pyodide" not in sys.path: sys.path.insert(0, "/home/pyodide")');

  // Runs in Python: import the module, call the function, return the result as JSON text.
  pyodide.runPython(`
import importlib, json

def _bridge_call(target, args_json):
    module_name, _, function_name = target.partition(".")
    try:
        module = importlib.import_module("mechanism." + module_name)
    except ImportError:
        raise ValueError("unknown module: mechanism." + module_name)
    function = getattr(module, function_name, None)
    if not callable(function):
        raise ValueError("unknown function: mechanism." + target)
    return json.dumps(function(*json.loads(args_json)))
`);
  tell('Ready.');
}

export async function callPython(target, args = []) {
  if (!pyodide) throw new Error('callPython: call loadMechanism() first');
  const bridgeCall = pyodide.globals.get('_bridge_call');
  try {
    return JSON.parse(bridgeCall(target, JSON.stringify(args)));
  } catch (error) {
    // Python exceptions arrive as PythonError; the last line holds the readable part.
    const lines = String(error.message).trim().split('\n');
    throw new Error(lines[lines.length - 1]);
  } finally {
    bridgeCall.destroy();
  }
}

// Debug helper for the test page only: evaluates one Python expression, returns it as a JS value.
export function evalPython(expression) {
  if (!pyodide) throw new Error('evalPython: call loadMechanism() first');
  return JSON.parse(pyodide.runPython('import json\njson.dumps(' + expression + ')'));
}
