// Small sketches drawn with SVG. Each function returns a string of SVG markup; the page puts it in place.
// No numbers are drawn here: these are sketches, and the real numbers always come from the Python mechanism.
// Styles (.figure, .dim, .fig-pulse) live in index.html's style block.

const WORDS = "Sketch: a signal travels from a satellite to a phone. Travel time times the speed of light is one distance, and one distance is one line on the map.";

// A satellite: a small box with two wings. (x, y) is the centre of the box.
function satellite(x, y) {
  return `<rect x="${x - 4}" y="${y - 4}" width="8" height="8"/>`
    + `<rect x="${x - 13}" y="${y - 2}" width="7" height="4"/><rect x="${x + 6}" y="${y - 2}" width="7" height="4"/>`;
}

// A phone: a tall rounded rectangle. (x, y) is its top left corner.
function phone(x, y) {
  return `<rect x="${x}" y="${y}" width="14" height="24" rx="3"/><line x1="${x + 5}" y1="${y + 19}" x2="${x + 9}" y2="${y + 19}"/>`;
}

// A dashed line from one x to another with one short pulse that travels along it.
function signalLine(x1, x2, y) {
  const travel = x2 - x1;
  return `<line class="dim" x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke-dasharray="4 4"/>`
    + `<circle class="fig-pulse" cx="${x1}" cy="${y}" r="3" style="--travel: ${travel}px"/>`;
}

// A small arrow, then a short straight line: one distance is one line on the map.
function arrowAndLine(arrowX, lineX1, lineX2, y) {
  return `<path d="M${arrowX} ${y}h12m-4 -4l4 4l-4 4"/><line x1="${lineX1}" y1="${y}" x2="${lineX2}" y2="${y}"/>`;
}

function text(x, y, words) {
  return `<text x="${x}" y="${y}">${words}</text>`;
}

// The strip above the first map. Two sizes: a narrow one for phones (64 px tall) and a wide one (96 px tall).
// The page shows one of them and hides the other (index.html).
export function firstScreenFigure() {
  const narrow = `<svg class="figure figure-narrow" viewBox="0 0 358 64" preserveAspectRatio="xMinYMid meet" role="img" aria-label="${WORDS}">`
    + satellite(14, 18) + signalLine(34, 138, 18) + phone(144, 6)
    + text(0, 46, "travel time × speed of light") + text(0, 60, "= distance")
    + arrowAndLine(176, 198, 354, 18)
    + text(198, 46, "one distance =") + text(198, 60, "one line on the map")
    + `</svg>`;
  const wide = `<svg class="figure figure-wide" viewBox="0 0 640 76" preserveAspectRatio="xMinYMid meet" role="img" aria-label="${WORDS}">`
    + satellite(20, 28) + signalLine(46, 290, 28) + phone(296, 16)
    + text(0, 66, "travel time × speed of light = distance")
    + arrowAndLine(350, 380, 630, 28)
    + text(380, 66, "one distance = one line on the map")
    + `</svg>`;
  return narrow + wide;
}
