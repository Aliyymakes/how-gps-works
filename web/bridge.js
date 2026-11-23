// Bridge between the page (JavaScript) and the Python mechanism (Pyodide).
// loadMechanism(onStatus) loads everything; callPython("module.function", [args]) calls it.
// Contract: docs/interface.md ("The page side").

// Pinned Pyodide version (ships Python 3.14.2).
const PYODIDE_BASE = 'https://cdn.jsdelivr.net/pyodide/v314.0.8/full/';

// Files of the `mechanism` package. A missing file is skipped with one console.warn.
const MECHANISM_FILES = [
  '__init__.py', 'constants.py', 'coords.py', 'scenario.py', 'solver.py',
  'mapview.py', 'geometry.py', 'signal.py', 'relativity.py',
];

const MECHANISM_DIR = '/home/pyodide/mechanism';

let pyodide = null;
let loading = null;

export function loadMechanism(onStatus = () => {}) {
  if (!loading) loading = doLoad(onStatus);
  return loading;
}

async function doLoad(onStatus) {
  onStatus('Loading Python (a few seconds the first time)...');
  const { loadPyodide } = await import(PYODIDE_BASE + 'pyodide.mjs');
  pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

  onStatus('Loading numpy...');
  await pyodide.loadPackage('numpy');

  onStatus('Loading the mechanism code...');
  pyodide.FS.mkdirTree(MECHANISM_DIR);
  for (const name of MECHANISM_FILES) {
    const url = new URL('../mechanism/' + name, import.meta.url);
    const response = await fetch(url);
    if (!response.ok) {
      console.warn('bridge: skipping missing mechanism file ' + name);
      continue;
    }
    pyodide.FS.writeFile(MECHANISM_DIR + '/' + name, await response.text());
  }
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
  onStatus('Ready.');
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
