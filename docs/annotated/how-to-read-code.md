# How to read code

This page is for someone who has never programmed. It explains the small set of ideas you need to follow the annotated files in this folder. Each idea has a tiny Python example (the mechanism is written in Python) and a JavaScript example (the web page is written in JavaScript). The examples here are made up for teaching; the real code is in the annotated files.

You do not need to memorise anything. Read the idea, look at the two examples, and come back when a later file uses it.

## A file

A file is a named container of text on the computer. Code is just text, saved in a file, that a program can read and run. The end of the name tells you the language: `.py` is Python, `.js` is JavaScript, `.html` is the page structure, `.css` is the page look.

In this project, `mechanism/solver.py` is one file. It holds the code that works out a position.

## A comment

A comment is a note for humans. The computer skips it. In Python a comment starts with `#`. In JavaScript it starts with `//`.

```text
# Python: this line is a note, nothing happens
x = 5
```

```text
// JavaScript: this line is a note, nothing happens
let x = 5;
```

Without comments the code still works. They only help the reader.

## A variable

A variable is a name stuck on a value, like a label on a jar. You can use the name later instead of repeating the value.

```text
speed = 300000
print(speed)
```

```text
let speed = 300000;
console.log(speed);
```

Both examples store the number 300000 under the name `speed`, then show it. In JavaScript, `let` means "make a new name" and `const` means "make a new name that will not change". The `;` ends a statement.

## A function

A function is a named recipe. You give it inputs, it follows its steps, and it hands back a result. You write the recipe once and can use it many times.

```text
def double(n):
    return n * 2

print(double(4))
```

```text
function double(n) {
  return n * 2;
}

console.log(double(4));
```

`def` (Python) or `function` (JavaScript) says "here comes a recipe". `n` is the input. The indented part (Python) or the part between `{` and `}` (JavaScript) is the steps. `double(4)` runs the recipe with 4 and gives back 8.

## A return value

A return value is the answer a function hands back. The word `return` ends the function and gives the answer to whoever called it.

```text
def add(a, b):
    return a + b

total = add(2, 3)
```

```text
function add(a, b) {
  return a + b;
}

const total = add(2, 3);
```

After this, `total` holds 5. If a function has no `return`, it gives back nothing useful (`None` in Python, `undefined` in JavaScript).

## A list (Python) or array (JavaScript)

A list is an ordered row of values. Counting starts at 0, not 1, so the first item is number 0.

```text
sats = ["A", "B", "C"]
print(sats[0])
print(len(sats))
```

```text
const sats = ["A", "B", "C"];
console.log(sats[0]);
console.log(sats.length);
```

Both show `A` (item 0) and then 3 (how many items there are). Python calls this a list, JavaScript calls it an array. Square brackets `[ ]` make one.

## A dict (Python) or object (JavaScript)

A dict is a set of labelled values, like a form with fields. You look a value up by its label (called a key) instead of by its position.

```text
sat = {"name": "G01", "height_km": 20200}
print(sat["name"])
```

```text
const sat = { name: "G01", heightKm: 20200 };
console.log(sat.name);
```

Both show `G01`. Curly braces `{ }` make one. Python calls it a dict, JavaScript calls it an object. Lists and dicts can sit inside each other, for example a list of satellites where each satellite is a dict.

## An if

An `if` makes a choice. The steps under it run only when the condition is true. `else` says what to do otherwise.

```text
if height > 0:
    print("above ground")
else:
    print("underground")
```

```text
if (height > 0) {
  console.log("above ground");
} else {
  console.log("underground");
}
```

`>` means "greater than", `==` means "equal to" (two equals signs, because one `=` already means "store a value"). In Python the indentation shows what belongs to the `if`. In JavaScript the braces do.

## A loop

A loop repeats steps. The most common loop walks through a list, one item at a time.

```text
for s in ["A", "B", "C"]:
    print(s)
```

