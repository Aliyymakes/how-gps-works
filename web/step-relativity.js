// Rung 4: relativity (design.md 2a, 2b). It draws a small table; every number comes from Python
// (relativity.drift_over_time). The only arithmetic here is scaling a bar to its largest value.
import * as config from "./config.js";
import { whenPythonReady } from "./startup.js";

// Layout for this section only. Colours, fonts and radii come from theme.css.
const STYLE = `
.rel { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-4); }
.rel-stack { grid-template-columns: minmax(0, 1fr); }
.rel-note { font-size: var(--text-sm); color: var(--text-muted); min-height: 1.5em; }
.rel-card { padding: var(--s-4); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--s-3); }
.rel-table { width: 100%; border-collapse: collapse; }
.rel-table th { text-align: left; font: 500 var(--text-xs) var(--font-mono); color: var(--text-muted); padding: var(--s-2) var(--s-2) var(--s-2) 0; }
.rel-table td { padding: var(--s-2) var(--s-2) var(--s-2) 0; border-top: 1px solid var(--line); vertical-align: middle; }
.rel-table .num { overflow-wrap: anywhere; }
.rel-bar { height: 8px; background: var(--surface-2); border-radius: var(--r-pill); overflow: hidden; margin-top: var(--s-1); min-width: 0; }
.rel-bar > span { display: block; height: 100%; background: var(--text-muted); transform-origin: left center; }
@media (max-width: 359px) { .rel-card { padding: var(--s-3); } .rel-table th, .rel-table td { padding-right: var(--s-1); overflow-wrap: anywhere; } .rel-table .badge { padding: 2px var(--s-2); } }
`;

const nf = new Intl.NumberFormat("en", { maximumFractionDigits: 1 });
const LEVEL_WORDS = { ok: "Good fix", warn: "Fix is off", bad: "Fix is far off" };

function errorLevel(errorM) {
  if (errorM < config.errorLimits.ok_m) return "ok";
  if (errorM < config.errorLimits.warn_m) return "warn";
  return "bad";
}

// Draft sentences: every visible sentence below is for Icarus to approve.
const PAGE = `
<div class="rel">
  <header class="rel-stack" style="display: grid; gap: var(--s-2)">
    <h2 id="rel-title">Do the satellites' own clocks matter?</h2>
    <p class="muted">Over time, a satellite clock drifts a little from true time. Here every satellite drifts by the same amount.</p>
    <p class="rel-note" data-id="status" role="status" aria-live="polite">Loading the maths…</p>
  </header>
  <section class="card rel-card" aria-labelledby="rel-title">
    <table class="rel-table">
      <caption class="label" style="text-align: left; padding-bottom: var(--s-2)">Drift over time</caption>
      <thead><tr><th scope="col">Hours</th><th scope="col">Each distance gains</th><th scope="col">Position off by (clock solved)</th></tr></thead>
      <tbody data-id="rows"></tbody>
    </table>
    <p class="rel-note" data-id="msg" role="status" aria-live="polite"></p>
  </section>
  <p>The drift is the same for every satellite, so it looks just like the phone's own clock error, and solving for the clock absorbs it. The position stays put.</p>
</div>`;

export function mountRelativityStep(container) {
  if (!document.getElementById("rel-style")) {
    const style = document.createElement("style");
    style.id = "rel-style";
    style.textContent = STYLE;
    document.head.append(style);
  }
  container.insertAdjacentHTML("beforeend", PAGE);
  const root = container.lastElementChild;
  const $ = (id) => root.querySelector(`[data-id="${id}"]`);
  const el = { status: $("status"), rows: $("rows"), msg: $("msg") };
  whenPythonReady(el.status, start, { hasControls: false });

  async function start(callPython) {
    try {
      const { lat_deg, lon_deg } = config.receiver;
      const receiver = await callPython("coords.latlon_to_xyz", [lat_deg, lon_deg]);
      if (receiver.error) throw new Error(receiver.error);
      const satellites = [];
      for (const sat of config.satellites) {
        const point = await callPython("coords.satellite_from_sky", [lat_deg, lon_deg, sat.azimuth_deg, sat.elevation_deg]);
        if (point.error) throw new Error(point.error);
        satellites.push({ id: sat.id, ...point });
      }
      const result = await callPython("relativity.drift_over_time",
        [receiver, satellites, config.relativityPhoneClockErrorS, config.relativityHours]);
      el.status.textContent = "";
      if (result.error) { el.msg.textContent = result.error; return; } // Python's own plain sentence
      showRows(result);
    } catch (error) {
      console.error(error);
      el.status.textContent = "";
      el.msg.textContent = "Something went wrong in the calculation, so the table is empty.";
    }
  }

  function showRows(rows) {
    const biggest = Math.max(...rows.map((row) => row.range_added_m), 1e-9); // bar scale only
    el.rows.replaceChildren();
    for (const row of rows) {
      const level = errorLevel(row.error_clock_solved_m);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="num" data-cell="hours"></td>
        <td><span class="num" data-cell="range"></span><div class="rel-bar" aria-hidden="true"><span data-cell="bar"></span></div></td>
        <td><span class="num" data-cell="error"></span> <span class="badge is-${level}" data-cell="badge"></span></td>`;
      const cell = (name) => tr.querySelector(`[data-cell="${name}"]`);
      cell("hours").textContent = `${nf.format(row.hours)} h`;
      cell("range").textContent = `${nf.format(row.range_added_m)} m`;
      cell("bar").style.transform = `scaleX(${row.range_added_m / biggest})`;
      cell("error").textContent = `${nf.format(row.error_clock_solved_m)} m`;
      cell("badge").textContent = LEVEL_WORDS[level];
      el.rows.append(tr);
    }
  }
}
