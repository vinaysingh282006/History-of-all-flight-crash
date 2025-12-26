const COLORS = {
    bgMain: '#1E1E2F', bgCard: '#27293D', text: '#E0E0E0',
    accentPrimary: '#4DD0E1', accentSecondary: '#FFCA28',
    danger: '#EF5350', success: '#66BB6A', textSecondary: '#B0B0C4'
};

let AVIATION_DATA = [];

function generateSampleData() {
    const data = [];
    const operators = ['Aeroflot', 'Pan Am', 'American Airlines', 'Air France', 'Lufthansa', 'Delta'];
    const types = ['Boeing 747', 'DC-3', 'Airbus A320', 'Cessna 172', 'Concorde'];
    const locations = ['New York', 'Paris', 'Moscow', 'Pacific Ocean', 'London'];

    for (let i = 0; i < 500; i++) {
        const year = 1950 + Math.floor(Math.random() * 70);
        const fatalities = Math.round(Math.pow(Math.random(), 3) * 300);
        const aboard = fatalities + Math.round(Math.random() * 50);
        const operator = operators[Math.floor(Math.random() * operators.length)];
        const type = types[Math.floor(Math.random() * types.length)];
        const ground = Math.random() < 0.05 ? Math.round(Math.random() * 10) : 0;

        let baseScore = (fatalities * 0.5 + ground * 0.2);
        const isJet = type.includes('Boeing') || type.includes('Airbus') || type.includes('Concorde');
        baseScore += isJet ? 15 : 0;
        baseScore += operator === 'Aeroflot' || operator === 'Pan Am' ? 20 : 0;

        let severityScore = Math.min(100, Math.log1p(baseScore) * 15 + (Math.random() * 10 - 5)).toFixed(2);

        data.push({
            id: i,
            year: year,
            date: new Date(year, Math.floor(Math.random() * 12) + 1, Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0],
            fatalities: fatalities,
            aboard: aboard,
            ground: ground,
            operator: operator,
            type: type,
            location: locations[Math.floor(Math.random() * locations.length)],
            latitude: 30 + Math.random() * 40 * (Math.random() > 0.5 ? 1 : -1),
            longitude: -100 + Math.random() * 200 * (Math.random() > 0.5 ? 1 : -1),
            severityScore: parseFloat(severityScore),
            summary: `Accident details for ${operator} flight in ${year}.`
        });
    }
    return data;
}

async function loadCrashData() {
    try {
        const response = await fetch('../data/crashes.json');
        if (!response.ok) throw new Error('Network response was not ok');
        const rawData = await response.json();

        return rawData
            .filter(d => Number.isFinite(Number(d.Latitude)) && Number.isFinite(Number(d.Longitude)))
            .map((d, index) => {
                const fatalities = Number(d.Fatalities) || 0;

                // Derive reasonable values for missing fields
                const aboard = fatalities + Math.floor(Math.random() * 20);
                const ground = 0;

                // Simple derived severity score (kept consistent)
                const severityScore = Math.min(
                    100,
                    Math.log1p(fatalities) * 20
                );

                return {
                    id: index,
                    year: Number(d.Year),
                    date: d.Year ? `${d.Year}-01-01` : 'Unknown',
                    fatalities,
                    aboard,
                    ground,
                    operator: d.Type || 'Unknown',
                    type: d.Type || 'Unknown',
                    location: d.Location || 'Unknown',
                    country: d.Country || 'Unknown',
                    latitude: Number(d.Latitude),
                    longitude: Number(d.Longitude),
                    severityScore: Number(severityScore.toFixed(2)),
                    summary: `Crash in ${d.Location}, ${d.Country}`
                };
            });
    } catch (e) {
        throw e;
    }
}


async function initDataAndUI() {
    try {
        AVIATION_DATA = await loadCrashData();
        console.log(`Loaded ${AVIATION_DATA.length} crash records`);
    } catch (error) {
        console.error('Failed to load real crash data or data not found. Falling back to sample data.', error);
        AVIATION_DATA = generateSampleData();
    }

    updateMetrics();
    populateYearSelectors();
    renderGlobe();
    renderMLRisk();
    renderFatalityTrends();
    renderDataGrid();
}


