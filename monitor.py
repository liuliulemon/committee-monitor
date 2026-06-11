import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

KEYWORDS = [
    "nonprofit", "non-profit", "ngo",
    "501(c)(3)", "tax-exempt", "charity", "foundation"
]

COMMITTEE_URLS = [
    "https://www.judiciary.senate.gov/",
    "https://energycommerce.house.gov/",
    "https://financialservices.house.gov/",
]

def find_matches():
    matches = []

    for url in COMMITTEE_URLS:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text().lower()

            for kw in KEYWORDS:
                if kw in text:
                    matches.append(f"{url} mentions '{kw}'")
                    break
        except Exception as e:
            print(f"Error with {url}: {e}")

    return matches

def send_email(results):
    if not results:
        return

    msg = MIMEText("\n".join(results))
    msg["Subject"] = "Congressional Committee NGO Alert"
    msg["From"] = "YOUR_EMAIL@gmail.com"
    msg["To"] = "lliu@icnl.org"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("YOUR_EMAIL@gmail.com", "YOUR_APP_PASSWORD")
        server.send_message(msg)

if __name__ == "__main__":
    results = find_matches()
    send_email(results)
