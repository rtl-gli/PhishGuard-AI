# PhishGuard AI

**Explainable AI phishing URL detection**

PhishGuard AI is a project that leverages machine learning for cybersecurity by checking URLs to see if they have the characteristics of phishing.

 It encompasses the use of **feature engineering, machine learning, model evaluation, explainable prediction, automated testing, and FastAPI web applications.**

> **Important:** PhishGuard AI provides an estimate of the probability based on the features of the URL rather than providing a guarantee of safety or maliciousness.

---

## Features

- Analyse URLs for phishing characteristics
- Machine-learning classification using a Decision Tree
- Logistic Regression used as a baseline model
- Explainable predictions using the Decision Tree's decision path
- Risk classification: LOW, MEDIUM or HIGH
- Security indicators highlighting suspicious URL characteristics
- Technical analysis of extracted URL features
- FastAPI backend with a browser-based interface
- Automated feature-extraction tests using pytest
- Reproducible model evaluation

---

## How It Works

PhishGuard AI follows this pipeline:

```text
URL
 │
 ▼
Feature Extraction
 │
 ▼
16 Numerical URL Features
 │
 ▼
Machine Learning Model
 │
 ▼
Phishing Classification
 │
 ├── Risk Level
 ├── Estimated Phishing Likelihood
 ├── Security Indicators
 └── Explainable Decision Path
```

The system does not need to download or interact with the webpage itself. Instead, it analyses characteristics contained within the URL.

---

## Machine Learning

### Dataset

The model was trained using the **PhishTrap** URL dataset.

The dataset contains:

- **19,944 URLs**
- **9,972 legitimate URLs**
- **9,972 phishing URLs**
- **16 URL-based features**

The dataset is balanced between the two classes.

The raw dataset is intentionally excluded from the Git repository using `.gitignore`.

### Features

PhishGuard extracts the following features:

| Feature | Description |
|---|---|
| `url_length` | Length of the URL |
| `hyphen_count` | Number of hyphens |
| `digit_count` | Number of digits |
| `subdomain_count` | Number of subdomains |
| `trusted_tld` | Whether the TLD belongs to a selected trusted set |
| `protocol_exists` | Whether HTTP/HTTPS is present |
| `special_char_count` | Number of selected special characters |
| `entropy` | Shannon entropy of the URL |
| `path_depth` | Number of path levels |
| `domain_length` | Length of the hostname |
| `is_domain_ip` | Whether an IP address is used as the domain |
| `has_at_symbol` | Whether `@` appears in the URL |
| `has_double_slash_redirect` | Whether multiple `//` sequences occur |
| `tld_length` | Length of the TLD |
| `query_param_count` | Number of query parameters |
| `path_length` | Length of the URL path |

---

## Model Selection

Two machine-learning approaches were compared using the same train/test split.

### Logistic Regression

The Logistic Regression model was used as a baseline.

**Test accuracy: 82.88%**

### Decision Tree

The Decision Tree was tested at multiple maximum depths:

| Max Depth | Test Accuracy | Phishing Recall | Phishing F1 | False Negatives |
|---:|---:|---:|---:|---:|
| 3 | 80.32% | 69.66% | 77.97% | 605 |
| 5 | 83.35% | 78.13% | 82.43% | 436 |
| **8** | **85.11%** | **81.14%** | **84.49%** | **376** |
| 12 | 84.26% | 79.24% | 83.42% | 414 |
| Unlimited | 82.88% | 76.78% | 81.76% | 463 |

A maximum depth of **8** was selected for the deployed Decision Tree based on the evaluation performed during development.

The unrestricted tree also showed a larger difference between training and test performance, providing evidence of overfitting.

---

## Model Evaluation

The final Decision Tree was evaluated on **3,989 test samples**.

pytest
=================== test session starts ====================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rithg\Documents\PhishGuard AI
plugins: anyio-4.15.1
collected 10 items                                          

tests\test_api.py ..                                  [ 20%]
tests\test_features.py ........                       [100%]

