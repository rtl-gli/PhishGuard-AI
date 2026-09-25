from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
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
    url = request.url.strip()
    if not url:
        raise HTTPException(
            status_code=422,
            detail="Please provide a non-empty URL.",
        )
    if len(url) > 2048:
        raise HTTPException(
            status_code=422,
            detail="The URL must be 2,048 characters or fewer.",
        )

    candidate = url if "://" in url else f"http://{url}"
    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid URL.",
        ) from error

    if not hostname or any(character.isspace() for character in hostname):
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid URL with a domain name.",
        )

    result = predict_url(url)

    explanation = explain_url(url)

    return {
    "url": result["url"],
    "risk_level": result["risk_level"],
    "phishing_probability": result["phishing_probability"],
    "prediction": result["prediction"],
    "indicators": result["indicators"],
    "features": result["features"],
    "explanations": explanation["explanations"],
}