class KalshiDataExplorer {
  constructor() {
    this.data = [];
    this.filteredData = [];
    this.currentSort = { column: null, direction: "asc" };
    this.init();
  }

  init() {
    this.bindEvents();
    this.setupDateDefaults();
    this.setupAnalysisTabs();
  }

  bindEvents() {
    // Form submission
    document.getElementById("apiForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.fetchData();
    });

    // Search functionality
    document.getElementById("searchInput").addEventListener("input", (e) => {
      this.filterData(e.target.value);
    });

    // Sort functionality
    document.getElementById("sortBtn").addEventListener("click", () => {
      const column = document.getElementById("sortColumn").value;
      if (column) {
        this.sortData(column);
      }
    });

    // Export CSV
    document.getElementById("exportCsv").addEventListener("click", () => {
      this.exportToCSV();
    });

    // Analysis functionality
    document.getElementById("analyzeBtn").addEventListener("click", () => {
      this.showAnalysis();
    });

    document.getElementById("closeAnalysis").addEventListener("click", () => {
      this.hideAnalysis();
    });

    document.getElementById("loadChart").addEventListener("click", () => {
      this.loadSelectedChart();
    });

    // Table header sorting
    document.addEventListener("click", (e) => {
      if (e.target.tagName === "TH") {
        const column = e.target.dataset.column;
        if (column) {
          this.sortData(column);
        }
      }
    });
  }

  setupAnalysisTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetTab = btn.dataset.tab;

        // Update active tab button
        tabBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        // Update active tab pane
        tabPanes.forEach((pane) => pane.classList.remove("active"));
        document.getElementById(`${targetTab}-tab`).classList.add("active");

        // Load content for the tab
        this.loadTabContent(targetTab);
      });
    });
  }

  setupDateDefaults() {
    // Set default date range (last 7 days)
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    document.getElementById("dateFrom").value =
      this.formatDateForInput(weekAgo);
    document.getElementById("dateTo").value = this.formatDateForInput(now);
  }

  formatDateForInput(date) {
    return date.toISOString().slice(0, 16);
  }

  async fetchData() {
    const formData = new FormData(document.getElementById("apiForm"));
    const params = Object.fromEntries(formData);

    // Convert dates to timestamps
    if (params.dateFrom) {
      params.min_ts = Math.floor(new Date(params.dateFrom).getTime() / 1000);
    }
    if (params.dateTo) {
      params.max_ts = Math.floor(new Date(params.dateTo).getTime() / 1000);
    }

    this.showLoading(true);

    try {
      // Real API call to Flask backend
      const response = await this.simulateApiCall(params);

      if (response.success) {
        this.data = response.data;
        this.filteredData = [...this.data];
        this.renderTable();
        this.updateResultsInfo();
      } else {
        this.showError(response.error);
      }
    } catch (error) {
      this.showError("Failed to fetch data: " + error.message);
    } finally {
      this.showLoading(false);
    }
  }

  // Real API call to Flask backend
  async simulateApiCall(params) {
    try {
      const response = await fetch("/api/trades", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ticker: params.ticker,
          limit: parseInt(params.limit) || 100,
          min_ts: params.min_ts,
          max_ts: params.max_ts,
          fetchAll: params.fetchAll === "on",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("API call failed:", error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  renderTable() {
    const tableHeader = document.getElementById("tableHeader");
    const tableBody = document.getElementById("tableBody");

    if (this.filteredData.length === 0) {
      tableHeader.innerHTML = "<th>No data available</th>";
      tableBody.innerHTML = "";
      return;
    }

    // Generate headers from first data item
    const headers = Object.keys(this.filteredData[0]);
    tableHeader.innerHTML = headers
      .map(
        (header) =>
          `<th data-column="${header}">${this.formatHeader(header)}</th>`
      )
      .join("");

    // Generate table rows
    tableBody.innerHTML = this.filteredData
      .map(
        (row) =>
          `<tr>${headers
            .map(
              (header) =>
                `<td class="${this.getCellClass(header)}">${this.formatCell(
                  row[header],
                  header
                )}</td>`
            )
            .join("")}</tr>`
      )
      .join("");
  }

  formatHeader(header) {
    return header
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  formatCell(value, column) {
    if (column === "timestamp") {
      return new Date(value).toLocaleString();
    }
    if (column === "price") {
      return `$${parseFloat(value).toFixed(2)}`;
    }
    if (column === "side") {
      return `<span class="side-${value}">${value.toUpperCase()}</span>`;
    }
    if (column === "created_at") {
      return new Date(value).toLocaleString();
    }
    return value;
  }

  getCellClass(column) {
    const classes = {
      timestamp: "timestamp",
      price: "price",
      quantity: "quantity",
      side: "side",
    };
    return classes[column] || "";
  }

  filterData(searchTerm) {
    if (!searchTerm) {
      this.filteredData = [...this.data];
    } else {
      const term = searchTerm.toLowerCase();
      this.filteredData = this.data.filter((row) =>
        Object.values(row).some((value) =>
          String(value).toLowerCase().includes(term)
        )
      );
    }
    this.renderTable();
    this.updateResultsInfo();
  }

  sortData(column) {
    const direction =
      this.currentSort.column === column && this.currentSort.direction === "asc"
        ? "desc"
        : "asc";
    this.currentSort = { column, direction };

    this.filteredData.sort((a, b) => {
      let aVal = a[column];
      let bVal = b[column];

      // Handle numeric values
      if (column === "price" || column === "quantity") {
        aVal = parseFloat(aVal);
        bVal = parseFloat(bVal);
      }
      // Handle timestamps
      else if (column === "timestamp" || column === "created_at") {
        aVal = new Date(aVal).getTime();
        bVal = new Date(bVal).getTime();
      }
      // Handle strings
      else {
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
      }

      if (aVal < bVal) return direction === "asc" ? -1 : 1;
      if (aVal > bVal) return direction === "asc" ? 1 : -1;
      return 0;
    });

    this.renderTable();
  }

  updateResultsInfo() {
    const countElement = document.getElementById("resultCount");
    const timeElement = document.getElementById("resultTime");

    countElement.textContent = `${this.filteredData.length} records`;
    timeElement.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
  }

  exportToCSV() {
    if (this.filteredData.length === 0) {
      alert("No data to export");
      return;
    }

    const headers = Object.keys(this.filteredData[0]);
    const csvContent = [
      headers.join(","),
      ...this.filteredData.map((row) =>
        headers
          .map((header) => {
            const value = row[header];
            // Escape commas and quotes in CSV
            return `"${String(value).replace(/"/g, '""')}"`;
          })
          .join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `kalshi_trades_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  showLoading(show) {
    const loading = document.getElementById("loading");
    const fetchBtn = document.getElementById("fetchBtn");

    if (show) {
      loading.style.display = "block";
      fetchBtn.disabled = true;
      fetchBtn.textContent = "Fetching...";
    } else {
      loading.style.display = "none";
      fetchBtn.disabled = false;
      fetchBtn.textContent = "Fetch Data";
    }
  }

  showError(message) {
    alert("Error: " + message);
  }

  // Analysis Methods
  showAnalysis() {
    if (this.data.length === 0) {
      alert("Please fetch data first before analyzing");
      return;
    }
    document.getElementById("analysisSection").style.display = "block";
    this.loadTabContent("stats"); // Load default tab
  }

  hideAnalysis() {
    document.getElementById("analysisSection").style.display = "none";
  }

  async loadTabContent(tabName) {
    switch (tabName) {
      case "stats":
        await this.loadStatistics();
        break;
      case "metrics":
        await this.loadMetrics();
        break;
      case "charts":
        this.showChartPlaceholder();
        break;
      case "all":
        await this.loadAllAnalysis();
        break;
    }
  }

  async loadStatistics() {
    try {
      const response = await fetch("/api/analysis/stats");
      const result = await response.json();

      if (result.success) {
        this.displayStatistics(result.data);
      } else {
        this.showError(result.error);
      }
    } catch (error) {
      this.showError("Failed to load statistics: " + error.message);
    }
  }

  async loadMetrics() {
    try {
      const response = await fetch("/api/analysis/metrics");
      const result = await response.json();

      if (result.success) {
        this.displayMetrics(result.data);
      } else {
        this.showError(result.error);
      }
    } catch (error) {
      this.showError("Failed to load metrics: " + error.message);
    }
  }

  async loadSelectedChart() {
    const chartType = document.getElementById("chartSelect").value;
    const chartDisplay = document.getElementById("chartDisplay");

    chartDisplay.innerHTML =
      "<div class='loading'><div class='spinner'></div><p>Generating chart...</p></div>";

    try {
      const response = await fetch(`/api/analysis/chart/${chartType}`);
      const result = await response.json();

      if (result.success) {
        chartDisplay.innerHTML = `<img src="data:image/png;base64,${result.data.image_data}" alt="${chartType} chart">`;
      } else {
        chartDisplay.innerHTML = `<div class="placeholder">Error: ${result.error}</div>`;
      }
    } catch (error) {
      chartDisplay.innerHTML = `<div class="placeholder">Failed to load chart: ${error.message}</div>`;
    }
  }

  async loadAllAnalysis() {
    const container = document.getElementById("allAnalysisContent");
    const loading = document.getElementById("analysisLoading");

    loading.style.display = "block";
    container.innerHTML = "";

    try {
      const response = await fetch("/api/analysis/all");
      const result = await response.json();

      if (result.success) {
        this.displayAllAnalysis(result.data);
      } else {
        container.innerHTML = `<div class="placeholder">Error: ${result.error}</div>`;
      }
    } catch (error) {
      container.innerHTML = `<div class="placeholder">Failed to load analysis: ${error.message}</div>`;
    } finally {
      loading.style.display = "none";
    }
  }

  displayStatistics(stats) {
    const grid = document.getElementById("statsGrid");

    const statCards = [
      // Basic stats
      { title: "Total Trades", value: stats.total_trades, unit: "trades" },
      { title: "Unique Tickers", value: stats.unique_tickers, unit: "tickers" },

      // Yes Price stats
      {
        title: "Avg Yes Price",
        value: `$${stats.yes_price_stats?.mean?.toFixed(2) || "N/A"}`,
        unit: "",
      },
      {
        title: "Yes Price Range",
        value: `$${stats.yes_price_stats?.min?.toFixed(2) || "N/A"} - $${
          stats.yes_price_stats?.max?.toFixed(2) || "N/A"
        }`,
        unit: "",
      },
      {
        title: "Yes Price Volatility",
        value: stats.yes_price_stats?.std?.toFixed(4) || "N/A",
        unit: "",
      },

      // No Price stats
      {
        title: "Avg No Price",
        value: `$${stats.no_price_stats?.mean?.toFixed(2) || "N/A"}`,
        unit: "",
      },
      {
        title: "No Price Range",
        value: `$${stats.no_price_stats?.min?.toFixed(2) || "N/A"} - $${
          stats.no_price_stats?.max?.toFixed(2) || "N/A"
        }`,
        unit: "",
      },
      {
        title: "No Price Volatility",
        value: stats.no_price_stats?.std?.toFixed(4) || "N/A",
        unit: "",
      },

      // Spread stats
      {
        title: "Avg Spread",
        value: `$${stats.spread_stats?.mean?.toFixed(2) || "N/A"}`,
        unit: "",
      },
      {
        title: "Spread Range",
        value: `$${stats.spread_stats?.min?.toFixed(2) || "N/A"} - $${
          stats.spread_stats?.max?.toFixed(2) || "N/A"
        }`,
        unit: "",
      },
      {
        title: "Spread Volatility",
        value: stats.spread_stats?.std?.toFixed(4) || "N/A",
        unit: "",
      },

      // Taker side distribution
      {
        title: "Yes Trades",
        value: stats.taker_side_distribution?.yes || 0,
        unit: "trades",
      },
      {
        title: "No Trades",
        value: stats.taker_side_distribution?.no || 0,
        unit: "trades",
      },

      // Date range
      {
        title: "Date Range",
        value:
          stats.date_range?.start && stats.date_range?.end
            ? `${new Date(
                stats.date_range.start
              ).toLocaleDateString()} to ${new Date(
                stats.date_range.end
              ).toLocaleDateString()}`
            : "N/A",
        unit: "",
      },
    ];

    grid.innerHTML = statCards
      .map(
        (card) => `
        <div class="stat-card">
            <h3>${card.title}</h3>
            <div class="value">${card.value}<span class="unit">${card.unit}</span></div>
        </div>
    `
      )
      .join("");
  }

  displayMetrics(metrics) {
    const grid = document.getElementById("metricsGrid");

    const metricCards = [
      {
        title: "Price Volatility",
        value: metrics.price_volatility?.toFixed(4),
        unit: "",
      },
      {
        title: "Price Skewness",
        value: metrics.price_skewness?.toFixed(4),
        unit: "",
      },
      {
        title: "Price Kurtosis",
        value: metrics.price_kurtosis?.toFixed(4),
        unit: "",
      },
      {
        title: "Average Trade Size",
        value: metrics.avg_trade_size?.toFixed(2),
        unit: "units",
      },
      {
        title: "Largest Trade",
        value: metrics.largest_trade?.toLocaleString(),
        unit: "units",
      },
      {
        title: "VWAP",
        value: `$${metrics.volume_weighted_avg_price?.toFixed(2)}`,
        unit: "",
      },
      {
        title: "Buy/Sell Ratio",
        value: metrics.buy_sell_ratio?.toFixed(2),
        unit: "",
      },
      {
        title: "Price Spread",
        value: `$${metrics.price_spread?.toFixed(2)}`,
        unit: "",
      },
      {
        title: "Trading Intensity",
        value: metrics.trading_intensity?.toFixed(2),
        unit: "trades/hour",
      },
    ];

    grid.innerHTML = metricCards
      .map(
        (card) => `
      <div class="metric-card">
        <h3>${card.title}</h3>
        <div class="value">${card.value || "N/A"}<span class="unit">${
          card.unit
        }</span></div>
      </div>
    `
      )
      .join("");
  }

  displayAllAnalysis(analysis) {
    const container = document.getElementById("allAnalysisContent");

    let html = `
      <div class="analysis-section">
        <h3>Basic Statistics</h3>
        <div class="stats-grid">
          ${Object.entries(analysis.basic_stats)
            .map(
              ([key, value]) => `
            <div class="stat-card">
              <h3>${key.replace(/_/g, " ").toUpperCase()}</h3>
              <div class="value">${
                typeof value === "number" ? value.toLocaleString() : value
              }</div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
      
      <div class="analysis-section">
        <h3>Advanced Metrics</h3>
        <div class="metrics-grid">
          ${Object.entries(analysis.advanced_metrics)
            .map(
              ([key, value]) => `
            <div class="metric-card">
              <h3>${key.replace(/_/g, " ").toUpperCase()}</h3>
              <div class="value">${
                typeof value === "number" ? value.toFixed(4) : value
              }</div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
      
      <div class="analysis-section">
        <h3>Charts</h3>
        <div class="charts-grid">
    `;

    const chartNames = {
      price_chart: "Price Movement",
      volume_chart: "Volume Analysis",
      side_analysis: "Buy/Sell Analysis",
      heatmap: "Trading Heatmap",
      price_distribution: "Price Distribution",
      time_series: "Time Series Analysis",
    };

    Object.entries(analysis.charts).forEach(([key, imageData]) => {
      if (imageData) {
        html += `
          <div class="chart-item">
            <h4>${chartNames[key] || key}</h4>
            <img src="data:image/png;base64,${imageData}" alt="${
          chartNames[key] || key
        }">
          </div>
        `;
      }
    });

    html += `
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  showChartPlaceholder() {
    const chartDisplay = document.getElementById("chartDisplay");
    chartDisplay.innerHTML =
      "<div class='placeholder'>Select a chart type and click 'Load Chart' to view</div>";
  }
}

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  new KalshiDataExplorer();
});
