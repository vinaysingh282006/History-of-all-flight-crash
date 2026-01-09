/* =========================================================
   MAP SETUP
========================================================= */

const map = L.map("map").setView([20, 0], 2);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const markers = L.markerClusterGroup({
  spiderfyOnMaxZoom: true,
  showCoverageOnHover: false,
  zoomToBoundsOnClick: true,
  maxClusterRadius: 80,
});



/* =========================================================
   GLOBAL STATE
========================================================= */

let crashData = [];

let chart = null;
let timelineChart = null;
let operatorChart = null;

const weatherCache = new Map();



/* =========================================================
   ERROR HANDLING
========================================================= */

window.addEventListener("error", (e) => console.error(e.message));
window.addEventListener("unhandledrejection", (e) => console.error(e.reason));



/* =========================================================
   DATA NORMALIZATION
========================================================= */

function normalizeCrashData(data) {
  return data.map((c) => ({
    ...c,
    Year: Number(c.Year) || 0,
    Fatalities: Number(c.Fatalities) || 0,
    Latitude: Number(c.Latitude),
    Longitude: Number(c.Longitude),
    Country: c.Country || "Unknown",
    Type: c.Type || "Unknown",
    Location: c.Location || "Unknown",
  }));
}



/* =========================================================
   DATA LOADING
========================================================= */

async function loadData() {
  try {
    const res = await fetch("data/crashes.json");

    if (!res.ok) throw new Error(res.statusText);

    const raw = await res.json();

    crashData = normalizeCrashData(raw);

    renderMarkers(crashData);
    updateAnalytics(crashData);
    updateTimeline(crashData);

  } catch (e) {
    const stats = document.getElementById("stats");
    if (stats) stats.innerHTML = `<p style="color:red">${e.message}</p>`;
  }
}



/* =========================================================
   MAP MARKERS
========================================================= */

function renderMarkers(data) {
  markers.clearLayers();

  data.forEach((crash) => {
    if (!crash.Latitude || !crash.Longitude) return;

    let color = "green";
    if (crash.Fatalities > 50) color = "red";
    else if (crash.Fatalities > 10) color = "orange";
    else if (crash.Fatalities > 0) color = "yellow";

    const id = `${crash.Year}-${crash.Location.replace(/\s+/g, "-")}`;

    const marker = L.circleMarker([crash.Latitude, crash.Longitude], {
      radius: Math.max(5, Math.min(15, crash.Fatalities / 10)),
      fillColor: color,
      color: "#000",
      weight: 1,
      fillOpacity: 0.7,
    }).bindPopup(`
        <b>${crash.Location}</b><br>
        Year: ${crash.Year}<br>
        Type: ${crash.Type}<br>
        Fatalities: ${crash.Fatalities}<br>
        Country: ${crash.Country}<br>
        <div id="weather-${id}">Loading...</div>
        <button onclick="fetchWeather(${crash.Latitude}, ${crash.Longitude}, '${id}')">
          Load Weather
        </button>
    `);

    markers.addLayer(marker);
  });

  map.addLayer(markers);
}



/* =========================================================
   WEATHER HANDLING
========================================================= */

async function fetchWeather(lat, lon, id) {
  const key = `${lat}_${lon}`;

  if (weatherCache.has(key)) {
    document.getElementById(`weather-${id}`).innerHTML = weatherCache.get(key);
    return;
  }

  try {
    const res = await fetch(
      `${WEATHER_API_URL}?lat=${lat}&lon=${lon}&appid=${WEATHER_API_KEY}&units=metric`
    );

    if (!res.ok) throw new Error(res.statusText);

    const w = await res.json();

    const html = `
      Temp: ${w.main.temp}°C<br>
      Humidity: ${w.main.humidity}%<br>
      Wind: ${w.wind.speed} m/s
    `;

    weatherCache.set(key, html);
    document.getElementById(`weather-${id}`).innerHTML = html;

  } catch {
    document.getElementById(`weather-${id}`).innerHTML = "Weather unavailable";
  }
}



/* =========================================================
   ANALYTICS
========================================================= */

function updateAnalytics(data) {
  const totalFatalities = data.reduce((s, d) => s + d.Fatalities, 0);

  document.getElementById("count").textContent = data.length;
  document.getElementById("fatalities").textContent = totalFatalities;
  document.getElementById("avg").textContent = data.length
    ? (totalFatalities / data.length).toFixed(1)
    : 0;

  const decade = {};
  data.forEach((d) => {
    const k = Math.floor(d.Year / 10) * 10;
    decade[k] = (decade[k] || 0) + 1;
  });

  if (chart) chart.destroy();

  chart = new Chart(document.getElementById("chart"), {
    type: "bar",
    data: {
      labels: Object.keys(decade),
      datasets: [{ label: "Crashes", data: Object.values(decade) }],
    },
    options: { responsive: true },
  });

  updateOperatorAnalysis(data);
}



/* =========================================================
   OPERATOR / TYPE ANALYSIS
========================================================= */

function updateOperatorAnalysis(data) {
  const grouped = {};

  data.forEach((d) => {
    grouped[d.Type] = grouped[d.Type] || { c: 0, f: 0 };
    grouped[d.Type].c++;
    grouped[d.Type].f += d.Fatalities;
  });

  const top = Object.entries(grouped).slice(0, 8);

  if (operatorChart) operatorChart.destroy();

  operatorChart = new Chart(document.getElementById("operator-chart"), {
    type: "bar",
    data: {
      labels: top.map((i) => i[0]),
      datasets: [
        { label: "Crashes", data: top.map((i) => i[1].c) },
        { label: "Fatalities", data: top.map((i) => i[1].f) },
      ],
    },
    options: { responsive: true },
  });
}



/* =========================================================
   TIMELINE
========================================================= */

function updateTimeline(data) {
  const yearly = {};

  data.forEach((d) => {
    yearly[d.Year] = (yearly[d.Year] || 0) + 1;
  });

  if (timelineChart) timelineChart.destroy();

  timelineChart = new Chart(document.getElementById("timeline-chart"), {
    type: "line",
    data: {
      labels: Object.keys(yearly),
      datasets: [{ label: "Crashes", data: Object.values(yearly) }],
    },
    options: { responsive: true },
  });
}



/* =========================================================
   FILTERING
========================================================= */

let filterTimeout = null;

function applyFiltersDebounced() {
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(applyFilters, 250);
}

function applyFilters() {
  const minY = +yearMin.value || 0;
  const maxY = +yearMax.value || 9999;
  const type = typeFilter.value;
  const region = regionFilter.value.toLowerCase();
  const minF = +fatalFilter.value || 0;

  const filtered = crashData.filter(
    (c) =>
      c.Year >= minY &&
      c.Year <= maxY &&
      (type === "All" || c.Type === type) &&
      (!region || c.Country.toLowerCase().includes(region)) &&
      c.Fatalities >= minF
  );

  renderMarkers(filtered);
  updateAnalytics(filtered);
  updateTimeline(filtered);
}



/* =========================================================
   EVENTS
========================================================= */

document.getElementById("applyFilter")
  .addEventListener("click", applyFiltersDebounced);

document.getElementById("resetFilter")
  .addEventListener("click", () => {
    renderMarkers(crashData);
    updateAnalytics(crashData);
    updateTimeline(crashData);
  });



/* =========================================================
   INIT
========================================================= */

loadData();
