// Put words in a message line and flash it briefly, so pressing something always gives a visible answer,
// even when the words are the same as before.
export function say(node, text) {
  node.textContent = text;
  if (text && node.animate) node.animate([{ opacity: 0.3 }, { opacity: 1 }], { duration: 160, easing: "ease" });
}
