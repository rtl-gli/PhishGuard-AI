from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.predict import predict_url
from src.explain import explain_url


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="PhishGuard AI",
    description="Explainable AI phishing URL detection",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


class URLRequest(BaseModel):
    url: str


def render_template(filename: str):
    html_file = BASE_DIR / "templates" / filename
    return html_file.read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def root():
    return render_template("index.html")


@app.get("/detector", response_class=HTMLResponse)
def detector():
    return render_template("index.html")


@app.post("/api/analyze")
def analyze_url(request: URLRequest):

    result = predict_url(request.url)

    explanation = explain_url(request.url)

    return {
    "url": result["url"],
    "risk_level": result["risk_level"],
    "phishing_probability": result["phishing_probability"],
    "prediction": result["prediction"],
    "indicators": result["indicators"],
    "features": result["features"],
    "explanations": explanation["explanations"],
}