```text
for (const s of ["A", "B", "C"]) {
  console.log(s);
}
```

Both show `A`, then `B`, then `C`. Each time round, `s` is the next item. Without a loop you would have to write the same steps three times.

## An import

An import borrows code from another file or from a ready-made toolbox, so you do not rewrite it.

```text
import math
print(math.sqrt(9))
```

```text
import { sqrt } from "./maths.js";
console.log(sqrt(9));
```

The first borrows Python's built-in `math` toolbox and uses its square root, giving 3. The second borrows a function called `sqrt` from a file next to it (`./maths.js`). Imports at the top of a file tell you which other files it depends on.

## async and await

Some jobs take time: loading a file, waiting for the network. `async` marks a function that may need to wait. `await` means "pause here until this finishes, then carry on". While it waits, the page stays usable.

```text
async def load():
    data = await fetch_data()
    return data
```

```text
async function load() {
  const data = await fetchData();
  return data;
}
```

Without `await`, the next line would run before the data had arrived, and `data` would not be ready yet.

## An event listener

An event is something that happens on the page: a click, a key press, a slider moving. An event listener is a rule that says "when this happens, run this function".

```text
# Python has no page, so this is JavaScript only
```

```text
button.addEventListener("click", function () {
  console.log("clicked");
});
```

The button is told to watch for clicks. Each time someone clicks, the function runs. The page waits quietly until then. `() => { ... }` is a shorter way to write the same kind of function.

## An HTML tag

HTML describes what is on the page. A tag is a label in angle brackets that says what a piece of the page is. Most tags come as an opening tag and a closing tag with content between them.

```text
<h1>Where am I?</h1>
<button id="go">Start</button>
```

`<h1>` is a big heading. `<button>` is a button. `id="go"` gives that button a name so the JavaScript can find it. The closing tag has a `/`: `</h1>`.

## A CSS rule

CSS describes how things look. A rule picks some part of the page (the selector) and lists the looks to give it.

```text
button {
  color: white;
  background: navy;
}
```

This says: every `button` gets white text on a navy background. A `.name` selector picks everything labelled `class="name"`, and a `#name` selector picks the one thing with `id="name"`.

## How to read the annotated files

Every file in this folder explains one source file and has the same shape:

1. **Title and Source line.** The title names the file. The `Source:` line says which real file is explained.
2. **What this file is for.** Two to four sentences on its job.
3. **Which files it talks to.** What it uses, and who uses it.
4. **In three lines.** The whole file in three short points. If you only read one part, read this.
5. **The code, line by line.** The real code, from the first line to the last, a few lines at a time. Under each piece you get what it does, why it is there, and what would break without it. Maths lines also get the idea behind them and a worked example with real numbers.

Blank lines are skipped. Every other line of the source is quoted exactly, and a test (`tests/test_annotations.py`) checks that nothing was left out and nothing was invented.

## The annotated files

Mechanism (Python):

- [`__init__.py`](mechanism/__init__.py.md)
- [`constants.py`](mechanism/constants.py.md)
- [`coords.py`](mechanism/coords.py.md)
- [`geometry.py`](mechanism/geometry.py.md)
- [`mapview.py`](mechanism/mapview.py.md)
- [`relativity.py`](mechanism/relativity.py.md)
- [`scenario.py`](mechanism/scenario.py.md)
- [`signal.py`](mechanism/signal.py.md)
- [`solver.py`](mechanism/solver.py.md)

Page (HTML, JavaScript, CSS), coming:

- `index.html` (coming)
- `web/bridge.js` (coming)
- `web/config.js` (coming)
- `web/first-screen.js` (coming)
- `web/say.js` (coming)
- `web/startup.js` (coming)
- `web/step-geometry.js` (coming)
- `web/step-relativity.js` (coming)
- `web/step-signal.js` (coming)
- `web/theme.js` (coming)
- `web/theme.css` (coming)
