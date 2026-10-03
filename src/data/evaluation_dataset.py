"""
Auditable benchmark dataset for ScamShield AI evaluation.
Covers real-world SMS, emails, URLs, and multimodal scenarios.
"""

TEXT_EVALUATION_DATA = [
    # --- Legitimate Text Samples (Label: 0) ---
    {
        "id": "legit_txt_1",
        "text": "Hey Mom, I'm heading home now. Let me know if you need anything from the grocery store.",
        "label": 0,
        "type": "Personal SMS"
    },
    {
        "id": "legit_txt_2",
        "text": "Your Amazon package with order #112-9842 has been delivered to your front porch.",
        "label": 0,
        "type": "Legitimate Delivery Notice"
    },
    {
        "id": "legit_txt_3",
        "text": "Reminder: Your dentist appointment is scheduled for tomorrow at 3:00 PM. Reply 1 to confirm.",
        "label": 0,
        "type": "Appointment Reminder"
    },
    {
        "id": "legit_txt_4",
        "text": "Dear customer, your monthly HDFC bank account statement for September is now available to download in netbanking.",
        "label": 0,
        "type": "Official Statement Alert"
    },
    {
        "id": "legit_txt_5",
        "text": "The team meeting has been rescheduled to Thursday 11 AM. Please review the attached slide deck.",
        "label": 0,
        "type": "Work Email"
    },
    {
        "id": "legit_txt_6",
        "text": "Happy birthday Rahul! Hope you have a wonderful year ahead full of success and joy.",
        "label": 0,
        "type": "Personal Greeting"
    },
    {
        "id": "legit_txt_7",
        "text": "Your Google verification code is 492019. Never share this code with anyone.",
        "label": 0,
        "type": "Legitimate OTP Notification"
    },
    {
        "id": "legit_txt_8",
        "text": "Thank you for dining at Bistro Garden. Your bill of $42.50 was settled via Apple Pay.",
        "label": 0,
        "type": "Payment Receipt"
    },
    {
        "id": "legit_txt_9",
        "text": "Flight 6E-204 boarding has commenced at Gate 14. Please proceed for immediate boarding.",
        "label": 0,
        "type": "Airline Boarding Notice"
    },
    {
        "id": "legit_txt_10",
        "text": "Your subscription to Netflix has been renewed successfully for $15.49. Next billing date: Nov 1.",
        "label": 0,
        "type": "Subscription Receipt"
    },

    # --- Scam / Fraudulent Text Samples (Label: 1) ---
    {
        "id": "scam_txt_1",
        "text": "URGENT: Dear SBI user, your netbanking access is blocked today. Immediately update KYC to avoid deactivation: http://sbi-netbanking-kyc.icu/pan-update.php",
        "label": 1,
        "type": "Banking KYC Phishing"
    },
    {
        "id": "scam_txt_2",
        "text": "CONGRATULATIONS! Your mobile number won $1,000,000 in the International Lottery 2026. Claim cash prize now: send bank details and $50 processing fee.",
        "label": 1,
        "type": "Lottery Advance Fee Scam"
    },
    {
        "id": "scam_txt_3",
        "text": "FINAL NOTICE: Power supply will be disconnected tonight at 9:30 PM due to unpaid electricity bill of Rs 1,450. Contact officer immediately at 9812739182.",
        "label": 1,
        "type": "Utility Disconnection Threat"
    },
    {
        "id": "scam_txt_4",
        "text": "Work from home part-time and earn 5000 daily by simply subscribing to YouTube channels. Contact manager on Telegram @taskincome2026 to start now.",
        "label": 1,
        "type": "Part-Time Task Scam"
    },
    {
        "id": "scam_txt_5",
        "text": "POLICE ARREST NOTICE: A cyber crime case has been registered against your Aadhaar. An arrest warrant will be executed within 24 hours unless you call back.",
        "label": 1,
        "type": "Law Enforcement Coercion"
    },
    {
        "id": "scam_txt_6",
        "text": "FedEx: Your parcel #US-81729 is on hold at customs. An outstanding clearance fee of $2.99 is required. Update address: http://customs-tax-clearance-parcel.top/pay",
        "label": 1,
        "type": "Delivery Impersonation"
    },
    {
        "id": "scam_txt_7",
        "text": "Urgent Security Alert: Unauthorized transaction of $940.00 detected on your Chase card. Share your OTP and CVV with customer support immediately to cancel.",
        "label": 1,
        "type": "Card Fraud Social Engineering"
    },
    {
        "id": "scam_txt_8",
        "text": "Income Tax Department: You are eligible for an approved tax refund of Rs 18,500. Submit your netbanking password and PIN to deposit funds: http://income-tax-refund-claim-gov.xyz/refund",
        "label": 1,
        "type": "Tax Refund Phishing"
    },
    {
        "id": "scam_txt_9",
        "text": "Dear customer, your Airtel 5G SIM will be blocked within 2 hours. Submit Aadhaar and OTP to our executive immediately to complete re-KYC.",
        "label": 1,
        "type": "Telecom SIM Swap Fraud"
    },
    {
        "id": "scam_txt_10",
        "text": "Guaranteed 300% weekly return on Bitcoin mining platform! Deposit minimum $100 crypto today to unlock daily profits. Transfer to wallet address now.",
        "label": 1,
        "type": "Cryptocurrency Investment Scam"
    }
]

