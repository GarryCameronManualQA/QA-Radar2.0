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
# ================================
# Interpretation & Judgement Layer
# ================================

def categorise_signals(signals: dict) -> dict:
    """
    Light-weight categorisation to support senior human judgement.
    No automated conclusions are made.
    """
    categories = {
        "trust_indicators": [],
        "claims_detected": [],
        "missing_or_ambiguous": []
    }

    if signals.get("title"):
        categories["trust_indicators"].append("Page has a clear title")

    if signals.get("h1"):
        categories["trust_indicators"].append("Primary H1 present")

    if signals.get("trust_links"):
        categories["trust_indicators"].append(
            f"{len(signals['trust_links'])} trust-related links detected"
        )
    else:
        categories["missing_or_ambiguous"].append(
            "No obvious trust or policy links detected"
        )

    if signals.get("claims"):
        categories["claims_detected"].extend(signals["claims"])
    else:
        categories["claims_detected"].append(
            "No explicit claims detected at discovery level"
        )

    return categories


def judgement_prompts(categories: dict) -> list:
    """
    Questions intended for senior QA / risk judgement.
    """
    prompts = []

    if categories["trust_indicators"]:
        prompts.append(
            "Do the detected trust indicators meaningfully support user confidence?"
        )

    if categories["claims_detected"]:
        prompts.append(
            "Are any claims present that would require substantiation or testing?"
        )

    if categories["missing_or_ambiguous"]:
        prompts.append(
            "Are there omissions that increase user or regulatory risk?"
        )

    prompts.append(
        "Based on discovery alone, what areas require deeper inspection?"
    )

    return prompts


# ================================
# Enhanced UI Output
# ================================

if "signals" in locals() and signals:

    st.markdown("---")
    st.subheader("Discovery Interpretation")

    categories = categorise_signals(signals)

    with st.expander("Trust Indicators", expanded=True):
        for item in categories["trust_indicators"]:
            st.markdown(f"- {item}")

    with st.expander("Claims & Assertions"):
        for item in categories["claims_detected"]:
            st.markdown(f"- {item}")

    with st.expander("Missing / Ambiguous Signals"):
        for item in categories["missing_or_ambiguous"]:
            st.markdown(f"- {item}")

    st.markdown("---")
    st.subheader("Senior Judgement Prompts")

    for i, prompt in enumerate(judgement_prompts(categories), start=1):
        st.markdown(f"**{i}.** {prompt}")

    st.info(
        "This tool supports professional judgement. "
        "No automated conclusions or risk decisions are made."
    )
    # ================================
# Human-Centred Presentation Layer
# ================================

if "signals" in locals() and signals:

    st.markdown("---")
    st.header("🔍 Trust Discovery Summary")

    summary_points = []

    if signals.get("title"):
        summary_points.append("✔ Page has a clear title")

    if signals.get("h1"):
        summary_points.append("✔ Primary page heading detected")

    if signals.get("trust_links"):
        summary_points.append(f"✔ {len(signals['trust_links'])} trust / policy links present")

    if not summary_points:
        summary_points.append("⚠ No obvious trust indicators detected at discovery level")

    for point in summary_points:
        st.write(point)

    st.markdown("---")
    st.header("📄 Page Claims & Assertions")

    if signals.get("claims"):
        for claim in signals["claims"]:
            st.write(f"– {claim}")
    else:
        st.write("– No explicit claims detected at discovery level")

    st.markdown("---")
    st.header("⚠ Gaps & Ambiguities")

    gaps = []

    if not signals.get("trust_links"):
        gaps.append("No visible trust, contact, or policy links")

    if not signals.get("claims"):
        gaps.append("No explicit claims detected (may still exist deeper in content)")

    if gaps:
        for gap in gaps:
            st.write(f"– {gap}")
    else:
        st.write("– No immediate gaps detected at discovery level")

    st.markdown("---")
    st.header("🧠 Questions for Human Judgement")

    st.write("1. Do the detected trust indicators meaningfully support user confidence?")
    st.write("2. Are there claims that would require validation or testing?")
    st.write("3. Are there omissions that increase regulatory, user, or reputational risk?")
    st.write("4. What areas require deeper inspection beyond discovery?")

    st.info(
        "This tool provides discovery-level intelligence only. "
        "All conclusions require senior human judgement."
    )
    # ==========================================
