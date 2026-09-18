const urlInput = document.getElementById("urlInput");
const analyseButton = document.getElementById("analyseButton");

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


analyseButton.addEventListener("click", analyseURL);


urlInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        analyseURL();
    }
});


async function analyseURL() {

    const url = urlInput.value.trim();

    errorMessage.textContent = "";

    if (!url) {
        errorMessage.textContent = "Please enter a URL.";
        return;
    }


    analyseButton.disabled = true;
    analyseButton.textContent = "Analysing...";


    try {

        const response = await fetch("/api/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url: url
            })

        });


        if (!response.ok) {
            throw new Error("Unable to analyse URL.");
        }


        const data = await response.json();

        displayResults(data);


    } catch (error) {

        errorMessage.textContent =
            "An error occurred while analysing the URL.";

        console.error(error);

    } finally {

        analyseButton.disabled = false;
        analyseButton.textContent = "Analyse URL";

    }
}


function displayResults(data) {

    results.classList.remove("hidden");


    const percentage =
        (data.phishing_probability * 100).toFixed(1);


    riskLevel.textContent = data.risk_level;

    probability.textContent = `${percentage}%`;

    riskProgress.style.width = `${percentage}%`;


    if (data.prediction === 1) {

        classification.textContent =
            "Potentially phishing";

    } else {

        classification.textContent =
            "Likely legitimate";

    }


    riskCard.className = "risk-card";

    riskCard.classList.add(
        data.risk_level.toLowerCase()
    );


    indicators.innerHTML = "";


    if (data.indicators.length === 0) {

        const item = document.createElement("li");

        item.textContent =
            "No obvious suspicious URL characteristics detected";

        indicators.appendChild(item);

    } else {

        data.indicators.forEach(function(indicator) {

            const item = document.createElement("li");

            item.textContent = indicator;

            indicators.appendChild(item);

        });

    }


    const featureLabels = {

        url_length: "URL length",
        hyphen_count: "Hyphens",
        digit_count: "Digits",
        subdomain_count: "Subdomains",
        trusted_tld: "Trusted TLD",
        protocol_exists: "Protocol",
        special_char_count: "Special characters",
        entropy: "URL entropy",
        path_depth: "Path depth",
        domain_length: "Domain length",
        is_domain_ip: "IP address domain",
        has_at_symbol: "@ symbol",
        has_double_slash_redirect: "Double-slash redirect",
        tld_length: "TLD length",
        query_param_count: "Query parameters",
        path_length: "Path length"

    };


    decisions.innerHTML = "";


    if (!data.decisions || data.decisions.length === 0) {

        const message = document.createElement("p");

        message.textContent =
            "No decision-path information was returned.";

        decisions.appendChild(message);

    } else {

        data.decisions.forEach(function(decision, index) {

            const row = document.createElement("div");

            row.className = "decision-row";


            const number = document.createElement("span");

            number.className = "decision-number";

            number.textContent = index + 1;


            const content = document.createElement("div");

            content.className = "decision-content";


            const name = document.createElement("strong");

            name.textContent =
                featureLabels[decision.feature]
                || decision.feature;


            const explanation = document.createElement("span");

            explanation.textContent =
                `Value ${decision.value} `
                + `${decision.direction} `
                + `threshold ${decision.threshold.toFixed(3)}`;


            content.appendChild(name);

            content.appendChild(explanation);


            row.appendChild(number);

            row.appendChild(content);


            decisions.appendChild(row);

        });

    }


    features.innerHTML = "";


    Object.entries(data.features).forEach(
        function([key, value]) {

            const row = document.createElement("div");

            row.className = "feature-row";


            const name = document.createElement("span");

            name.textContent =
                featureLabels[key] || key;


            const valueElement = document.createElement("strong");

            valueElement.textContent = value;


            row.appendChild(name);

            row.appendChild(valueElement);


            features.appendChild(row);

        }
    );

}


    const featureLabels = {

        url_length: "URL length",
        hyphen_count: "Hyphens",
        digit_count: "Digits",
        subdomain_count: "Subdomains",
        trusted_tld: "Trusted TLD",
        protocol_exists: "Protocol",
        special_char_count: "Special characters",
        entropy: "URL entropy",
        path_depth: "Path depth",
        domain_length: "Domain length",
        is_domain_ip: "IP address domain",
        has_at_symbol: "@ symbol",
        has_double_slash_redirect: "Double-slash redirect",
        tld_length: "TLD length",
        query_param_count: "Query parameters",
        path_length: "Path length"

    };


    Object.entries(data.features).forEach(
        function([key, value]) {

            const row = document.createElement("div");

            row.className = "feature-row";

            row.innerHTML = `
                <span>${featureLabels[key] || key}</span>
                <strong>${value}</strong>
            `;

            features.appendChild(row);

        }
    );

