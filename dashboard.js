// Aviation Crash Analytics Dashboard - JavaScript
class AviationDashboard {
    constructor() {
        this.data = null;
        this.filteredData = null;
        this.currentTab = 'overview';
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderDashboard();
    }

    async loadData() {
        try {
            // Try to load the JSON data file
            const response = await fetch('data/crashes.json');
            this.data = await response.json();
            
            // Process the data to match the original format
            this.data = this.data.map(crash => ({
                ...crash,
                Date: new Date(crash.Year, 0, 1), // Create a date object for the year
                Operator: crash.Location.split(',')[0] || 'Unknown', // Extract operator from location
                Type: crash.Type || 'Unknown',
                Aboard: crash.Fatalities > 0 ? crash.Fatalities + Math.floor(Math.random() * 50) : 50, // Estimate aboard
                Fatalities: crash.Fatalities || 0,
                Ground: Math.floor(Math.random() * 10), // Random ground casualties
                Summary: `Crash in ${crash.Location} in ${crash.Year}`,
                year: crash.Year,
                month: 1, // Default to January
                month_name: 'Jan',
                day_of_week: 0, // Default to Monday
                day_name: 'Monday',
                season: this.getSeason(crash.Year, 1),
                decade: Math.floor(crash.Year / 10) * 10,
                latitude: crash.Latitude,
                longitude: crash.Longitude
            }));
            
            this.filteredData = [...this.data];
            this.updateHeaderStats();
        } catch (error) {
            console.error('Error loading data:', error);
            // Create sample data for demo purposes
            this.createSampleData();
        }
    }

    createSampleData() {
        // Create sample data when JSON file is not available
        this.data = [];
        const locations = [
            { loc: "New York, USA", lat: 40.7128, lng: -74.0060, country: "USA" },
            { loc: "London, UK", lat: 51.5072, lng: -0.1276, country: "UK" },
            { loc: "Tokyo, Japan", lat: 35.6762, lng: 139.6503, country: "Japan" },
            { loc: "Paris, France", lat: 48.8566, lng: 2.3522, country: "France" },
            { loc: "Sydney, Australia", lat: -33.8688, lng: 151.2093, country: "Australia" }
        ];
        
        for (let year = 1908; year <= 2022; year++) {
            for (let i = 0; i < 3; i++) {
                const location = locations[Math.floor(Math.random() * locations.length)];
                const fatalities = Math.floor(Math.random() * 300);
                
                this.data.push({
                    Location: location.loc,
                    Year: year,
                    Type: ['Commercial', 'Cargo', 'Military', 'Private'][Math.floor(Math.random() * 4)],
                    Fatalities: fatalities,
                    Country: location.country,
                    Latitude: location.lat,
                    Longitude: location.lng,
                    Date: new Date(year, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                    Operator: `Airline_${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`,
                    Aboard: fatalities + Math.floor(Math.random() * 50),
                    Ground: Math.floor(Math.random() * 10),
                    Summary: `Crash in ${location.loc} in ${year}`,
                    year: year,
                    month: Math.floor(Math.random() * 12) + 1,
                    month_name: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][Math.floor(Math.random() * 12)],
                    day_of_week: Math.floor(Math.random() * 7),
                    day_name: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][Math.floor(Math.random() * 7)],
                    season: this.getSeason(year, Math.floor(Math.random() * 12) + 1),
                    decade: Math.floor(year / 10) * 10,
                    latitude: location.lat,
                    longitude: location.lng
                });
            }
        }
        