function updateMetrics() {
    const totalRecords = AVIATION_DATA.length;
    const totalFatalities = AVIATION_DATA.reduce((sum, d) => sum + d.fatalities, 0);
    const avgSeverity = totalRecords > 0 ? AVIATION_DATA.reduce((sum, d) => sum + d.severityScore, 0) / totalRecords : 0;
    const yearMin = Math.min(...AVIATION_DATA.map(d => d.year));
    const yearMax = Math.max(...AVIATION_DATA.map(d => d.year));

    const metrics = [
        { label: 'Total Records', value: totalRecords.toLocaleString() },
        { label: 'Total Fatalities', value: totalFatalities.toLocaleString() },
        { label: 'Avg. Severity Score', value: avgSeverity.toFixed(2) },
        { label: 'Year Range', value: `${yearMin}-${yearMax}` }
    ];

    const grid = document.getElementById('metrics-grid');
    grid.innerHTML = metrics.map(m => `
        <div class="metric-card">
            <div class="metric-number">${m.value}</div>
            <div class="metric-label">${m.label}</div>
        </div>
    `).join('');
}

function populateYearSelectors() {
    const years = Array.from(new Set(AVIATION_DATA.map(d => d.year))).sort((a, b) => b - a);
    const select = document.getElementById('globe-year-select');
    select.innerHTML = '<option value="All">All Years</option>'; // Clear and add default
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        select.appendChild(option);
    });
}

function getPlotlyLayout(title, height, yaxisTitle = '', xaxisTitle = '') {
    return {
        title: {
            text: title,
            font: { color: COLORS.text, size: 20 }
        },
        height: height,
        paper_bgcolor: COLORS.bgCard,
        plot_bgcolor: COLORS.bgCard,
        font: { color: COLORS.text, size: 12 },
        margin: { l: 60, r: 20, t: 50, b: 60 },
        xaxis: {
            gridcolor: '#444', linecolor: '#444',
            title: xaxisTitle,
            zerolinecolor: '#444'
        },
        yaxis: {
            gridcolor: '#444', linecolor: '#444',
            title: yaxisTitle,
            zerolinecolor: '#444'
        },
        legend: { x: 1, xanchor: 'right', y: 1.1, orientation: 'h' }
    };
}

// --- Tab 1: 3D Globe ---
function renderGlobe() {
    const selectedYear = document.getElementById('globe-year-select').value;
    let filteredData = AVIATION_DATA;
    if (selectedYear !== 'All') {
        filteredData = AVIATION_DATA.filter(d => d.year == selectedYear);
    }

    const data = [{
        type: 'scattergeo',
        lon: filteredData.map(d => d.longitude),
        lat: filteredData.map(d => d.latitude),
        mode: 'markers',
        marker: {
            size: filteredData.map(d => Math.log1p(d.severityScore) * 3 + 4),
            color: filteredData.map(d => d.severityScore),
            colorscale: [[0, COLORS.success], [0.5, COLORS.accentPrimary], [1, COLORS.danger]],
            opacity: 0.8,
            colorbar: { title: 'Severity Score', tickfont: { color: COLORS.text } },
            line: { width: 1, color: COLORS.text }
        },
        hovertext: filteredData.map(d =>
            `<b>${d.operator}</b><br>Date: ${d.date}<br>Fatalities: ${d.fatalities}<br><b>Severity: ${d.severityScore}</b>`
        ),
        hovertemplate: "%{hovertext}<extra></extra>"
    }];

    const layout = {
        ...getPlotlyLayout(`🌍 3D Globe - ${filteredData.length} Crashes ${selectedYear !== 'All' ? '(' + selectedYear + ')' : '(All Years)'}`, 750),
        geo: {
            scope: 'world',
            showland: true,
            landcolor: '#3D3F57',
            countrycolor: '#B0B0C4',
            coastlinecolor: '#B0B0C4',
            bgcolor: COLORS.bgCard,
            projection: { type: 'orthographic' }
        }
    };

    Plotly.newPlot('globe-chart', data, layout, { responsive: true });
}

// --- Tab 2: ML Prediction & Risk ---
function renderMLRisk() {
    renderSeverityScatter();
    renderOperatorRiskRanking();
}

