import re
from urllib.parse import urlparse

def _is_ip(host):
    # returns True if host is an IPv4 address
    return re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', host) is not None

def predict(url: str):
    """Simple heuristic-based phishing detector.
    Returns dict: {'prediction_label': 0/1, 'prediction_score': 0-100, 'explanation': str}
    The score is higher when URL looks more suspicious.
    """
    score = 0.0
    reasons = []

    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path or ''
        scheme = parsed.scheme.lower()
    except Exception as e:
        return {'prediction_label': 1, 'prediction_score': 100.0, 'explanation': f'Invalid URL parse: {e}'}

    # 1) scheme (http vs https)
    if scheme != 'https':
        score += 20
        reasons.append('No HTTPS')

    # 2) IP address in host
    host_only = host.split(':')[0]  # remove port if present
    if _is_ip(host_only):
        score += 30
        reasons.append('IP address in host')

    # 3) suspicious tokens commonly used in phishing URLs
    suspicious_tokens = ['login', 'secure', 'account', 'update', 'verify', 'bank', 'paypal', 'signin', 'webscr']
    for t in suspicious_tokens:
        if t in url.lower():
            score += 8
            reasons.append(f"Contains token '{t}'")

    # 4) presence of '@' — common trick
    if '@' in url:
        score += 25
        reasons.append("'@' in URL (suspicious)")

    # 5) too long URL
    if len(url) > 75:
        score += min(20, (len(url)-75)/2)  # cap contribution
        reasons.append('Long URL')

    # 6) lots of subdomains (like a.b.c.d.e.example.com)
    host_parts = host_only.split('.')
    if len([p for p in host_parts if p]) >= 4:
        score += 10
        reasons.append('Many subdomains')

    # 7) hyphens or suspicious punctuation in domain
    if '-' in host_only:
        score += 6
        reasons.append('Hyphen in domain')

    # 8) count dots
    dot_count = host_only.count('.')
    if dot_count >= 4:
        score += 6
        reasons.append('Many dots in domain')

    # normalize score to 0-100
    score = max(0.0, min(100.0, score))

    # label threshold (you can tune this)
    label = 1 if score >= 50 else 0

    explanation = '; '.join(sorted(set(reasons))) if reasons else 'No obvious suspicious features detected'
    return {
        'prediction_label': label,
        'prediction_score': score,
        'explanation': explanation
    }