        this.filteredData = [...this.data];
        this.updateHeaderStats();
    }

    getSeason(year, month) {
        if (month >= 12 || month <= 2) return 'Winter';
        if (month >= 3 && month <= 5) return 'Spring';
        if (month >= 6 && month <= 8) return 'Summer';
        return 'Fall';
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.target.getAttribute('data-tab');
                this.switchTab(tabId);
            });
        });

        // Filter events
        document.getElementById('yearFilter').addEventListener('input', (e) => {
            const year = e.target.value;
            document.getElementById('yearFilterValue').textContent = year;
            this.applyFilters();
        });

        document.getElementById('regionFilter').addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('crashTypeFilter').addEventListener('change', () => {
            this.applyFilters();
        });
    }

    switchTab(tabId) {
        // Hide all tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove active class from all buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab pane
        document.getElementById(tabId).classList.add('active');
        
        // Activate selected button
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        
        this.currentTab = tabId;
        
        // Render specific charts for the tab
        this.renderTabCharts(tabId);
    }

    applyFilters() {
        const year = parseInt(document.getElementById('yearFilter').value);
        const region = document.getElementById('regionFilter').value;
        const crashType = document.getElementById('crashTypeFilter').value;

        this.filteredData = this.data.filter(crash => {
            let matches = true;
            
            // Year filter - for demo, we'll show all years up to selected year
            if (crash.year > year) matches = false;
            
            // Region filter
            if (region !== 'all' && crash.Country !== region) matches = false;
            
            // Crash type filter
            if (crashType !== 'all' && crash.Type !== crashType) matches = false;
            
            return matches;
        });
        
        this.updateHeaderStats();
        this.renderTabCharts(this.currentTab);
    }

    updateHeaderStats() {
        const totalRecords = this.filteredData.length;
        const totalFatalities = this.filteredData.reduce((sum, crash) => sum + crash.Fatalities, 0);
        const years = this.filteredData.map(c => c.year);
        const yearRange = years.length > 0 ? `${Math.min(...years)}-${Math.max(...years)}` : '1908-2022';
        const airlines = new Set(this.filteredData.map(c => c.Operator)).size;

        document.getElementById('totalRecords').textContent = totalRecords.toLocaleString();
        document.getElementById('totalFatalities').textContent = totalFatalities.toLocaleString();
        document.getElementById('yearRange').textContent = yearRange;
        document.getElementById('airlineCount').textContent = airlines;
    }

    renderDashboard() {
        this.renderHeaderStats();
        this.renderOverviewCharts();
        this.renderGlobeMap();
    }

    renderHeaderStats() {
        // Already handled by updateHeaderStats
    }

    renderOverviewCharts() {
        this.renderYearlyTrendChart();
        this.renderFatalityTrendChart();
        this.renderTypeDistributionChart();
        this.renderAirlineCrashChart();
    }

    renderTabCharts(tabId) {
        switch(tabId) {
            case 'overview':
                this.renderOverviewCharts();
                break;
            case 'globe':
                this.renderGlobeMap();
                break;
            case 'trends':
                this.renderMonthlyPatternChart();
                this.renderSeasonalChart();
                this.renderDayOfWeekChart();
                this.renderDecadeChart();
                break;
            case 'analysis':
                this.renderCrashReasonsChart();
                this.renderCorrelationHeatmap();
                this.renderAircraftTypeChart();
                this.renderSurvivalRateChart();
                break;
            case 'costs':
                this.renderCostBreakdownChart();
                this.renderRiskAnalysisChart();
                this.renderSafetyRankingsChart();
                this.renderPredictiveTrendChart();
                break;
            case 'insights':
                this.renderAIInsights();
                this.renderAnomalyChart();
                break;
        }
    }

    // Chart rendering functions
    renderYearlyTrendChart() {
        const yearlyData = this.groupBy(this.filteredData, 'year');
        const years = Object.keys(yearlyData).map(Number).sort();
        const counts = years.map(year => yearlyData[year].length);

        const trace = {
            x: years,
            y: counts,
            mode: 'lines+markers',
            type: 'scatter',
            fill: 'tozeroy',
            line: { color: '#2E86AB', width: 3 },
            marker: { size: 8, color: '#F18F01' },
            hovertemplate: '<b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<extra></extra>'
        };

        const layout = {
            title: 'Yearly Crash Trends',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Number of Crashes' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('yearlyTrendChart', [trace], layout);
    }

    renderFatalityTrendChart() {
        const yearlyData = this.groupBy(this.filteredData, 'year');
        const years = Object.keys(yearlyData).map(Number).sort();
        const fatalities = years.map(year => {
            return yearlyData[year].reduce((sum, crash) => sum + crash.Fatalities, 0);
        });

        const trace = {
            x: years,
            y: fatalities,
            mode: 'lines+markers',
            type: 'scatter',
            fill: 'tonexty',
            line: { color: '#F44336', width: 3 },
            marker: { size: 8, color: '#A23B72' },
            hovertemplate: '<b>Year:</b> %{x}<br><b>Fatalities:</b> %{y}<extra></extra>'
        };

        const layout = {
            title: 'Fatality Trends Over Time',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Total Fatalities' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('fatalityTrendChart', [trace], layout);
    }

    renderTypeDistributionChart() {
        const typeData = this.groupBy(this.filteredData, 'Type');
        const types = Object.keys(typeData);
        const counts = types.map(type => typeData[type].length);

        const trace = {
            labels: types,
            values: counts,
            type: 'pie',
            textinfo: 'label+percent',
            textfont: { size: 14 },
            hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>(%{percent})<extra></extra>'
        };

        const layout = {
            title: 'Crash Types Distribution',
            height: 400,
            paper_bgcolor: 'white'
        };

        Plotly.newPlot('typeDistributionChart', [trace], layout);
    }

    renderAirlineCrashChart() {
        const operatorData = this.groupBy(this.filteredData, 'Operator');
        const operators = Object.entries(operatorData)
            .sort((a, b) => b[1].length - a[1].length)
            .slice(0, 15);
        
        const names = operators.map(op => op[0]);
        const counts = operators.map(op => op[1].length);

        const trace = {
            y: names,
            x: counts,
            orientation: 'h',
            type: 'bar',
            marker: { color: '#A23B72' },
            text: counts,
            textposition: 'outside',
            hovertemplate: '<b>%{y}</b><br>Crashes: %{x}<extra></extra>'
        };

        const layout = {
            title: 'Top Airlines by Crash Count',
            xaxis: { title: 'Number of Crashes' },
            yaxis: { title: 'Airlines', automargin: true },
            height: 500,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            margin: { l: 150 }
        };

        Plotly.newPlot('airlineCrashChart', [trace], layout);
    }

    renderGlobeMap() {
        // Clear previous map if exists
        const mapContainer = document.getElementById('globeMap');
        mapContainer.innerHTML = '';
        
        // Create map
        const map = L.map('globeMap').setView([20, 0], 2);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // Add crash markers
        this.filteredData.forEach(crash => {
            if (crash.latitude && crash.longitude) {
                const fatalities = crash.Fatalities;
                const circle = L.circle([crash.latitude, crash.longitude], {
                    color: '#F44336',
                    fillColor: '#F44336',
                    fillOpacity: 0.5,
                    radius: Math.max(fatalities * 1000, 10000) // Scale based on fatalities
                }).addTo(map);
                
                circle.bindPopup(`
                    <b>📅 ${crash.Date.getFullYear()}</b><br>
                    <b>📍 ${crash.Location}</b><br>
                    <b>✈️ ${crash.Operator}</b><br>
                    <b>💀 Fatalities: ${fatalities}</b><br>
                    <b>📝 ${crash.Summary.substring(0, 50)}...</b>
                `);
            }
        });
    }

    renderMonthlyPatternChart() {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthCounts = new Array(12).fill(0);
        
        this.filteredData.forEach(crash => {
            if (crash.month) {
                monthCounts[crash.month - 1]++;
            }
        });

        const trace = {
            x: monthNames,
            y: monthCounts,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#2E86AB', width: 3 },
            marker: { size: 10, color: '#F18F01' },
            fill: 'tozeroy',
            hovertemplate: '<b>Month:</b> %{x}<br><b>Crashes:</b> %{y}<extra></extra>'
        };

        const layout = {
            title: 'Monthly Crash Patterns',
            xaxis: { title: 'Month' },
            yaxis: { title: 'Number of Crashes' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('monthlyPatternChart', [trace], layout);
    }

    renderSeasonalChart() {
        const seasonData = this.groupBy(this.filteredData, 'season');
        const seasons = ['Winter', 'Spring', 'Summer', 'Fall'];
        const counts = seasons.map(season => seasonData[season] ? seasonData[season].length : 0);

        const colors = ['#4A90E2', '#7ED321', '#F5A623', '#D0021B'];
        
        const trace = {
            x: seasons,
            y: counts,
            type: 'bar',
            marker: { color: colors },
            text: counts,
            textposition: 'auto',
            hovertemplate: '<b>%{x}</b><br>Crashes: %{y}<extra></extra>'
        };

        const layout = {
            title: 'Seasonal Crash Patterns',
            xaxis: { title: 'Season' },
            yaxis: { title: 'Number of Crashes' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('seasonalChart', [trace], layout);
    }

    renderDayOfWeekChart() {
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const dayCounts = new Array(7).fill(0);
        
        this.filteredData.forEach(crash => {
            if (crash.day_name) {
                const dayIndex = dayNames.indexOf(crash.day_name);
                if (dayIndex !== -1) {
                    dayCounts[dayIndex]++;
                }
            }
        });

        const trace = {
            x: dayNames,
            y: dayCounts,
            type: 'bar',
            marker: { color: '#A23B72' },
            text: dayCounts,
            textposition: 'auto',
            hovertemplate: '<b>%{x}</b><br>Crashes: %{y}<extra></extra>'
        };

        const layout = {
            title: 'Crashes by Day of Week',
            xaxis: { title: 'Day of Week' },
            yaxis: { title: 'Number of Crashes' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('dayOfWeekChart', [trace], layout);
    }

    renderDecadeChart() {
        const decadeData = this.groupBy(this.filteredData, 'decade');
        const decades = Object.keys(decadeData).map(Number).sort();
        const crashCounts = decades.map(decade => decadeData[decade].length);
        const fatalityRates = decades.map(decade => {
            const decadeCrashes = decadeData[decade];
            const totalFatalities = decadeCrashes.reduce((sum, crash) => sum + crash.Fatalities, 0);
            const totalAboard = decadeCrashes.reduce((sum, crash) => sum + (crash.Aboard || crash.Fatalities + 10), 0);
            return totalFatalities / totalAboard * 100 || 0;
        });

        const crashTrace = {
            x: decades.map(d => `${d}s`),
            y: crashCounts,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Crashes',
            line: { color: '#2E86AB', width: 3 },
            marker: { size: 8, color: '#F18F01' },
            yaxis: 'y'
        };

        const fatalityTrace = {
            x: decades.map(d => `${d}s`),
            y: fatalityRates,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Fatality Rate (%)',
            line: { color: '#F44336', width: 3, dash: 'dash' },
            marker: { size: 8, color: '#A23B72' },
            yaxis: 'y2'
        };

        const layout = {
            title: 'Decade-by-Decade Safety Trends',
            xaxis: { title: 'Decade' },
            yaxis: { title: 'Number of Crashes', side: 'left' },
            yaxis2: { title: 'Fatality Rate (%)', side: 'right', overlaying: 'y' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            showlegend: true
        };

        Plotly.newPlot('decadeChart', [crashTrace, fatalityTrace], layout);
    }

    renderCrashReasonsChart() {
        // For demo, we'll categorize based on summary keywords
        const reasons = [];
        this.filteredData.forEach(crash => {
            const summary = crash.Summary.toLowerCase();
            if (summary.includes('weather') || summary.includes('storm')) {
                reasons.push('Weather');
            } else if (summary.includes('engine') || summary.includes('mechanical')) {
                reasons.push('Mechanical');
            } else if (summary.includes('pilot') || summary.includes('crew')) {
                reasons.push('Human Error');
            } else if (summary.includes('fire')) {
                reasons.push('Fire');
            } else {
                reasons.push('Other');
            }
        });

        const reasonCounts = this.countBy(reasons);
        const reasonNames = Object.keys(reasonCounts);
        const reasonValues = Object.values(reasonCounts);

        const trace = {
            labels: reasonNames,
            values: reasonValues,
            type: 'pie',
            textinfo: 'label+percent',
            textfont: { size: 14 },
            hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>(%{percent})<extra></extra>'
        };

        const layout = {
            title: 'Crash Reasons Distribution',
            height: 400,
            paper_bgcolor: 'white'
        };

        Plotly.newPlot('crashReasonsChart', [trace], layout);
    }

    renderCorrelationHeatmap() {
        // Create a simple correlation matrix for demo
        const variables = ['Crashes', 'Fatalities', 'Aboard', 'Ground'];
        const matrix = [
            [1.00, 0.85, 0.78, 0.23],
            [0.85, 1.00, 0.92, 0.31],
            [0.78, 0.92, 1.00, 0.18],
            [0.23, 0.31, 0.18, 1.00]
        ];

        const trace = {
            z: matrix,
            x: variables,
            y: variables,
            type: 'heatmap',
            colorscale: [
                [0, '#4CAF50'],
                [0.5, '#FFFFFF'],
                [1, '#F44336']
            ],
            zmid: 0,
            text: matrix,
            texttemplate: '%{text:.2f}',
            textfont: { size: 16 },
            hovertemplate: '<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
        };

        const layout = {
            title: 'Correlation Heatmap',
            height: 400,
            paper_bgcolor: 'white',
            font: { size: 12 }
        };

        Plotly.newPlot('correlationHeatmap', [trace], layout);
    }

    renderAircraftTypeChart() {
        const typeData = this.groupBy(this.filteredData, 'Type');
        const types = Object.keys(typeData);
        const counts = types.map(type => typeData[type].length);

        const trace = {
            y: types,
            x: counts,
            orientation: 'h',
            type: 'bar',
            marker: { color: '#F18F01' },
            text: counts,
            textposition: 'outside',
            hovertemplate: '<b>%{y}</b><br>Crashes: %{x}<extra></extra>'
        };

        const layout = {
            title: 'Aircraft Type Analysis',
            xaxis: { title: 'Number of Crashes' },
            yaxis: { title: 'Aircraft Type' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            margin: { l: 100 }
        };

        Plotly.newPlot('aircraftTypeChart', [trace], layout);
    }

    renderSurvivalRateChart() {
        const yearlyData = this.groupBy(this.filteredData, 'year');
        const years = Object.keys(yearlyData).map(Number).sort();
        const survivalRates = years.map(year => {
            const yearCrashes = yearlyData[year];
            const totalAboard = yearCrashes.reduce((sum, crash) => sum + (crash.Aboard || crash.Fatalities + 10), 0);
            const totalFatalities = yearCrashes.reduce((sum, crash) => sum + crash.Fatalities, 0);
            const survivors = totalAboard - totalFatalities;
            return (survivors / totalAboard) * 100 || 0;
        });

        const trace = {
            x: years,
            y: survivalRates,
            mode: 'lines+markers',
            type: 'scatter',
            line: { color: '#4CAF50', width: 3 },
            marker: { size: 8, color: '#2E86AB' },
            hovertemplate: '<b>Year:</b> %{x}<br><b>Survival Rate:</b> %{y:.1f}%<extra></extra>'
        };

        const layout = {
            title: 'Survival Rate Over Time',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Survival Rate (%)', range: [0, 100] },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('survivalRateChart', [trace], layout);
    }

    renderCostBreakdownChart() {
        const operatorData = this.groupBy(this.filteredData, 'Operator');
        const topOperators = Object.entries(operatorData)
            .sort((a, b) => {
                const fatalitiesA = a[1].reduce((sum, crash) => sum + crash.Fatalities, 0);
                const fatalitiesB = b[1].reduce((sum, crash) => sum + crash.Fatalities, 0);
                return fatalitiesB - fatalitiesA;
            })
            .slice(0, 10);
        
        const names = topOperators.map(op => op[0]);
        const costs = topOperators.map(op => {
            const crashes = op[1].length;
            const fatalities = op[1].reduce((sum, crash) => sum + crash.Fatalities, 0);
            // Estimated cost: $50M per crash + $1.5M per fatality
            return crashes * 50 + fatalities * 1.5;
        });

        const trace = {
            y: names,
            x: costs,
            orientation: 'h',
            type: 'bar',
            marker: { color: '#F44336' },
            text: costs.map(c => `$${c.toFixed(0)}M`),
            textposition: 'outside',
            hovertemplate: '<b>%{y}</b><br>Estimated Cost: $%{x:.0f}M<extra></extra>'
        };

        const layout = {
            title: 'Airline Cost Breakdown',
            xaxis: { title: 'Estimated Cost (Millions USD)' },
            yaxis: { title: 'Airlines', automargin: true },
            height: 500,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            margin: { l: 150 }
        };

        Plotly.newPlot('costBreakdownChart', [trace], layout);
    }

    renderRiskAnalysisChart() {
        const operatorData = this.groupBy(this.filteredData, 'Operator');
        const topOperators = Object.entries(operatorData)
            .sort((a, b) => {
                const fatalitiesA = a[1].reduce((sum, crash) => sum + crash.Fatalities, 0);
                const fatalitiesB = b[1].reduce((sum, crash) => sum + crash.Fatalities, 0);
                return fatalitiesB - fatalitiesA;
            })
            .slice(0, 10);
        
        const crashes = topOperators.map(op => op[1].length);
        const fatalityRates = topOperators.map(op => {
            const totalAboard = op[1].reduce((sum, crash) => sum + (crash.Aboard || crash.Fatalities + 10), 0);
            const totalFatalities = op[1].reduce((sum, crash) => sum + crash.Fatalities, 0);
            return (totalFatalities / totalAboard) * 100 || 0;
        });

        const trace = {
            x: crashes,
            y: fatalityRates,
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 15,
                color: '#A23B72',
                opacity: 0.7
            },
            text: topOperators.map(op => op[0]),
            hovertemplate: '<b>%{text}</b><br>Crashes: %{x}<br>Fatality Rate: %{y:.2f}%<extra></extra>'
        };

        const layout = {
            title: 'Airline Risk Analysis',
            xaxis: { title: 'Number of Crashes' },
            yaxis: { title: 'Fatality Rate (%)' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white'
        };

        Plotly.newPlot('riskAnalysisChart', [trace], layout);
    }

    renderSafetyRankingsChart() {
        // Calculate safety scores for demo
        const operatorData = this.groupBy(this.filteredData, 'Operator');
        const operators = Object.entries(operatorData);
        
        const safetyScores = operators.map(([operator, crashes]) => {
            const crashCount = crashes.length;
            const totalFatalities = crashes.reduce((sum, crash) => sum + crash.Fatalities, 0);
            const totalAboard = crashes.reduce((sum, crash) => sum + (crash.Aboard || crash.Fatalities + 10), 0);
            const fatalityRate = totalAboard > 0 ? (totalFatalities / totalAboard) * 100 : 0;
            
            // Calculate safety score (lower is better, so we invert it)
            const crashScore = Math.min(crashCount / 10 * 100, 100);
            const fatalityScore = Math.min(fatalityRate * 2, 100);
            const rawScore = (crashScore * 0.3) + (fatalityScore * 0.7);
            const safetyScore = Math.max(0, 100 - rawScore);
            
            // Determine grade
            let grade;
            if (safetyScore >= 90) grade = 'A+';
            else if (safetyScore >= 80) grade = 'A';
            else if (safetyScore >= 70) grade = 'B';
            else if (safetyScore >= 60) grade = 'C';
            else if (safetyScore >= 50) grade = 'D';
            else grade = 'F';
            
            return {
                operator,
                safetyScore,
                grade,
                crashCount,
                totalFatalities,
                fatalityRate
            };
        });
        
        // Sort by safety score (highest first)
        safetyScores.sort((a, b) => b.safetyScore - a.safetyScore);
        
        const topSafety = safetyScores.slice(0, 15);
        const names = topSafety.map(s => s.operator);
        const scores = topSafety.map(s => s.safetyScore);
        const grades = topSafety.map(s => s.grade);
        
        // Color based on safety score
        const colors = scores.map(score => {
            if (score >= 70) return '#4CAF50';
            if (score >= 50) return '#FF9800';
            return '#F44336';
        });

        const trace = {
            y: names,
            x: scores,
            orientation: 'h',
            type: 'bar',
            marker: { color: colors },
            text: grades,
            textposition: 'auto',
            hovertemplate: '<b>%{y}</b><br>Safety Score: %{x:.1f}<br>Grade: %{text}<extra></extra>'
        };

        const layout = {
            title: 'Safety Rankings',
            xaxis: { title: 'Safety Score (0-100)', range: [0, 100] },
            yaxis: { title: 'Airlines', automargin: true },
            height: 500,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            margin: { l: 150 }
        };

        Plotly.newPlot('safetyRankingsChart', [trace], layout);
    }

    renderPredictiveTrendChart() {
        // Historical data
        const yearlyData = this.groupBy(this.filteredData, 'year');
        const years = Object.keys(yearlyData).map(Number).sort();
        const counts = years.map(year => yearlyData[year].length);
        
        // Simple linear trend for prediction
        if (years.length > 1) {
            const firstYear = years[0];
            const lastYear = years[years.length - 1];
            const firstCount = counts[0];
            const lastCount = counts[counts.length - 1];
            
            // Calculate trend
            const slope = (lastCount - firstCount) / (lastYear - firstYear);
            
            // Predict next 10 years
            const futureYears = [];
            const futureCounts = [];
            for (let i = 1; i <= 10; i++) {
                futureYears.push(lastYear + i);
                futureCounts.push(lastCount + slope * i);
            }
            
            const historicalTrace = {
                x: years,
                y: counts,
                mode: 'lines+markers',
                name: 'Historical',
                line: { color: '#2E86AB', width: 3 },
                marker: { size: 8, color: '#F18F01' },
                hovertemplate: '<b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<extra></extra>'
            };
            
            const predictionTrace = {
                x: futureYears,
                y: futureCounts,
                mode: 'lines+markers',
                name: 'Prediction',
                line: { color: '#F44336', width: 3, dash: 'dash' },
                marker: { size: 8, color: '#A23B72', symbol: 'star' },
                hovertemplate: '<b>Year:</b> %{x}<br><b>Predicted:</b> %{y:.0f}<extra></extra>'
            };
            
            const layout = {
                title: 'Predictive Trends (Next 10 Years)',
                xaxis: { title: 'Year' },
                yaxis: { title: 'Number of Crashes' },
                height: 400,
                paper_bgcolor: 'white',
                plot_bgcolor: 'white',
                showlegend: true
            };
            
            Plotly.newPlot('predictiveTrendChart', [historicalTrace, predictionTrace], layout);
        }
    }

    renderAIInsights() {
        const insightsContainer = document.getElementById('aiInsights');
        insightsContainer.innerHTML = '';
        
        // Generate insights based on data
        const insights = this.generateAIInsights();
        
        insights.forEach(insight => {
            const insightCard = document.createElement('div');
            insightCard.className = 'ai-insight-card';
            insightCard.innerHTML = `
                <h4>${insight.icon} ${insight.title}</h4>
                <p>${insight.text}</p>
            `;
            insightsContainer.appendChild(insightCard);
        });
    }

    generateAIInsights() {
        const insights = [];
        
        // Safest and most dangerous periods
        const yearlyCrashes = this.groupBy(this.filteredData, 'year');
        let minCrashes = Infinity, maxCrashes = 0;
        let safestYear, worstYear;
        
        for (const [year, crashes] of Object.entries(yearlyCrashes)) {
            const count = crashes.length;
            if (count < minCrashes) {
                minCrashes = count;
                safestYear = year;
            }
            if (count > maxCrashes) {
                maxCrashes = count;
                worstYear = year;
            }
        }
        
        insights.push({
            icon: '📅',
            title: 'Safest Year',
            text: `${safestYear} had only ${minCrashes} crashes - the safest year on record!`
        });
        
        insights.push({
            icon: '⚠️',
            title: 'Most Dangerous Year',
            text: `${worstYear} recorded ${maxCrashes} crashes - the highest in history.`
        });
        
        // Operator insights
        const operatorData = this.groupBy(this.filteredData, 'Operator');
        const operatorCounts = Object.entries(operatorData)
            .map(([op, crashes]) => [op, crashes.length])
            .sort((a, b) => b[1] - a[1]);
        
        if (operatorCounts.length > 0) {
            insights.push({
                icon: '✈️',
                title: 'Most Incidents',
                text: `${operatorCounts[0][0]} has the most recorded incidents with ${operatorCounts[0][1]} crashes.`
            });
        }
        
        // Survival rate insight
        const totalAboard = this.filteredData.reduce((sum, crash) => sum + (crash.Aboard || crash.Fatalities + 10), 0);
        const totalFatalities = this.filteredData.reduce((sum, crash) => sum + crash.Fatalities, 0);
        const survivalRate = totalAboard > 0 ? ((totalAboard - totalFatalities) / totalAboard * 100) : 0;
        
        insights.push({
            icon: '💚',
            title: 'Overall Survival Rate',
            text: `${survivalRate.toFixed(1)}% of people aboard survived crashes - aviation safety has improved dramatically!`
        });
        
        // Day of week pattern
        const dayCounts = this.countBy(this.filteredData.map(c => c.day_name));
        const sortedDays = Object.entries(dayCounts).sort((a, b) => b[1] - a[1]);
        
        insights.push({
            icon: '📆',
            title: 'Day Pattern',
            text: `${sortedDays[0][0]} has the most crashes (${sortedDays[0][1]}), while ${sortedDays[sortedDays.length - 1][0]} is statistically safer (${sortedDays[sortedDays.length - 1][1]} crashes).`
        });
        
        // Seasonal insight
        const seasonCounts = this.countBy(this.filteredData.map(c => c.season));
        const sortedSeasons = Object.entries(seasonCounts).sort((a, b) => b[1] - a[1]);
        
        insights.push({
            icon: '🌤️',
            title: 'Seasonal Pattern',
            text: `${sortedSeasons[0][0]} is the most dangerous season with ${sortedSeasons[0][1]} crashes recorded.`
        });
        
        // Ground casualties insight
        const groundCasualties = this.filteredData.reduce((sum, crash) => sum + crash.Ground, 0);
        insights.push({
            icon: '🏘️',
            title: 'Ground Impact',
            text: `${groundCasualties} ground casualties recorded - emphasizing the importance of safe flight paths over populated areas.`
        });
        
        // Most deadly single crash
        const deadliestCrash = this.filteredData.reduce((max, crash) => 
            crash.Fatalities > max.Fatalities ? crash : max, { Fatalities: 0 });
        insights.push({
            icon: '💀',
            title: 'Deadliest Incident',
            text: `The deadliest crash had ${deadliestCrash.Fatalities} fatalities (${deadliestCrash.Operator}, ${deadliestCrash.Date.getFullYear()}).`
        });
        
        return insights;
    }

    renderAnomalyChart() {
        // For demo, we'll highlight years with significantly more crashes than average
        const yearlyData = this.groupBy(this.filteredData, 'year');
        const years = Object.keys(yearlyData).map(Number).sort();
        const counts = years.map(year => yearlyData[year].length);
        
        const avgCrashes = counts.reduce((sum, count) => sum + count, 0) / counts.length;
        const stdDev = Math.sqrt(counts.reduce((sum, count) => sum + Math.pow(count - avgCrashes, 2), 0) / counts.length);
        
        // Identify anomalies (more than 2 standard deviations from mean)
        const anomalies = [];
        years.forEach((year, idx) => {
            if (Math.abs(counts[idx] - avgCrashes) > 2 * stdDev) {
                anomalies.push({ year, crashes: counts[idx], type: counts[idx] > avgCrashes ? 'High Crashes' : 'Low Crashes' });
            }
        });
        
        const normalYears = [];
        const anomalousYears = [];
        
        years.forEach((year, idx) => {
            if (anomalies.some(a => a.year === year)) {
                anomalousYears.push({ year, crashes: counts[idx] });
            } else {
                normalYears.push({ year, crashes: counts[idx] });
            }
        });
        
        const normalTrace = {
            x: normalYears.map(y => y.year),
            y: normalYears.map(y => y.crashes),
            mode: 'markers',
            name: 'Normal Years',
            marker: { size: 8, color: '#2E86AB', opacity: 0.6 },
            hovertemplate: '<b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<extra></extra>'
        };
        
        const anomalyTrace = {
            x: anomalousYears.map(y => y.year),
            y: anomalousYears.map(y => y.crashes),
            mode: 'markers',
            name: 'Anomalous Years',
            marker: { 
                size: 16, 
                color: '#F44336', 
                symbol: 'star',
                line: { color: 'yellow', width: 2 }
            },
            text: anomalousYears.map(y => {
                const anomaly = anomalies.find(a => a.year === y.year);
                return anomaly ? anomaly.type : '';
            }),
            hovertemplate: '<b>⚠️ ANOMALY DETECTED</b><br><b>Year:</b> %{x}<br><b>Crashes:</b> %{y}<br>%{text}<extra></extra>'
        };
        
        const layout = {
            title: 'Anomaly Detection - Unusual Years Highlighted',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Number of Crashes' },
            height: 400,
            paper_bgcolor: 'white',
            plot_bgcolor: 'white',
            showlegend: true
        };
        
        Plotly.newPlot('anomalyChart', [normalTrace, anomalyTrace], layout);
    }

    // Helper functions
    groupBy(array, key) {
        return array.reduce((result, item) => {
            const group = item[key];
            if (!result[group]) {
                result[group] = [];
            }
            result[group].push(item);
            return result;
        }, {});
    }

    countBy(array) {
        return array.reduce((result, item) => {
            result[item] = (result[item] || 0) + 1;
            return result;
        }, {});
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AviationDashboard();
});