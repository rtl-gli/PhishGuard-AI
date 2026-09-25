from src.predict import predict_url


test_urls = [
    "https://www.google.com",
    "https://www.microsoft.com",
    "https://www.wikipedia.org",
    "https://www.amazon.co.uk",
    "http://rrakuten.co.jp.lbtte.xyz",
    "http://mixtapegods.icu",
    "http://192.168.1.100/login",
    "http://example-login-account-security.com/verify",
]


print("PhishGuard AI - Manual URL Testing")
print("──────────────────────────────────")


for url in test_urls:

    result = predict_url(url)

    print(f"\nURL: {url}")
    print(f"Risk: {result['risk_level']}")
    print(
        f"Model risk score: "
        f"{result['phishing_probability']:.2%}"
    )

    if result["indicators"]:
        print("Indicators:")
        for indicator in result["indicators"]:
            print(f"  • {indicator}")
    else:
        print("Indicators: None detected")