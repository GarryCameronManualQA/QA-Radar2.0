import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib.robotparser

st.set_page_config(
    page_title="QA Radar – Trust Risk Discovery",
    layout="wide"
)

st.title("QA Radar – Trust Risk Discovery")
st.caption("Discovery-level intelligence to support senior QA judgment")

url = st.text_input(
    "Enter a primary domain (https://example.com)",
    placeholder="https://example.com"
)

def is_allowed_by_robots(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        return False

def fetch_page(url: str) -> str | None:
    try:
        headers = {
            "User-Agent": "QA-Radar/1.0 (Trust Risk Discovery)"
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def extract_signals(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    signals = {
        "title": soup.title.string.strip() if soup.title else None,
        "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
        "claims": [],
        "trust_links": []
    }

    text = soup.get_text(" ").lower()
    for phrase in ["guarantee", "clinically proven", "trusted by", "certified"]:
        if phrase in text:
            signals["claims"].append(phrase)

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(x in href for x in ["privacy", "terms", "about", "contact"]):
            signals["trust_links"].append(href)

    return signals

if st.button("Run Trust Discovery"):
    if not url:
        st.warning("Please enter a domain.")
    elif not is_allowed_by_robots(url):
        st.error("Robots.txt disallows scanning this domain.")
    else:
        with st.spinner("Running discovery…"):
            html = fetch_page(url)

        if not html:
            st.error("Failed to retrieve page content.")
        else:
            signals = extract_signals(html)

            st.subheader("Discovery Signals")

            st.json(signals)

            st.info(
                "This output is discovery-level only. "
                "No conclusions are drawn without senior human review."
            )
