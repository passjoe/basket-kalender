const labels = { matched_confident: "✓ Matchad", matched_probable: "✓ Trolig", ambiguous: "? Osäker", unmatched: "✕ Ej hittad" };

function cell(value) { const td = document.createElement("td"); td.textContent = value || "–"; return td; }
function render(data) {
  const events = data.events;
  const matched = events.filter(e => e.sportadmin.status.startsWith("matched")).length;
  const differences = events.filter(e => e.sportadmin.has_differences).length;
  document.querySelector("#updated").textContent = `Senast uppdaterad: ${new Date(data.generated_at).toLocaleString("sv-SE")}`;
  document.querySelector("#stats").textContent = `${events.length} Profixio-matcher · ${matched} matchade · ${differences} med avvikelse · ${events.length - matched} ej matchade/osäkra`;
  const filter = document.querySelector("#series-filter");
  const differencesToggle = document.querySelector("#differences-toggle");
  const table = document.querySelector("#matches-table");
  [...new Set(events.map(event => event.series).filter(Boolean))].sort().forEach(series => {
    const option = document.createElement("option"); option.value = series; option.textContent = series; filter.append(option);
  });
  function showEvents() {
    const body = document.querySelector("#matches"); body.replaceChildren();
    const selected = filter.value;
    let lastDate = null;
    let dateGroupIndex = 0;
    for (const event of events.filter(event => !selected || event.series === selected)) {
      if (event.date !== lastDate) {
        lastDate = event.date;
        dateGroupIndex = 1 - dateGroupIndex; // Toggle between 0 and 1
      }
      const row = document.createElement("tr"); const status = event.sportadmin.status;
      row.className = `${status} date-group-${dateGroupIndex}`; row.append(cell(event.date), cell(event.start_time), cell(event.series), cell(event.location), cell(event.home_team), cell(event.away_team), cell(labels[status]));
      const actual = event.sportadmin.differences.filter(d => d.type === "different" || d.type === "missing");
      const details = actual.map(d => `${d.field}: Profixio ${d.profixio || "saknas"}; SportAdmin ${d.sportadmin || "saknas"}`).join(" | ");
      const differenceCell = cell(details || "–"); differenceCell.className = "differences-column";
      row.append(differenceCell); body.append(row);
    }
  }
  filter.addEventListener("change", showEvents);
  differencesToggle.addEventListener("change", () => table.classList.toggle("hide-differences", !differencesToggle.checked));
  showEvents();
}
fetch("data/matches.json").then(response => { if (!response.ok) throw new Error("Kunde inte läsa matchdata"); return response.json(); }).then(render).catch(error => { const notice = document.querySelector("#error"); notice.textContent = error.message; notice.hidden = false; });
