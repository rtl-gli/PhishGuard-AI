const urlInput = document.getElementById("urlInput");
const scanForm = document.getElementById("scanForm");
const analyseButton = document.getElementById("analyseButton");
const newScanButton = document.getElementById("newScanButton");
const results = document.getElementById("results");
const riskCard = document.getElementById("riskCard");
const riskLevel = document.getElementById("riskLevel");
const probability = document.getElementById("probability");
const riskProgress = document.getElementById("riskProgress");
const classification = document.getElementById("classification");
const indicators = document.getElementById("indicators");
const features = document.getElementById("features");
const decisions = document.getElementById("decisions");
const errorMessage = document.getElementById("errorMessage");
const historySection = document.getElementById("historySection");
const historyList = document.getElementById("historyList");
const clearHistoryButton = document.getElementById("clearHistoryButton");
const featureLabels = {
    url_length: "URL length", hyphen_count: "Hyphens", digit_count: "Digits",
    subdomain_count: "Subdomains", trusted_tld: "Trusted TLD",
    special_char_count: "Special characters", entropy: "URL entropy", path_depth: "Path depth",
    protocol_exists: "Connection security",
    domain_length: "Domain length", is_domain_ip: "IP address domain", has_at_symbol: "@ symbol",
    has_double_slash_redirect: "Double-slash redirect", tld_length: "TLD length",
    query_param_count: "Query parameters", path_length: "Path length"
};
const HISTORY_KEY = "phishguard-recent-scans";

scanForm.addEventListener("submit", (event) => { event.preventDefault(); analyseURL(); });
newScanButton.addEventListener("click", () => { results.classList.add("hidden"); urlInput.focus(); window.scrollTo({ top: 0, behavior: "smooth" }); });
clearHistoryButton.addEventListener("click", () => { localStorage.removeItem(HISTORY_KEY); renderHistory(); });

async function analyseURL() {
    const url = urlInput.value.trim();
    errorMessage.textContent = "";
    if (!url) { errorMessage.textContent = "Paste a link first so we can check it."; urlInput.focus(); return; }
    analyseButton.disabled = true;
    analyseButton.querySelector("span").textContent = "Checking…";
    try {
        const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url }) });
        if (!response.ok) throw new Error("Unable to analyse URL.");
        const data = await response.json();
        displayResults(data);
        saveHistory(data);
    } catch (error) {
        errorMessage.textContent = "We couldn’t check that link. Please try again.";
        console.error(error);
    } finally {
        analyseButton.disabled = false;
        analyseButton.querySelector("span").textContent = "Analyse link";
    }
}

function displayResults(data) {
    results.classList.remove("hidden");
    const percentage = Math.round(data.phishing_probability * 100);
    const level = data.risk_level.toLowerCase();
    riskCard.className = `risk-card ${level}`;
    riskLevel.textContent = data.risk_level;
    probability.textContent = `${percentage}%`;
    riskProgress.style.width = `${percentage}%`;
    document.querySelector(".risk-bar").setAttribute("aria-valuenow", percentage);
    classification.textContent = data.prediction === 1 ? "Potentially phishing" : "Likely legitimate";
    document.querySelector(".risk-icon").textContent = data.prediction === 1 ? "!" : "✓";
    renderIndicators(data.indicators);
    renderDecisions(data.decisions);
    renderFeatures(data.features, data.url);
    results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderIndicators(items) {
    indicators.innerHTML = "";
    const list = items.length ? items : ["No obvious suspicious URL characteristics detected."];
    list.forEach((item) => {
        const row = document.createElement("li");
        row.textContent = item;
        indicators.appendChild(row);
    });
}

function renderDecisions(items) {
    decisions.innerHTML = "";
    if (!items || !items.length) { decisions.textContent = "No decision-path information was returned."; return; }
    items.forEach((decision, index) => {
        const row = document.createElement("div");
        row.className = "decision-row";
        const number = document.createElement("span");
        number.className = "decision-number";
        number.textContent = index + 1;
        const content = document.createElement("div");
        content.className = "decision-content";
        const name = document.createElement("strong");
        name.textContent = featureLabels[decision.feature] || decision.feature;
        const explanation = document.createElement("span");
        explanation.textContent = `Value ${decision.value} ${decision.direction} threshold ${Number(decision.threshold).toFixed(3)}`;
        content.append(name, explanation);
        row.append(number, content);
        decisions.appendChild(row);
    });
}

function formatFeatureValue(key, value, url) {
    if (key === "protocol_exists") {
        return /^https:\/\//i.test(url) ? "HTTPS detected" : "No HTTPS";
    }
    if (key === "trusted_tld") return value ? "Recognised" : "Unrecognised";
    if (key === "is_domain_ip") return value ? "IP address used" : "Domain name used";
    if (key === "has_at_symbol") return value ? "Present" : "Not present";
    if (key === "has_double_slash_redirect") return value ? "Possible redirect" : "Not detected";
    return value;
}

function renderFeatures(featureData, url) {
    features.innerHTML = "";
    Object.entries(featureData).forEach(([key, value]) => {
        const row = document.createElement("div");
        row.className = "feature-row";
        const label = document.createElement("span");
        label.textContent = featureLabels[key] || key;
        const valueElement = document.createElement("strong");
        valueElement.textContent = formatFeatureValue(key, value, url);
        row.append(label, valueElement);
        features.appendChild(row);
    });
}

function saveHistory(data) {
    const history = getHistory().filter((item) => item.url !== data.url);
    history.unshift({ url: data.url, risk_level: data.risk_level });
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 4)));
    renderHistory();
}

function getHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
    catch (error) { console.warn("Could not read scan history.", error); return []; }
}

function renderHistory() {
    const history = getHistory();
    historySection.classList.toggle("hidden", !history.length);
    historyList.innerHTML = "";
    history.forEach((item) => {
        const row = document.createElement("div");
        row.className = "history-list-item";
        const url = document.createElement("span");
        url.className = "history-url";
        url.title = item.url;
        url.textContent = item.url;
        const risk = document.createElement("span");
        risk.className = `history-risk ${item.risk_level.toLowerCase()}`;
        risk.textContent = item.risk_level;
        row.append(url, risk);
        historyList.appendChild(row);
    });
}

renderHistory();