URL_EVALUATION_DATA = [
    # 10 Legitimate URLs (0)
    ("https://www.google.com", 0),
    ("https://github.com", 0),
    ("https://en.wikipedia.org", 0),
    ("https://www.amazon.com", 0),
    ("https://www.apple.com", 0),
    ("https://www.microsoft.com", 0),
    ("https://stackoverflow.com", 0),
    ("https://www.onlinesbi.sbi", 0),
    ("https://mail.google.com", 0),
    ("https://www.netflix.com", 0),

    # 10 Phishing URLs (1)
    ("http://paypal-security-update-center.xyz/login.php", 1),
    ("http://192.168.1.105/sbi/verify-kyc.html", 1),
    ("http://account-verification-amazon.top/signin-secure", 1),
    ("http://appleid-support-security-alert.tk/re-login", 1),
    ("http://hdfc-bank-online-verification.icu/pan-card-update", 1),
    ("http://free-gift-card-bonus-claim.buzz/win-iphone-today", 1),
    ("http://wellsfargo-security-alert-online.live/verify-credentials", 1),
    ("http://customs-tax-clearance-parcel.top/pay-pending-duty", 1),
    ("http://electricity-bill-unpaid-disconnected.icu/instant-pay", 1),
    ("http://epfo-claim-settlement-kyc.work/epf/member-passbook", 1)
]

MULTIMODAL_EVALUATION_DATA = [
    {
        "id": "mm_1",
        "name": "SBI Netbanking KYC Warning Screenshot",
        "content": "sbi_kyc_fraud.png",
        "modality": "screenshot",
        "label": 1,
        "description": "Simulated screenshot with urgent red alert, bank impersonation, and phishing URL."
    },
    {
        "id": "mm_2",
        "name": "International Lottery Winner Screenshot",
        "content": "lottery_winner.png",
        "modality": "screenshot",
        "label": 1,
        "description": "Prize notification screenshot with advance fee payment demand."
    },
    {
        "id": "mm_3",
        "name": "Customs Delivery Notice Screenshot",
        "content": "fedex_delivery.png",
        "modality": "screenshot",
        "label": 1,
        "description": "Fake courier notification asking for immediate customs tax payment."
    },
    {
        "id": "mm_4",
        "name": "Legitimate Store Receipt Screenshot",
        "content": "clean_invoice.png",
        "modality": "screenshot",
        "label": 0,
        "description": "Authentic purchase invoice receipt with no threats or scam links."
    },
    {
        "id": "mm_5",
        "name": "SMS with Phishing Link Combination",
        "content": "URGENT: Your account has been suspended. Restore access immediately at http://paypal-security-update-center.xyz/login.php",
        "modality": "text",
        "label": 1,
        "description": "Compound multi-modal text + URL scam message."
    },
    {
        "id": "mm_6",
        "name": "Benign SMS with Authentic Link",
        "content": "Hey, check out this interesting machine learning documentation page: https://en.wikipedia.org/wiki/Machine_learning",
        "modality": "text",
        "label": 0,
        "description": "Benign conversational message with legitimate trusted link."
    }
]