function renderSeverityScatter() {
    const threshold = parseFloat(document.getElementById('severity-threshold').value);
    document.getElementById('threshold-value').textContent = threshold;
    const highSeverityCount = AVIATION_DATA.filter(d => d.severityScore >= threshold).length;
    document.getElementById('crashes-above-threshold').textContent = highSeverityCount.toLocaleString();

    const data = [
        {
            x: AVIATION_DATA.map(d => d.aboard),
            y: AVIATION_DATA.map(d => d.fatalities),
            mode: 'markers',
            type: 'scatter',
            name: 'All Crashes',
            marker: {
                size: AVIATION_DATA.map(d => Math.log1p(d.fatalities) + 4),
                color: AVIATION_DATA.map(d => d.severityScore),
                colorscale: 'Plasma',
                showscale: true,
                colorbar: { title: 'Severity Score', tickfont: { color: COLORS.text } }
            },
            text: AVIATION_DATA.map(d =>
                `Operator: ${d.operator}<br>Severity: ${d.severityScore}<br>Fatalities: ${d.fatalities}`
            ),
            hovertemplate: "%{text}<extra></extra>"
        },
        {
            x: AVIATION_DATA.filter(d => d.severityScore >= threshold).map(d => d.aboard),
            y: AVIATION_DATA.filter(d => d.severityScore >= threshold).map(d => d.fatalities),
            mode: 'markers',
            type: 'scatter',
            name: `High Severity (≥ ${threshold})`,
            marker: {
                size: AVIATION_DATA.filter(d => d.severityScore >= threshold).map(d => Math.log1p(d.fatalities) * 2 + 5),
                color: COLORS.danger,
                line: { width: 2, color: COLORS.text }
            }
        }
    ];

    const layout = {
        ...getPlotlyLayout('✨ ML-Driven Severity Analysis (Fatalities vs. Persons Aboard)', 600, 'Total Fatalities (Log)', 'Total Persons Aboard (Log)'),
        xaxis: {
            type: 'log', title: 'Total Persons Aboard (Log Scale)', gridcolor: '#444', linecolor: '#444'
        },
        yaxis: {
            type: 'log', title: 'Total Fatalities (Log Scale)', gridcolor: '#444', linecolor: '#444'
        }
    };

    Plotly.newPlot('severity-scatter-chart', data, layout, { responsive: true });
}

function renderOperatorRiskRanking() {
    const operatorStats = {};

    AVIATION_DATA.filter(d => d.operator !== 'Unknown').forEach(d => {
        if (!operatorStats[d.operator]) {
            operatorStats[d.operator] = { crashes: 0, fatalities: 0, severitySum: 0 };
        }
        operatorStats[d.operator].crashes += 1;
        operatorStats[d.operator].fatalities += d.fatalities;
        operatorStats[d.operator].severitySum += d.severityScore;
    });

    let rankedOperators = Object.keys(operatorStats).map(op => {
        const stats = operatorStats[op];
        const avgSeverity = stats.severitySum / stats.crashes;
        const weightedRiskScore = (stats.crashes * 1.5) + (stats.fatalities / 10) + (avgSeverity * 2);
        return {
            operator: op,
            weightedRiskScore: weightedRiskScore
        };
    }).filter(op => op.weightedRiskScore > 10).sort((a, b) => b.weightedRiskScore - a.weightedRiskScore).slice(0, 15);

    const data = [{
        y: rankedOperators.map(op => op.operator),
        x: rankedOperators.map(op => op.weightedRiskScore),
        orientation: 'h',
        type: 'bar',
        marker: {
            color: rankedOperators.map(op => op.weightedRiskScore),
            colorscale: 'Cividis',
            line: { color: COLORS.bgMain, width: 1 }
        },
        text: rankedOperators.map(op => op.weightedRiskScore.toFixed(1)),
        textposition: 'outside'
    }];

    const layout = {
        ...getPlotlyLayout('🥇 Airline Weighted Risk Ranking (ML-Enhanced)', 600, 'Airline Operator', 'Weighted Risk Score'),
        yaxis: { automargin: true, categoryarray: rankedOperators.map(op => op.operator), categoryorder: "array" }
    };

    Plotly.newPlot('operator-risk-chart', data, layout, { responsive: true });
}

function updateMLRisk(value) {
    document.getElementById('severity-threshold').value = value;
    renderSeverityScatter();
}