===================== warnings summary =====================
.venv\Lib\site-packages\starlette\testclient.py:53
  C:\Users\rithg\Documents\PhishGuard AI\.venv\Lib\site-packages\starlette\testclient.py:53: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = Callable[[], AbstractContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============== 10 passed, 1 warning in 2.28s ===============
(.venv) PS C:\Users\rithg\Documents\PhishGuard AI> git add requirements.txt tests/test_api.py
>> git commit -m "Add API endpoint tests"
>> git push
[main afbaec7] Add API endpoint tests
 2 files changed, 33 insertions(+)
 create mode 100644 tests/test_api.py
Enumerating objects: 8, done.
Counting objects: 100% (8/8), done.
Delta compression using up to 16 threads
Compressing objects: 100% (5/5), done.
Writing objects: 100% (5/5), 681 bytes | 681.00 KiB/s, done.
Total 5 (delta 3), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (3/3), completed with 3 localobjects.
To https://github.com/rtl-gli/PhishGuard-AI.git
   353fb7a..afbaec7  main -> main
(.venv) PS C:\Users\rithg\Documents\PhishGuard AI> 


### Feature-Importance Visualisations

The project also generates:

- `feature_importance.png` — impurity-based Decision Tree importance
- `permutation_importance.png` — permutation importance measured using F1 score

### Results

- **Accuracy:** 85.11%
- **Phishing precision:** 88.13%
- **Phishing recall:** 81.14%
- **Phishing F1-score:** 84.49%
- **Phishing false negatives:** 376

Confusion matrix:

```text
                 Predicted
                 Legit  Phishing

Actual Legit      1777     218
Actual Phishing    376    1618
```

For a phishing detector, false negatives are particularly important because they represent phishing URLs that the model classified as legitimate.

---

## Explainable AI

Rather than only returning a classification, PhishGuard AI exposes the **Decision Tree's decision path**.

For example, the model may evaluate characteristics such as:

```text
Subdomains > threshold
        ↓
TLD trust value <= threshold
        ↓
URL classified as potentially phishing
```

The web interface displays these decisions so that the prediction is more transparent.

This is useful for understanding **why the model reached a particular prediction**, rather than treating the classifier as a black box.

---

## Web Application

PhishGuard AI includes a FastAPI web application with a welcoming home page,
a dedicated URL detector, and a privacy-friendly in-browser safety assistant.

Open `/` for the home page or `/detector` to go directly to the URL checker.

The interface allows a user to:

1. Paste a URL without opening it in the [URL detector](http://127.0.0.1:8000/detector)
2. View a calm, plain-language risk summary
3. See the estimated phishing likelihood and classification
4. Understand which URL signals stood out
5. Follow practical next steps for staying safe
6. Expand the technical explanation when more detail is useful
7. Review recent scans saved locally in the browser
8. Ask the built-in safety assistant common phishing questions

The interface is responsive and designed for non-technical users first. It does
not ask for an account, passwords, or personal information. Recent scan history
is stored only in the browser's local storage and is not sent to the API.

### API

The main analysis endpoint is:

```text
POST /api/analyze
```

Example request:

```json
{
    "url": "https://example.com"
}
```

The API returns the classification, estimated phishing likelihood, risk level, security indicators, extracted features and explainability information.

---

## Project Structure

```text
PhishGuard AI/
│
├── app/
│   ├── main.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── style.css
│       └── script.js
│
├── data/
│   ├── raw/
│   └── processed/
│
├── model/
│   └── phishing_model.pkl
│
├── src/
│   ├── features.py
│   ├── train.py
│   ├── predict.py
│   ├── evaluate.py
│   ├── explain.py
│   └── compare_models.py
│
├── tests/
│   └── test_features.py
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── requirements.txt
├── .gitignore
├── README.md
└── LICENSE
```

---

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/rtl-gli/PhishGuard-AI.git
cd PhishGuard-AI

python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Model

The prediction pipeline can be run from the terminal:

```powershell
python src\predict.py "https://example.com"
```

Model evaluation:

```powershell
python src\evaluate.py
```

Model comparison:

```powershell
python src\compare_models.py
```

Explainable prediction:

```powershell
python src\explain.py "https://example.com"
```

---

## Running the Web Application

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Testing

Automated tests are included using `pytest`.

Run:

```powershell
python -m pytest
```

The tests currently cover areas including:

- Entropy calculation
- URL feature extraction
- Protocol detection
- IP address detection
- `@` symbol detection
- Query parameter counting
- Legitimate URL feature values
- Suspicious URL feature values

---

## Limitations

PhishGuard AI is an educational and experimental cybersecurity project.

Important limitations include:

- The model only analyses URL characteristics.
- It does not inspect webpage content.
- It does not check live domain reputation.
- The dataset may not represent the distribution of URLs encountered in the real world.
- The dataset is balanced, whereas real-world phishing prevalence is not necessarily balanced.
- Model likelihood outputs should not be interpreted as guaranteed probabilities of maliciousness.
- The heuristic security indicators are separate from the machine-learning model's decision path.
- A legitimate-looking URL can still lead to malicious content.

These limitations mean the system should be considered an **additional security signal**, rather than a replacement for established security systems.

---

## Future Development

Potential future improvements include:

- [ ] GitHub Actions continuous integration
- [ ] Cross-validation
- [ ] Probability calibration
- [ ] Feature importance visualisation
- [ ] Improved model threshold analysis
- [ ] Larger and more diverse datasets
- [ ] Browser extension
- [ ] Email phishing analysis
- [ ] Domain reputation checking
- [ ] URL scanning history
- [ ] More advanced machine-learning models

---

## Technologies

**Python**

- pandas
- NumPy
- scikit-learn
- joblib
- tld
- pytest

**Web**

- FastAPI
- Uvicorn
- HTML
- CSS
- JavaScript

**Development**

- Git
- GitHub
- VS Code

---

## Author

Developed as a personal cybersecurity and machine-learning project to explore practical applications of AI in cybersecurity.

The project focuses on combining **cybersecurity, machine learning, software engineering and explainable AI** into a practical application.