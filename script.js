class KalshiDataExplorer {
  constructor() {
    this.data = [];
    this.filteredData = [];
    this.currentSort = { column: null, direction: "asc" };
    this.selectedCategory = null;
    this.selectedSeries = null;
    this.init();
  }

  init() {
    this.bindEvents();
    this.setupDateDefaults();
    this.setupAnalysisTabs();
    this.loadCategories(); // Load categories for series browser on page load
  }

  bindEvents() {
    // Event ticker dropdown change
    document.getElementById("eventTicker").addEventListener("change", (e) => {
      this.onEventTickerChange(e.target.value);
    });

    // Form submission
    document.getElementById("apiForm").addEventListener("submit", (e) => {
      e.preventDefault();
      this.fetchData();
    });

    // Search functionality
    document.getElementById("searchInput").addEventListener("input", (e) => {
      this.filterData(e.target.value);
      this.updateClearButton(e.target.value);
    });

    // Clear search button
    document.getElementById("clearSearch").addEventListener("click", () => {
      this.clearSearch();
    });

    // Clear search when user clicks on the search box and it's not empty
    document.getElementById("searchInput").addEventListener("click", (e) => {
      if (e.target.value && e.target.value.trim() !== "") {
        // Show a small tooltip or hint that they can clear by clicking again
        e.target.title = "Click again to clear search";
      }
    });

    // Clear search on double click
    document.getElementById("searchInput").addEventListener("dblclick", (e) => {
      this.clearSearch();
    });

    // Export functionality
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

    // Back button functionality
    document
      .getElementById("backToCategories")
      .addEventListener("click", () => {
        const seriesList = document.getElementById("seriesList");
        const tickersList = document.getElementById("tickersList");
        const categoriesList = document.getElementById("categoriesList");

        seriesList.style.display = "none";
        tickersList.style.display = "none";
        categoriesList.style.display = "block";
        this.loadCategories();
      });

    document.getElementById("backToSeries").addEventListener("click", () => {
      const tickersList = document.getElementById("tickersList");
      const seriesList = document.getElementById("seriesList");

      tickersList.style.display = "none";
      seriesList.style.display = "block";
    });

    // Analysis tabs
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        // Remove active class from all tabs
        document
          .querySelectorAll(".tab-btn")
          .forEach((b) => b.classList.remove("active"));
        document
          .querySelectorAll(".tab-pane")
          .forEach((p) => p.classList.remove("active"));

        // Add active class to clicked tab
        btn.classList.add("active");
        const tabName = btn.getAttribute("data-tab");
        document.getElementById(`${tabName}-tab`).classList.add("active");

        // Load tab content
        this.loadTabContent(tabName);
      });
    });

    // Chart loading
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

    // Series row clicks (event delegation)
    document.addEventListener("click", (e) => {
      if (e.target.closest(".series-row")) {
        const row = e.target.closest(".series-row");
        const ticker = row.dataset.ticker;
        const title = row.dataset.title;
        if (ticker && title) {
          this.loadTickersForSeries(ticker, title);
        }
      }
    });

    // Ticker row clicks (event delegation)
    document.addEventListener("click", (e) => {
      if (e.target.closest(".ticker-row")) {
        const row = e.target.closest(".ticker-row");
        const ticker = row.querySelector(".ticker-name").textContent;
        if (ticker) {
          this.selectTickerForTrades(ticker);
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

    console.log("fetchData called with params:", params);

    // Validate that a ticker is selected
    if (!params.ticker || params.ticker.trim() === "") {
      console.log("Validation failed: no ticker selected");
      this.showError("Please select a ticker from the dropdown");
      return;
    }

    console.log("Validation passed, ticker:", params.ticker);

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
      const requestBody = {
        ticker: params.ticker,
        limit: 100, // Default limit since form field was removed
        fetchAll: params.fetchAll === "on",
      };

      // Only include date parameters if fetchAll is not selected
      if (!params.fetchAll || params.fetchAll !== "on") {
        if (params.min_ts) {
          requestBody.min_ts = params.min_ts;
        }
        if (params.max_ts) {
          requestBody.max_ts = params.max_ts;
        }
      }

      // Set limit to maximum when fetchAll is selected
      if (params.fetchAll === "on") {
        requestBody.limit = 1000; // Maximum limit for efficiency
      }

      console.log("API request body:", requestBody);

      const response = await fetch("/api/trades", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("API response:", result);
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

    // Define the preferred column order
    const preferredOrder = [
      "ticker",
      "count",
      "taker_side",
      "no_price",
      "yes_price",
      "created_at",
      "trade_id",
    ];

    // Get all available headers from the data
    const allHeaders = Object.keys(this.filteredData[0]);

    // Create ordered headers: preferred order first, then any remaining headers
    const orderedHeaders = [];

    // Add headers in preferred order (if they exist in the data)
    preferredOrder.forEach((header) => {
      if (allHeaders.includes(header)) {
        orderedHeaders.push(header);
      }
    });

    // Add any remaining headers that weren't in the preferred order
    allHeaders.forEach((header) => {
      if (!orderedHeaders.includes(header)) {
        orderedHeaders.push(header);
      }
    });

    // Generate table headers
    tableHeader.innerHTML = orderedHeaders
      .map(
        (header) =>
          `<th data-column="${header}">${this.formatHeader(header)}</th>`
      )
      .join("");

    // Generate table rows using the same order
    tableBody.innerHTML = this.filteredData
      .map(
        (row) =>
          `<tr>${orderedHeaders
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
    timeElement.textContent = `Last fetched: ${new Date().toLocaleTimeString()}`;
  }

  exportToCSV() {
    if (this.filteredData.length === 0) {
      alert("No data to export");
      return;
    }

    // Define the preferred column order (same as renderTable)
    const preferredOrder = [
      "ticker",
      "count",
      "taker_side",
      "no_price",
      "yes_price",
      "created_at",
      "trade_id",
    ];

    // Get all available headers from the data
    const allHeaders = Object.keys(this.filteredData[0]);

    // Create ordered headers: preferred order first, then any remaining headers
    const orderedHeaders = [];

    // Add headers in preferred order (if they exist in the data)
    preferredOrder.forEach((header) => {
      if (allHeaders.includes(header)) {
        orderedHeaders.push(header);
      }
    });

    // Add any remaining headers that weren't in the preferred order
    allHeaders.forEach((header) => {
      if (!orderedHeaders.includes(header)) {
        orderedHeaders.push(header);
      }
    });

    const csvContent = [
      orderedHeaders.join(","),
      ...this.filteredData.map((row) =>
        orderedHeaders
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

  updateClearButton(value) {
    const clearButton = document.getElementById("clearSearch");
    const searchInput = document.getElementById("searchInput");

    if (value && value.trim() !== "") {
      clearButton.classList.add("visible");
      searchInput.value = value; // Ensure the input value is set
    } else {
      clearButton.classList.remove("visible");
      searchInput.value = ""; // Clear the input value
      searchInput.title = ""; // Clear the tooltip
    }
  }

  clearSearch() {
    const searchInput = document.getElementById("searchInput");
    searchInput.value = "";
    this.filterData("");
    this.updateClearButton("");
  }

  async onEventTickerChange(eventTicker) {
    const tickerSelect = document.getElementById("ticker");

    if (!eventTicker) {
      // Reset ticker dropdown if no event selected
      tickerSelect.innerHTML = '<option value="">Select a ticker...</option>';
      tickerSelect.disabled = true;
      return;
    }

    try {
      const response = await fetch(
        `/api/markets/events/${encodeURIComponent(eventTicker)}/tickers`
      );
      const result = await response.json();

      if (result.success) {
        // Populate ticker dropdown
        tickerSelect.innerHTML = '<option value="">Select a ticker...</option>';
        result.data.tickers.forEach((ticker) => {
          const option = document.createElement("option");
          option.value = ticker;
          option.textContent = ticker;
          tickerSelect.appendChild(option);
        });

        // Enable ticker dropdown
        tickerSelect.disabled = false;

        console.log(
          `Loaded ${result.data.count} tickers for event: ${eventTicker}`
        );
      } else {
        this.showError(result.error);
      }
    } catch (error) {
      this.showError("Failed to load tickers: " + error.message);
    }
  }

  showMessage(message, type = "info") {
    // Create a temporary message element
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 10px 15px;
      border-radius: 5px;
      color: white;
      font-weight: bold;
      z-index: 1000;
      ${
        type === "success"
          ? "background-color: #4CAF50;"
          : "background-color: #2196F3;"
      }
    `;

    document.body.appendChild(messageDiv);

    // Remove after 3 seconds
    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.parentNode.removeChild(messageDiv);
      }
    }, 3000);
  }

  async loadCategories() {
    const categoriesList = document.getElementById("categoriesList");
    const seriesList = document.getElementById("seriesList");
    const seriesItems = document.getElementById("seriesItems");
    const seriesListTitle = document.getElementById("seriesListTitle");
    const backToCategories = document.getElementById("backToCategories");

    categoriesList.innerHTML = "<div>Loading categories...</div>";
    seriesList.style.display = "none";
    backToCategories.style.display = "none";

    try {
      const response = await fetch("/api/series/categories");
      const result = await response.json();
      if (result.success) {
        const categories = result.data;
        categoriesList.innerHTML = "";
        categories.forEach((cat) => {
          const btn = document.createElement("button");
          btn.className = "category-btn";
          btn.textContent = cat;
          btn.onclick = () => this.loadSeriesForCategory(cat);
          categoriesList.appendChild(btn);
        });
      } else {
        categoriesList.innerHTML = `<div class='error'>${result.error}</div>`;
      }
    } catch (error) {
      categoriesList.innerHTML = `<div class='error'>Failed to load categories: ${error.message}</div>`;
    }
  }

  async loadSeriesForCategory(category) {
    try {
      // Store the selected category
      this.selectedCategory = category;

      this.showMessage("Loading series...", "info");

      const response = await fetch(
        `/api/series/category/${encodeURIComponent(category)}`
      );
      const result = await response.json();

      if (result.success) {
        const seriesList = document.getElementById("seriesList");
        const seriesListTitle = document.getElementById("seriesListTitle");
        const seriesItems = document.getElementById("seriesItems");
        const categoriesList = document.getElementById("categoriesList");
        const backToCategories = document.getElementById("backToCategories");

        seriesListTitle.textContent = `Series in ${category}`;

        // Create search input and table structure
        let seriesHtml = `
          <div class="series-search-container">
            <input type="text" id="seriesSearchInput" placeholder="Search series by ticker, title, or tags..." class="series-search-input">
            <div class="series-search-info">
              <span id="seriesSearchCount">${result.data.length} series</span>
            </div>
          </div>
          <div class="series-table-container">
            <table class="series-table">
              <thead>
                <tr>
                  <th>Series Ticker</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Frequency</th>
                  <th>Tags</th>
                </tr>
              </thead>
              <tbody id="seriesTableBody">
        `;

        result.data.forEach((series) => {
          const ticker = series.ticker || "N/A";
          const title = series.title || "N/A";
          const seriesCategory = series.category || "N/A";
          const frequency = series.frequency || "N/A";
          const tags = series.tags ? series.tags.join(", ") : "N/A";

          seriesHtml += `
            <tr class="series-row" data-ticker="${ticker}" data-title="${title.replace(
            /"/g,
            "&quot;"
          )}" data-category="${seriesCategory}" data-frequency="${frequency}" data-tags="${tags.replace(
            /"/g,
            "&quot;"
          )}">
              <td class="series-ticker">${ticker}</td>
              <td class="series-title">${title}</td>
              <td class="series-category">${seriesCategory}</td>
              <td class="series-frequency">${frequency}</td>
              <td class="series-tags">${tags}</td>
            </tr>
          `;
        });

        seriesHtml += `
              </tbody>
            </table>
          </div>
        `;

        seriesItems.innerHTML = seriesHtml;

        // Add search functionality
        this.setupSeriesSearch(result.data);

        categoriesList.style.display = "none";
        seriesList.style.display = "block";
        backToCategories.style.display = "block";

        this.showMessage(
          `Found ${result.data.length} series in ${category}`,
          "success"
        );
      } else {
        this.showMessage(`Error loading series: ${result.error}`, "error");
      }
    } catch (error) {
      console.error("Error loading series:", error);
      this.showMessage("Failed to load series", "error");
    }
  }

  async loadTickersForSeries(seriesTicker, seriesTitle) {
    try {
      // Store the selected series
      this.selectedSeries = seriesTitle;

      this.showMessage("Loading tickers...", "info");

      const response = await fetch(`/api/series/${seriesTicker}/tickers`);
      const result = await response.json();

      if (result.success) {
        const tickersList = document.getElementById("tickersList");
        const tickersListTitle = document.getElementById("tickersListTitle");
        const tickerItems = document.getElementById("tickerItems");
        const seriesList = document.getElementById("seriesList");

        tickersListTitle.textContent = `Tickers for ${seriesTitle}`;

        // Create table structure for tickers with metadata
        let tickersHtml = `
          <div class="tickers-table-container">
            <table class="tickers-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Status</th>
                  <th>Volume</th>
                  <th>Title</th>
                  <th>Open Time</th>
                  <th>Close Time</th>
                </tr>
              </thead>
              <tbody>
        `;

        result.data.tickers.forEach((ticker) => {
          // Find the market data for this ticker
          const market = result.data.markets.find((m) => m.ticker === ticker);

          if (market) {
            const status = market.status || "Unknown";
            const volume = market.volume || 0;
            const title = market.title || "N/A";

            // Handle ISO string timestamps
            let closeTime = "N/A";
            let openTime = "N/A";

            if (market.close_time) {
              try {
                closeTime = new Date(market.close_time).toLocaleString();
              } catch (e) {
                closeTime = "N/A";
              }
            }

            if (market.open_time) {
              try {
                openTime = new Date(market.open_time).toLocaleString();
              } catch (e) {
                openTime = "N/A";
              }
            }

            tickersHtml += `
              <tr class="ticker-row" data-ticker="${ticker}">
                <td class="ticker-name">${ticker}</td>
                <td><span class="status-badge status-${status.toLowerCase()}">${status}</span></td>
                <td class="ticker-volume">${volume.toLocaleString()}</td>
                <td class="ticker-title">${title}</td>
                <td class="ticker-time">${openTime}</td>
                <td class="ticker-time">${closeTime}</td>
              </tr>
            `;
          } else {
            // Fallback if no market data available
            tickersHtml += `
              <tr class="ticker-row" data-ticker="${ticker}">
                <td class="ticker-name">${ticker}</td>
                <td><span class="status-badge status-unknown">Unknown</span></td>
                <td class="ticker-volume">N/A</td>
                <td class="ticker-title">N/A</td>
                <td class="ticker-time">N/A</td>
                <td class="ticker-time">N/A</td>
              </tr>
            `;
          }
        });

        tickersHtml += `
              </tbody>
            </table>
          </div>
        `;

        tickerItems.innerHTML = tickersHtml;

        // Store the tickers data for later use
        this.currentTickersData = result.data.markets;

        seriesList.style.display = "none";
        tickersList.style.display = "block";

        this.showMessage(
          `Found ${result.data.tickers.length} tickers for ${seriesTitle}`,
          "success"
        );
      } else {
        this.showMessage(`Error loading tickers: ${result.error}`, "error");
      }
    } catch (error) {
      console.error("Error loading tickers:", error);
      this.showMessage("Failed to load tickers", "error");
    }
  }

  selectTickerForTrades(ticker) {
    console.log("selectTickerForTrades called with:", ticker);

    // Extract event ticker from the ticker (e.g., "CORIVER-2024-T1075" -> "CORIVER-2024")
    const eventTicker = ticker.split("-").slice(0, -1).join("-");
    console.log("Extracted event ticker:", eventTicker);

    // Populate the event ticker field
    const eventTickerSelect = document.getElementById("eventTicker");
    eventTickerSelect.innerHTML = `<option value="${eventTicker}">${eventTicker}</option>`;
    eventTickerSelect.value = eventTicker;
    eventTickerSelect.disabled = false;
    console.log("Event ticker field populated:", eventTickerSelect.value);

    // Populate the ticker field in the trades form
    const tickerSelect = document.getElementById("ticker");
    tickerSelect.innerHTML = `<option value="${ticker}">${ticker}</option>`;
    tickerSelect.value = ticker;
    tickerSelect.disabled = false;
    console.log("Ticker field populated:", tickerSelect.value);

    // Fetch and display ticker metadata
    this.fetchTickerMetadata(ticker);

    // Scroll to the trades form
    document.getElementById("apiForm").scrollIntoView({ behavior: "smooth" });

    // Show a success message
    this.showMessage(
      `Selected ticker: ${ticker}. You can now fetch trades data.`,
      "success"
    );

    // Hide the tickers list and go back to categories
    const tickersList = document.getElementById("tickersList");
    const categoriesList = document.getElementById("categoriesList");
    tickersList.style.display = "none";
    categoriesList.style.display = "block";
    this.loadCategories();
  }

  async fetchTickerMetadata(ticker) {
    try {
      // Find the market data for this ticker from the current tickers data
      // We'll need to store this data when loading tickers
      if (this.currentTickersData) {
        const market = this.currentTickersData.find((m) => m.ticker === ticker);
        if (market) {
          this.displayTickerMetadata(market);
          return;
        }
      }

      // If we don't have the data, fetch it from the API
      const response = await fetch(
        `/api/series/${ticker.split("-").slice(0, -1).join("-")}/tickers`
      );
      const result = await response.json();

      if (result.success) {
        const market = result.data.markets.find((m) => m.ticker === ticker);
        if (market) {
          this.displayTickerMetadata(market);
        }
      }
    } catch (error) {
      console.error("Error fetching ticker metadata:", error);
    }
  }

  displayTickerMetadata(market) {
    const tickerInfoSection = document.getElementById("tickerInfoSection");
    const tickerCategory = document.getElementById("tickerCategory");
    const tickerSeries = document.getElementById("tickerSeries");
    const tickerStatus = document.getElementById("tickerStatus");
    const tickerVolume = document.getElementById("tickerVolume");
    const tickerTitle = document.getElementById("tickerTitle");
    const tickerOpenTime = document.getElementById("tickerOpenTime");
    const tickerCloseTime = document.getElementById("tickerCloseTime");

    // Show the section
    tickerInfoSection.style.display = "block";

    // Populate category and series data
    tickerCategory.textContent = this.selectedCategory || "N/A";
    tickerSeries.textContent = this.selectedSeries || "N/A";

    // Populate the market data
    const status = market.status || "Unknown";
    const volume = market.volume || 0;
    const title = market.title || "N/A";

    // Handle timestamps
    let openTime = "N/A";
    let closeTime = "N/A";

    if (market.open_time) {
      try {
        openTime = new Date(market.open_time).toLocaleString();
      } catch (e) {
        openTime = "N/A";
      }
    }

    if (market.close_time) {
      try {
        closeTime = new Date(market.close_time).toLocaleString();
      } catch (e) {
        closeTime = "N/A";
      }
    }

    // Update the display
    tickerStatus.textContent = status;
    tickerStatus.className = `info-value status-${status.toLowerCase()}`;
    tickerVolume.textContent = volume.toLocaleString();
    tickerTitle.textContent = title;
    tickerOpenTime.textContent = openTime;
    tickerCloseTime.textContent = closeTime;
  }

  setupSeriesSearch(seriesData) {
    const searchInput = document.getElementById("seriesSearchInput");
    const searchCount = document.getElementById("seriesSearchCount");
    const tableBody = document.getElementById("seriesTableBody");

    if (!searchInput) return;

    // Store original data for filtering
    this.currentSeriesData = seriesData;

    searchInput.addEventListener("input", (e) => {
      const searchTerm = e.target.value.toLowerCase().trim();
      this.filterSeriesTable(searchTerm, searchCount, tableBody);
    });

    // Clear search when input is cleared
    searchInput.addEventListener("keyup", (e) => {
      if (e.key === "Escape") {
        searchInput.value = "";
        this.filterSeriesTable("", searchCount, tableBody);
      }
    });
  }

  filterSeriesTable(searchTerm, searchCount, tableBody) {
    const rows = tableBody.querySelectorAll(".series-row");
    let visibleCount = 0;

    rows.forEach((row) => {
      const ticker = row.dataset.ticker.toLowerCase();
      const title = row.dataset.title.toLowerCase();
      const category = row.dataset.category.toLowerCase();
      const frequency = row.dataset.frequency.toLowerCase();
      const tags = row.dataset.tags.toLowerCase();

      // Check if any field contains the search term
      const matches =
        ticker.includes(searchTerm) ||
        title.includes(searchTerm) ||
        category.includes(searchTerm) ||
        frequency.includes(searchTerm) ||
        tags.includes(searchTerm);

      if (matches || !searchTerm) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    // Update the count display
    if (searchCount) {
      const totalCount = this.currentSeriesData.length;
      if (searchTerm) {
        searchCount.textContent = `${visibleCount} of ${totalCount} series`;
      } else {
        searchCount.textContent = `${totalCount} series`;
      }
    }
  }
}

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  new KalshiDataExplorer();
});
