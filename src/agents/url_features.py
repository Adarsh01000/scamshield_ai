import re
import math
from urllib.parse import urlparse
from typing import Dict, Any, List

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq", ".live",
    ".ru", ".work", ".icu", ".buzz", ".click", ".cn", ".fit", ".surf",
    ".rest", ".online", ".monster", ".cc"
}

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "account", "banking", "secure", "update", "signin",
    "confirm", "support", "wallet", "claim", "bonus", "gift", "free",
    "security", "authenticate", "billing", "service", "customer", "password",
    "recovery", "alert", "notification", "kyc", "otp", "validation"
]

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
    return round(entropy, 4)

def is_ip_address(host: str) -> bool:
    """Check if host is an IPv4 address."""
    # Strip port if present
    h = host.split(':')[0]
    pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return bool(re.match(pattern, h))

def extract_url_features(url: str) -> Dict[str, Any]:
    """
    Extract lexical, structural, and statistical features from a URL.
    Returns a dictionary of numerical and categorical features.
    """
    raw_url = url.strip()
    if not raw_url.startswith(("http://", "https://")):
        # If protocol is omitted, add default http:// for parsing
        parse_target = "http://" + raw_url
    else:
        parse_target = raw_url

    parsed = urlparse(parse_target)
    hostname = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    # Domain / hostname parts
    host_clean = hostname.split(':')[0]
    domain_parts = host_clean.split('.')
    num_subdomains = max(0, len(domain_parts) - 2) if len(domain_parts) > 1 else 0

    # Suspicious TLD check
    has_suspicious_tld = 1 if any(host_clean.endswith(tld) for tld in SUSPICIOUS_TLDS) else 0

    # IP address host check
    has_ip = 1 if is_ip_address(host_clean) else 0

    # Suspicious keyword matching in domain and path
    full_str = f"{hostname}/{path}/{query}"
    matched_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in full_str]
    keyword_count = len(matched_keywords)

    # Character counts
    url_len = len(raw_url)
    domain_len = len(host_clean)
    num_dots = raw_url.count('.')
    num_hyphens = raw_url.count('-')
    num_at = raw_url.count('@')
    num_question = raw_url.count('?')
    num_percent = raw_url.count('%')
    num_digits = sum(c.isdigit() for c in raw_url)
    digit_ratio = round(num_digits / max(1, url_len), 4)

    # Protocol
    is_https = 1 if raw_url.lower().startswith("https://") else 0

    # Double slash redirect check (// after index 8)
    has_double_slash = 1 if raw_url.find("//", 8) != -1 else 0

    # Punycode / Homograph check
    has_punycode = 1 if "xn--" in host_clean else 0

    # Shannon Entropy
    entropy = calculate_entropy(raw_url)

    features = {
        "url_length": url_len,
        "domain_length": domain_len,
        "num_dots": num_dots,
        "num_hyphens": num_hyphens,
        "num_at": num_at,
        "num_question": num_question,
        "num_percent": num_percent,
        "digit_ratio": digit_ratio,
        "num_subdomains": num_subdomains,
        "has_ip": has_ip,
        "is_https": is_https,
        "has_suspicious_tld": has_suspicious_tld,
        "keyword_count": keyword_count,
        "has_double_slash": has_double_slash,
        "has_punycode": has_punycode,
        "entropy": entropy
    }

    metadata = {
        "hostname": host_clean,
        "matched_keywords": matched_keywords,
        "has_suspicious_tld": bool(has_suspicious_tld),
        "has_ip": bool(has_ip),
        "is_https": bool(is_https)
    }

    return {"features": features, "metadata": metadata}
