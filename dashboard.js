// Aviation Crash Analytics Dashboard - Refactored for structure & readability

class AviationDashboard {

    /* ----------------------------- CORE ----------------------------- */

    constructor() {
        this.data = null;
        this.filteredData = null;
        this.currentTab = "overview";
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderDashboard();
    }

    /* ----------------------------- DATA LOADING ----------------------------- */

    async loadData() {
        try {
            const response = await fetch("data/crashes.json");
            const rawData = await response.json();

            this.data = rawData.map(crash => this.normalizeCrashData(crash));
            this.filteredData = [...this.data];

            this.updateHeaderStats();
        } catch (error) {
            console.error("Error loading data:", error);
            this.createSampleData();
        }
    }

    normalizeCrashData(crash) {
        return {
            ...crash,
            Date: new Date(crash.Year, 0, 1),
            Operator: crash.Location.split(",")[0] || "Unknown",
            Type: crash.Type || "Unknown",
            Aboard: crash.Fatalities > 0 ? crash.Fatalities + Math.floor(Math.random() * 50) : 50,
            Fatalities: crash.Fatalities || 0,
            Ground: Math.floor(Math.random() * 10),
            Summary: `Crash in ${crash.Location} in ${crash.Year}`,
            year: crash.Year,
            month: 1,
            month_name: "Jan",
            day_of_week: 0,
            day_name: "Monday",
            season: this.getSeason(crash.Year, 1),
            decade: Math.floor(crash.Year / 10) * 10,
            latitude: crash.Latitude,
            longitude: crash.Longitude
        };
    }

    createSampleData() {
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
                    Type: ["Commercial", "Cargo", "Military", "Private"][Math.floor(Math.random() * 4)],
                    Fatalities: fatalities,
                    Country: location.country,
                    Latitude: location.lat,
                    Longitude: location.lng,
                    Date: new Date(year, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                    Operator: `Airline_${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`,
                    Aboard: fatalities + Math.floor(Math.random() * 50),
                    Ground: Math.floor(Math.random() * 10),
                    Summary: `Crash in ${location.loc} in ${year}`,
                    year,
                    month: Math.floor(Math.random() * 12) + 1,
                    month_name: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][Math.floor(Math.random() * 12)],
                    day_of_week: Math.floor(Math.random() * 7),
                    day_name: ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][Math.floor(Math.random() * 7)],
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
        if (month >= 12 || month <= 2) return "Winter";
        if (month >= 3 && month <= 5) return "Spring";
        if (month >= 6 && month <= 8) return "Summer";
        return "Fall";
    }

    /* ----------------------------- EVENTS ----------------------------- */

    setupEventListeners() {
        document.querySelectorAll(".tab-button").forEach(button => {
            button.addEventListener("click", (e) => {
                const tabId = e.target.getAttribute("data-tab");
                this.switchTab(tabId);
            });
        });

        document.getElementById("yearFilter").addEventListener("input", (e) => {
            document.getElementById("yearFilterValue").textContent = e.target.value;
            this.applyFilters();
        });

        document.getElementById("regionFilter").addEventListener("change", () => this.applyFilters());
        document.getElementById("crashTypeFilter").addEventListener("change", () => this.applyFilters());
    }

    switchTab(tabId) {
        document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
        document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));

        document.getElementById(tabId).classList.add("active");
        document.querySelector(`[data-tab="${tabId}"]`).classList.add("active");

        this.currentTab = tabId;
        this.renderTabCharts(tabId);
    }

    /* ----------------------------- FILTERING ----------------------------- */

    applyFilters() {
        const year = parseInt(document.getElementById("yearFilter").value);
        const region = document.getElementById("regionFilter").value;
        const crashType = document.getElementById("crashTypeFilter").value;

        this.filteredData = this.data.filter(crash => {
            if (crash.year > year) return false;
            if (region !== "all" && crash.Country !== region) return false;
            if (crashType !== "all" && crash.Type !== crashType) return false;
            return true;
        });

        this.updateHeaderStats();
        this.renderTabCharts(this.currentTab);
    }

    /* ----------------------------- STATS ----------------------------- */

    updateHeaderStats() {
        const totalRecords = this.filteredData.length;
        const totalFatalities = this.filteredData.reduce((s, c) => s + c.Fatalities, 0);
        const years = this.filteredData.map(c => c.year);
        const yearRange = years.length ? `${Math.min(...years)}-${Math.max(...years)}` : "1908-2022";
        const airlines = new Set(this.filteredData.map(c => c.Operator)).size;

        document.getElementById("totalRecords").textContent = totalRecords.toLocaleString();
        document.getElementById("totalFatalities").textContent = totalFatalities.toLocaleString();
        document.getElementById("yearRange").textContent = yearRange;
        document.getElementById("airlineCount").textContent = airlines;
    }

    /* ----------------------------- RENDER FLOW ----------------------------- */

    renderDashboard() {
        this.renderOverviewCharts();
        this.renderGlobeMap();
    }

    renderTabCharts(tabId) {
        const map = {
            overview: () => this.renderOverviewCharts(),
            globe: () => this.renderGlobeMap(),
            trends: () => {
                this.renderMonthlyPatternChart();
                this.renderSeasonalChart();
                this.renderDayOfWeekChart();
                this.renderDecadeChart();
            },
            analysis: () => {
                this.renderCrashReasonsChart();
                this.renderCorrelationHeatmap();
                this.renderAircraftTypeChart();
                this.renderSurvivalRateChart();
            },
            costs: () => {
                this.renderCostBreakdownChart();
                this.renderRiskAnalysisChart();
                this.renderSafetyRankingsChart();
                this.renderPredictiveTrendChart();
            },
            insights: () => {
                this.renderAIInsights();
                this.renderAnomalyChart();
            }
        };

        map[tabId]?.();
    }

    /* ----------------------------- HELPERS ----------------------------- */

    groupBy(array, key) {
        return array.reduce((result, item) => {
            (result[item[key]] ||= []).push(item);
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

/* ----------------------------- INIT ----------------------------- */

document.addEventListener("DOMContentLoaded", () => {
    new AviationDashboard();
});