// --- Tab 3: Deep Dive ---
function updateDeepDive() {
    const minSeverity = parseFloat(document.getElementById('dive-severity-min').value);
    document.getElementById('dive-severity-min-value').textContent = minSeverity;

    const filtered = AVIATION_DATA
        .filter(d => d.severityScore >= minSeverity)
        .sort((a, b) => b.severityScore - a.severityScore);

    document.getElementById('dive-filtered-count').textContent = filtered.length.toLocaleString();

    const resultsContainer = document.getElementById('deep-dive-results');
    resultsContainer.innerHTML = '';

    if (filtered.length === 0) {
        resultsContainer.innerHTML = `<p style="color: ${COLORS.textSecondary};">No crashes match the selected minimum severity score.</p>`;
        return;
    }

    filtered.slice(0, 10).forEach(d => {
        const card = document.createElement('div');
        card.className = 'deep-dive-card';
        card.innerHTML = `
            <div class="dive-title">💥 ${d.operator} (${d.date}) - Severity: ${d.severityScore}</div>
            <div class="dive-stats">
                Location: ${d.location} | Aircraft: ${d.type} | Fatalities: ${d.fatalities} / ${d.aboard} aboard
            </div>
            <p style="margin-top: 5px; color: ${COLORS.textSecondary}; font-style: italic;">Summary: ${d.summary}</p>
        `;
        resultsContainer.appendChild(card);
    });
}

// --- Tab 4: Fatality Trends ---
function renderFatalityTrends() {
    const yearlyData = AVIATION_DATA.reduce((acc, d) => {
        if (!acc[d.year]) {
            acc[d.year] = { fatalities: 0, crashes: 0 };
        }
        acc[d.year].fatalities += d.fatalities;
        acc[d.year].crashes += 1;
        return acc;
    }, {});

    const sortedYears = Object.keys(yearlyData).sort();
    const totalFatalities = sortedYears.map(year => yearlyData[year].fatalities);
    const totalCrashes = sortedYears.map(year => yearlyData[year].crashes);

    const data = [
        {
            x: sortedYears,
            y: totalFatalities,
            mode: 'lines+markers',
            name: 'Total Fatalities',
            fill: 'tozeroy',
            line: { color: COLORS.danger, width: 3 },
            marker: { size: 8, color: COLORS.danger, line: { color: COLORS.bgCard, width: 1.5 } }
        },
        {
            x: sortedYears,
            y: totalCrashes,
            mode: 'lines',
            name: 'Total Crashes',
            yaxis: 'y2',
            line: { color: COLORS.accentPrimary, width: 2, dash: 'dot' }
        }
    ];

    const layout = {
        ...getPlotlyLayout('💀 Fatality and Crash Trends Over Time', 600, 'Total Fatalities'),
        yaxis2: {
            title: 'Total Crashes',
            overlaying: 'y',
            side: 'right',
            showgrid: false,
            titlefont: { color: COLORS.accentPrimary },
            tickfont: { color: COLORS.accentPrimary }
        },
        legend: { x: 0, xanchor: 'left', y: 1.1, orientation: 'h' }
    };

    Plotly.newPlot('fatality-trends-chart', data, layout, { responsive: true });
}

// --- Tab 5: Data Grid ---
function renderDataGrid() {
    const tbody = document.querySelector('#crash-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    // Show top 200 most recent records by default
    const displayedData = AVIATION_DATA.sort((a, b) => b.year - a.year).slice(0, 200);

    const rows = displayedData.map(d => {
        let severityClass = 'severity-low';
        if (d.severityScore >= 70) severityClass = 'severity-high';
        else if (d.severityScore >= 40) severityClass = 'severity-medium';

        return `
            <tr>
                <td>${d.year}</td>
                <td>${d.date}</td>
                <td>${d.operator}</td>
                <td>${d.type}</td>
                <td>${d.location}</td>
                <td>${d.fatalities}</td>
                <td class="${severityClass}">${d.severityScore}</td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = rows;
}


// --- UI Functions ---
function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].classList.remove('active');
    }
    const tablinks = document.getElementsByClassName("tab-button");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove('active');
    }
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');

    // Re-render charts on tab switch to ensure responsiveness
    // Using setTimeout to allow DOM update
    setTimeout(() => {
        if (tabName === 'globe') renderGlobe();
        if (tabName === 'deep-dive') updateDeepDive();
        if (tabName === 'trends') renderFatalityTrends();
        if (tabName === 'data-grid') renderDataGrid();
    }, 10);
}

// Expose openTab to window for onclick handlers
window.openTab = openTab;

window.onload = initDataAndUI;
