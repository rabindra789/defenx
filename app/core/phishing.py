from typing import Dict, List, Optional

class PhishingScanner:
    SUSPICIOUS_KEYWORDS: List[str] = ["password","login","bank","verify","urgent","click here"]
    SUSPICIOUS_DOMAINS: List[str] = ["bit.ly","tinyurl.com","malicious.com"]

    def __init__(self, keywords: Optional[List[str]] = None, domains: Optional[List[str]] = None):
        if keywords: self.SUSPICIOUS_KEYWORDS = keywords
        if domains: self.SUSPICIOUS_DOMAINS = domains

    def scan_email(self, content: str) -> Dict:
        content_lower = content.lower()
        score = 0
        reasons: List[str] = []

        for kw in self.SUSPICIOUS_KEYWORDS:
            if kw in content_lower:
                score += 1
                reasons.append(f"Keyword detected: {kw}")
        for domain in self.SUSPICIOUS_DOMAINS:
            if domain in content_lower:
                score += 2
                reasons.append(f"Suspicious domain: {domain}")

        if score >= 3: risk_level = "High"
        elif score >= 1: risk_level = "Medium"
        else: risk_level = "Low"

        return {"risk_score": score, "risk_level": risk_level, "reasons": reasons}