# QA RADAR 2.0 — JUDGMENT & GOVERNANCE LAYER
# ==========================================

st.markdown("---")
st.header("⚙️ QA Radar — Judgment Configuration")

JUDGMENT_MODE = st.toggle(
    "Enable Judgment Mode (Senior Consultant)",
    value=True,
    help="Activates interpretive reasoning, evidence discipline, and scope control"
)

ARCHETYPE = st.selectbox(
    "Site Archetype",
    [
        "General / Informational",
        "SaaS / Claim-Heavy",
        "Regulated / Medical",
        "E-commerce / Transactional",
        "Legacy / Unstructured",
    ],
    help="Used to calibrate evidence thresholds and trust expectations"
)

st.markdown("---")

# ----------------------------
# Evidence Bar Enforcement
# ----------------------------

def passes_evidence_bar(signal):
    return any([
        signal.get("direct_observation"),
        signal.get("pattern_consistency"),
        signal.get("user_impact"),
        signal.get("professional_inference")
    ])

# ----------------------------
# Severity Calibration
# ----------------------------

def calibrate_severity(signal):
    if not signal.get("confidence"):
        return "Exploratory"

    if signal.get("user_impact") and signal.get("financial_or_trust_risk"):
        return "Critical"

    if signal.get("user_impact"):
        return "High"

    if signal.get("pattern_consistency"):
        return "Medium"

    return "Low"

# ----------------------------
# Trust Domain Assessment
# ----------------------------

def assess_trust_domains(signals):
    domains = {
        "Brand Credibility": [],
        "Transaction Safety": [],
        "Support Reliability": []
    }

    if signals.get("claims"):
        domains["Brand Credibility"].append("Claims detected — validate evidence parity")

    if signals.get("pricing") and not signals.get("product_state"):
        domains["Transaction Safety"].append("Pricing present without clear product readiness")

    if not signals.get("contact") and ARCHETYPE in ["Regulated / Medical", "SaaS / Claim-Heavy"]:
        domains["Support Reliability"].append("Support escalation unclear")

    return domains

# ----------------------------
# Judgment Output
# ----------------------------

if "signals" in locals() and signals and JUDGMENT_MODE:

    st.markdown("---")
    st.header("🧭 Trust Domain Analysis")

    trust_domains = assess_trust_domains(signals)

    for domain, findings in trust_domains.items():
        st.subheader(domain)

        if findings:
            for item in findings:
                st.write(f"– {item}")
        else:
            st.write("– No immediate trust-degrading signals detected at discovery level")

    st.markdown("---")
    st.header("⚖️ Evidence & Severity Review")

    reviewed_findings = []

    for key, value in signals.items():
        signal = {
            "direct_observation": bool(value),
            "pattern_consistency": False,
            "user_impact": key in ["claims", "pricing"],
            "financial_or_trust_risk": key in ["pricing", "claims"],
            "confidence": True
        }

        if passes_evidence_bar(signal):
            severity = calibrate_severity(signal)
            reviewed_findings.append((key, severity))

    if reviewed_findings:
        for finding, severity in reviewed_findings:
            st.write(f"**{finding.replace('_',' ').title()}** → Severity: **{severity}**")
    else:
        st.write("No findings met the evidence bar for escalation.")

    st.markdown("---")
    st.header("🧠 Senior Decision Prompts")

    st.write("1. Are detected signals proportionate to the site’s archetype and maturity?")
    st.write("2. Do any claims or pricing elements exceed what is currently provable?")
    st.write("3. Would a reasonable user feel misled, uncertain, or over-promised?")
    st.write("4. What requires manual verification before escalation?")

    st.info(
        "QA Radar operates as a senior decision support system. "
        "It identifies what deserves attention — not what must be fixed."
    )

# ----------------------------
# Daily Scanner Guardrail
# ----------------------------

st.markdown("---")
st.header("🛡️ Scanner Stability Notice")

st.write(
    "This scanner performs bounded discovery only. "
    "If discovery is limited due to architecture, indexing, or access controls, "
    "findings remain indicative by design."
)

st.caption(
    "False certainty is a higher risk than incomplete visibility."
)