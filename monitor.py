import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

KEYWORDS = [
    "nonprofit", "non-profit", "ngo",
    "501(c)(3)", "tax-exempt", "charity", "foundation"
]

# Focus on news/press pages instead of homepages
COMMITTEE_NEWS_URLS = [
    "https://energycommerce.house.gov/news/",
    "https://financialservices.house.gov/news/",
    "https://www.judiciary.senate.gov/press-releases"
]

def get_article_links(url):
    links = []

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            # Must be a full link
            if not href.startswith("http"):
                continue

            href_lower = href.lower()

            # Skip generic section/index pages
            if any(x in href_lower for x in [
                "/press-releases",
                "/newsroom",
                "/news/",
                "/press/"
            ]):
                continue

            # Keep likely article links (more specific patterns)
            if any(x in href_lower for x in [
                "202",  # year-based URLs
                "-release",
                "-statement",
                "-announces",
                "-introduces"
            ]):
                links.append(href)

    except Exception as e:
        print(f"Error reading {url}: {e}")

    return list(set(links))[:10]  # remove duplicates



def check_articles(links):
    matches = []

    for link in links:
        try:
            r = requests.get(link, timeout=10)
            text = r.text.lower()

            for kw in KEYWORDS:
                if kw in text:
                    matches.append(f"{link} → contains '{kw}'")
                    break

        except Exception as e:
            print(f"Error checking {link}: {e}")

    return matches


def send_email(results):
    if not results:
        return

    msg = MIMEText("\n\n".join(results))
    msg["Subject"] = "Congressional Committee NGO Alert"
    msg["From"] = EMAIL_USER
    msg["To"] = "lliu@icnl.org"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)


if __name__ == "__main__":
    all_links = []

    for url in COMMITTEE_NEWS_URLS:
        all_links.extend(get_article_links(url))

    results = check_articles(all_links)
    send_email(results)
