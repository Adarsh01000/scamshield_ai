import re
from typing import List, Tuple
from src.models.schemas import UserInput, Evidence, AgentResult

class NLPAgent:
    """
    NLP Agent for ScamShield AI.
    Analyzes SMS, WhatsApp, and email text for urgency, threats, impersonation,
    financial requests, credential demands, and social engineering patterns.
    """
    def __init__(self):
        # Known entity patterns for impersonation
        self.financial_entities = [
            "sbi", "hdfc", "icici", "axis bank", "punjab national bank", "pnb",
            "paytm", "phonepe", "gpay", "google pay", "paypal", "chase", "wells fargo",
            "bank of america", "citi", "rbi", "reserve bank"
        ]
        self.service_entities = [
            "amazon", "flipkart", "netflix", "microsoft", "apple", "fedex", "dhl",
            "india post", "ups", "usps", "jio", "airtel", "vodafone", "bsnl"
        ]
        self.govt_entities = [
            "income tax", "irs", "customs", "cyber police", "cbi", "enforcement directorate",
            "electricity board", "epfo", "court summons", "traffic police"
        ]
        self.valid_tlds = {
            "com", "org", "net", "edu", "gov", "mil", "in", "io", "co", "icu", "top", "xyz",
            "buzz", "info", "biz", "online", "site", "shop", "tech", "club", "vip", "cc", "app",
            "me", "live", "store", "ru", "cn", "uk", "us", "ca", "de", "jp", "fr", "au", "dev",
            "ai", "tk", "ml", "ga", "cf", "gq", "work", "click", "fit", "surf", "rest", "monster"
        }

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs found inside text, verifying valid protocol or registered TLDs."""
        url_regex = r'(https?://[^\s<>"]+|www\.[^\s<>"]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>"]*)?)'
        found = re.findall(url_regex, text)
        clean_urls = []
        for u in found:
            u_clean = u.rstrip('.,;!?:)"\'')
            if not u_clean or u_clean.endswith((".py", ".txt", ".png", ".jpg")):
                continue
            # Validate protocol or recognized TLD
            if u_clean.startswith(("http://", "https://", "www.")):
                clean_urls.append(u_clean)
            else:
                host_part = u_clean.split('/')[0].split(':')[0]
                if '.' in host_part:
                    tld = host_part.split('.')[-1].lower()
                    if tld in self.valid_tlds:
                        clean_urls.append(u_clean)
        return clean_urls

    def analyze(self, user_input: UserInput) -> AgentResult:
        evidence_list: List[Evidence] = []
        raw_text = user_input.content
        text = raw_text.lower()

        # 1. Urgency & Account Threat
        if "urgent" in text or "blocked" in text:
            evidence_list.append(Evidence(
                indicator="urgency_language",
                detected=True,
                severity="high",
                confidence=0.90,
                source="nlp_agent",
                evidence="urgent / account will be blocked",
                explanation="The text creates pressure to act immediately."
            ))
        elif any(w in text for w in ["immediately", "act now", "suspended within", "24 hours", "expires today", "last chance", "final warning", "deactivated"]):
            match = next(w for w in ["immediately", "act now", "suspended within", "24 hours", "expires today", "last chance", "final warning", "deactivated"] if w in text)
            evidence_list.append(Evidence(
                indicator="urgency_language",
                detected=True,
                severity="high",
                confidence=0.85,
                source="nlp_agent",
                evidence=f"Urgency trigger found: '{match}'",
                explanation="The message creates artificial urgency and pressure to force hasty compliance."
            ))

        # 2. Coercive Threat & Legal/Arrest Pressure
        if any(w in text for w in ["legal action", "arrest warrant", "police case", "court notice", "penalty fine", "electricity disconnect", "power cut"]):
            match = next(w for w in ["legal action", "arrest warrant", "police case", "court notice", "penalty fine", "electricity disconnect", "power cut"] if w in text)
            evidence_list.append(Evidence(
                indicator="coercive_threat",
                detected=True,
                severity="critical",
                confidence=0.92,
                source="nlp_agent",
                evidence=f"Intimidation keyword: '{match}'",
                explanation="Scammers use fear and intimidation of legal or physical penalties to coerce victims."
            ))

        # 3. Credential & Sensitive Demands with Protective Warning Check
        has_security_warning = any(phrase in text for phrase in [
            "never share", "do not share", "don't share", "not share your",
            "never disclose", "do not disclose", "will never ask", "never ask for"
        ])
        is_soliciting_credential = any(phrase in text for phrase in [
            "share your otp", "enter otp", "send otp", "provide password", "submit pin",
            "verify password", "share otp", "give otp", "tell otp", "fill otp"
        ])

        if ("otp" in text or "password" in text) and not (has_security_warning and not is_soliciting_credential):
            evidence_list.append(Evidence(
                indicator="credential_request",
                detected=True,
                severity="high",
                confidence=0.95,
                source="nlp_agent",
                evidence="requesting otp or password",
                explanation="The text asks for sensitive credentials."
            ))
        elif any(w in text for w in ["cvv", "atm pin", "netbanking credentials", "credit card number", "aadhaar", "ssn", "secret code"]) and not has_security_warning:
            match = next(w for w in ["cvv", "atm pin", "netbanking credentials", "credit card number", "aadhaar", "ssn", "secret code"] if w in text)
            evidence_list.append(Evidence(
                indicator="credential_request",
                detected=True,
                severity="critical",
                confidence=0.94,
                source="nlp_agent",
                evidence=f"Sensitive authentication request: '{match}'",
                explanation="Direct solicitation of banking/identity secrets is a prime hallmark of credential harvesting."
            ))

        # 4. KYC / Account Update Demand
        if any(w in text for w in ["kyc update", "update kyc", "pan card link", "pan update", "kyc expired", "verify identity", "re-kyc"]):
            evidence_list.append(Evidence(
                indicator="kyc_verification_demand",
                detected=True,
                severity="high",
                confidence=0.88,
                source="nlp_agent",
                evidence="Unsolicited KYC verification or PAN linking request",
                explanation="Phishing campaigns frequently weaponize fake KYC compliance to compromise bank accounts."
            ))

        # 5. Brand & Institution Impersonation
        detected_brand = None
        for brand in self.financial_entities:
            if re.search(r'\b' + re.escape(brand) + r'\b', text):
                detected_brand = brand.upper()
                break
        if not detected_brand:
            for brand in self.service_entities + self.govt_entities:
                if re.search(r'\b' + re.escape(brand) + r'\b', text):
                    detected_brand = brand.upper()
                    break

        if detected_brand:
            # If other suspicious indicators exist, brand impersonation is higher risk; otherwise low
            has_other_indicators = len(evidence_list) > 0
            evidence_list.append(Evidence(
                indicator="brand_impersonation",
                detected=True,
                severity="medium" if has_other_indicators else "low",
                confidence=0.82 if has_other_indicators else 0.50,
                source="nlp_agent",
                evidence=f"Claimed organization: {detected_brand}",
                explanation=f"Text claims association with trusted entity '{detected_brand}'."
            ))

        # 6. Financial Requests, Lottery, or Fake Job Lures
        if any(w in text for w in ["won lottery", "congratulations you won", "claim prize", "lucky draw", "cash prize", "won $", "won rs"]):
            evidence_list.append(Evidence(
                indicator="lottery_reward_lure",
                detected=True,
                severity="high",
                confidence=0.93,
                source="nlp_agent",
                evidence="Unsolicited reward/lottery prize claim detected",
                explanation="Classic advance-fee fraud incentive promising unexpected winnings."
            ))
        elif any(w in text for w in ["work from home", "earn 5000", "daily income", "part time job", "like youtube videos", "telegram task"]):
            evidence_list.append(Evidence(
                indicator="job_offer_scam",
                detected=True,
                severity="high",
                confidence=0.89,
                source="nlp_agent",
                evidence="High-yield part-time task or work-from-home lure detected",
                explanation="Task scams trick victims into small deposits before stealing larger sums."
            ))
        elif any(w in text for w in ["wire transfer", "send money", "crypto", "bitcoin", "processing fee", "refundable deposit"]):
            evidence_list.append(Evidence(
                indicator="financial_request",
                detected=True,
                severity="high",
                confidence=0.84,
                source="nlp_agent",
                evidence="Direct payment or fund transfer request",
                explanation="Solicitation of funds via non-standard or pressure tactics indicates financial fraud."
            ))

        # 7. Embedded Links in Text
        extracted_urls = self.extract_urls(raw_text)
        if extracted_urls:
            evidence_list.append(Evidence(
                indicator="embedded_url_detected",
                detected=True,
                severity="low",
                confidence=0.70,
                source="nlp_agent",
                evidence=f"URLs found: {', '.join(extracted_urls[:3])}",
                explanation="Message contains embedded web links redirecting the recipient off-platform."
            ))

        # Calculate modality score
        modality_score = 0.0
        for ev in evidence_list:
            if ev.severity == "critical":
                modality_score += 45 * ev.confidence
            elif ev.severity == "high":
                modality_score += 35 * ev.confidence
            elif ev.severity == "medium":
                modality_score += 20 * ev.confidence
            else:
                modality_score += 10 * ev.confidence
        modality_score = min(modality_score, 100.0)

        return AgentResult(
            agent_name="nlp_agent",
            evidence_list=evidence_list,
            modality_score=modality_score,
            metadata={
                "extracted_urls": extracted_urls,
                "token_count": len(text.split()),
                "detected_brand": detected_brand
            }
        )
