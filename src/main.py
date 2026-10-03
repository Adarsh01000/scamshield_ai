import io
import json
import os
import pandas as pd
from PIL import Image
import streamlit as st

from src.agents.orchestrator import OrchestratorAgent
from src.agents.evaluation import EvaluationAgent
from src.core.config import settings

# Page Configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} — Multi-Modal Scam Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #334155;
    }
    .badge-critical {
        background-color: #ef4444;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-high {
        background-color: #f97316;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-medium {
        background-color: #eab308;
        color: black;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #10b981;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 10px 18px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_orchestrator():
    return OrchestratorAgent()

@st.cache_resource
def get_evaluation_agent():
    return EvaluationAgent()

orchestrator = get_orchestrator()
eval_agent = get_evaluation_agent()

def generate_official_complaint_docket(result, input_text: str, modality: str) -> str:
    import datetime, hashlib
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    raw_for_hash = (input_text or "screenshot") + now_str
    hash_id = hashlib.sha256(raw_for_hash.encode('utf-8', errors='ignore')).hexdigest()[:12].upper()
    
    indicators_str = "\n".join([f"   [!] {ind.replace('_', ' ').title()}" for ind in result.indicators]) or "   [None - Content appears legitimate and safe]"
    
    evidence_str = ""
    for idx, ev in enumerate(result.evidences, 1):
        evidence_str += (
            f"   [{idx}] Severity: {ev.severity.upper()} | Confidence: {ev.confidence*100:.0f}%\n"
            f"       Source Agent: {ev.source}\n"
            f"       Forensic Finding: {ev.evidence}\n"
            f"       Technical Rationale: {ev.explanation}\n\n"
        )
    if not evidence_str:
        evidence_str = "   No actionable malicious evidence detected.\n"
        
    docket = f"""================================================================================
NATIONAL CYBERCRIME REPORTING PORTAL (NCRP) - EVIDENTIARY COMPLAINT DOCKET
Generated via ScamShield AI • Multi-Modal Threat Assessment Platform
Reference Docket ID: NCRP-EVID-{hash_id}
Generated Timestamp: {now_str}
Statutory Reference: Section 66C & 66D, Information Technology Act, 2000
National Helpline: 1930 | Portal: https://cybercrime.gov.in
================================================================================

1. INCIDENT THREAT CLASSIFICATION:
   • Assessed Risk Level: {result.risk_level.upper()}
   • Composite Multi-Modal Risk Score: {result.risk_score:.1f} / 100
   • Investigated Modality: {modality.upper()}

2. SUSPECT INCIDENT PAYLOAD / CONTENT:
   "{input_text[:600] if input_text else '[Visual Screenshot / Binary Content Analyzed]'}"

3. DETECTED FORENSIC THREAT INDICATORS:
{indicators_str}

4. FORENSIC EVIDENCE REGISTRY & AGENT GROUNDING:
{evidence_str}
5. GROUNDED FORENSIC EXPLANATION:
   {result.explanation}

6. RECOMMENDED LAW ENFORCEMENT & PREVENTATIVE REMEDIATION:
   • Citizen Advisory: {result.recommendation}
   • Legal Action: File complaint under Section 66D (Cheating by personation by using computer resource).
   • Immediate Action: Freeze recipient UPI/Bank VPA, block sender number, verify domain credentials.

================================================================================
VERIFIED EVIDENTIARY DOCKET • SCAMSHIELD AI MULTI-AGENT CYBER DEFENSE PLATFORM
================================================================================
"""
    return docket


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title(f"{settings.APP_NAME}")
    st.caption(f"v{settings.VERSION} • Agentic AI Pipeline")

    st.markdown("---")
    st.subheader("⚙️ System Status")
    st.success("🟢 Orchestrator Agent: Active")
    st.success("🟢 NLP Rule/Semantic Agent: Active")
    st.success("🟢 URL ML Classifier: Active (RF)")
    
    if getattr(orchestrator.ocr, "winocr_available", False):
        ocr_status = "🟢 WinOCR (Windows Native): Active"
    elif orchestrator.ocr.tesseract_available:
        ocr_status = "🟢 Tesseract OCR: Active"
    else:
        ocr_status = "🟡 Fallback/Catalog OCR: Active"
    st.info(ocr_status)
    
    llm_status = "🟢 Gemini GenAI: Connected" if orchestrator.explanation.gemini_client else "🟡 Structured Template Mode"
    st.info(llm_status)

    # Multi-Device / Mobile Access Section
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_wifi_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_wifi_ip = "10.147.59.3"

    with st.expander("📱 Test on Mobile / Other Device"):
        st.markdown(f"**Network URL:**  \n`http://{local_wifi_ip}:8501`")
        st.caption("1. Connect your phone to this laptop's Wi-Fi or mobile hotspot.")
        st.caption("2. Scan this QR code with your phone camera:")
        st.image(
            f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=http://{local_wifi_ip}:8501",
            caption=f"http://{local_wifi_ip}:8501",
            width=160
        )

    st.markdown("---")
    st.subheader("🎯 Demo Presets")
    preset_choice = st.selectbox(
        "Load Sample Incident:",
        [
            "-- Select Preset --",
            "1. SBI KYC Account Blocked SMS",
            "2. International Lottery Prize SMS",
            "3. Electricity Disconnection Coercion",
            "4. Phishing URL (Bare IP & Login)",
            "5. Phishing URL (Amazon .top Abuse)",
            "6. Authentic Google OTP Notification",
            "7. Authentic Amazon Order Receipt",
            "8. Screenshot: SBI KYC Fraud Alert",
            "9. Screenshot: Clean Store Invoice"
        ]
    )

    st.markdown("---")
    st.caption("College Mini Project • 100 Marks Rubric")

# Top Header
st.markdown(f'<div class="main-header">🛡️ {settings.APP_NAME}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Based Multi-Modal Scam Detection & Explainable Risk Assessment</div>', unsafe_allow_html=True)

tabs = st.tabs([
    "🔍 Live Multi-Modal Scanner",
    "📈 URL ML Classifier Analytics",
    "🧪 Evaluation & Ablation Suite",
    "📐 Architecture & Viva Voce Guide"
])

# ---------------- TAB 1: LIVE SCANNER ----------------
with tabs[0]:
    # Universal Quick Search & Investigation Bar
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">⚡</span>
            <span style="font-weight: 700; font-size: 1.1rem; color: #38bdf8;">Universal Quick Scan & Incident Search</span>
        </div>
        <div style="color: #94a3b8; font-size: 0.88rem; margin-top: 4px;">
            Search or paste any SMS, WhatsApp notification, web link, or message to scan across all agents in 1 click.
        </div>
    </div>
    """, unsafe_allow_html=True)

    quick_col1, quick_col2 = st.columns([5, 1])
    with quick_col1:
        quick_input = st.text_input(
            "Quick Search Input",
            placeholder="Type or paste any SMS, WhatsApp alert, or website URL here...",
            label_visibility="collapsed",
            key="omnibar_query"
        )
    with quick_col2:
        quick_search_btn = st.button("🔍 Quick Scan", type="primary", use_container_width=True)

    st.markdown("##### 🎯 1-Click Incident Presets")
    chip_cols = st.columns(6)
    p_sbi = chip_cols[0].button("🚨 SBI KYC Fraud", use_container_width=True)
    p_elec = chip_cols[1].button("⚡ Power Cut Alert", use_container_width=True)
    p_lott = chip_cols[2].button("🎁 Prize / Lottery", use_container_width=True)
    p_ip = chip_cols[3].button("🌐 Bare IP Link", use_container_width=True)
    p_otp = chip_cols[4].button("✅ Google OTP", use_container_width=True)
    p_amazon = chip_cols[5].button("📦 Amazon Order", use_container_width=True)

    st.markdown("---")

    col_input, col_meta = st.columns([2, 1])

    with col_input:
        modality_option = st.radio(
            "Select Specialized Investigation Modality:",
            ["📝 Text / SMS / Email", "🔗 URL Scanner", "📸 Screenshot / Image Upload", "🌐 Multi-Modal Combined"],
            horizontal=True
        )

        input_text = ""
        input_url = ""
        uploaded_image = None
        preset_img_name = None

        # Apply Presets (from sidebar or quick chip clicks)
        if p_sbi or preset_choice == "1. SBI KYC Account Blocked SMS":
            input_text = "URGENT: Dear SBI user, your netbanking access is blocked today. Immediately update KYC to avoid deactivation: http://sbi-netbanking-kyc.icu/pan-update.php"
        elif p_lott or preset_choice == "2. International Lottery Prize SMS":
            input_text = "CONGRATULATIONS! Your mobile number won $1,000,000 in International Lottery 2026. Claim cash prize now: send bank details and $50 processing fee to http://free-gift-card-bonus-claim.buzz/win-iphone-today"
        elif p_elec or preset_choice == "3. Electricity Disconnection Coercion":
            input_text = "FINAL WARNING: Electricity power supply will be disconnected tonight at 9:30 PM due to pending bill of Rs 1,450. Contact executive immediately at 9812739182."
        elif p_ip or preset_choice == "4. Phishing URL (Bare IP & Login)":
            input_url = "http://192.168.1.105/sbi/verify-kyc.html"
        elif preset_choice == "5. Phishing URL (Amazon .top Abuse)":
            input_url = "http://account-verification-amazon.top/signin-secure"
        elif p_otp or preset_choice == "6. Authentic Google OTP Notification":
            input_text = "Your Google verification code is 492019. Never share this code with anyone."
        elif p_amazon or preset_choice == "7. Authentic Amazon Order Receipt":
            input_text = "Your Amazon package with order #112-9842 has been delivered. View order details at https://www.amazon.com"
        elif preset_choice == "8. Screenshot: SBI KYC Fraud Alert":
            preset_img_name = "sample_data/sbi_kyc_fraud.png"
        elif preset_choice == "9. Screenshot: Clean Store Invoice":
            preset_img_name = "sample_data/clean_invoice.png"

        target_content = ""
        target_modality = "text"
        target_bytes = None
        target_name = None

        if "Text" in modality_option:
            content_val = st.text_area("Enter SMS, WhatsApp, or Email Text:", value=input_text, height=130)
            target_modality = "text"
            target_content = content_val

        elif "URL" in modality_option:
            content_val = st.text_input("Enter Web URL to analyze:", value=input_url)
            target_modality = "url"
            target_content = content_val

        elif "Screenshot" in modality_option:
            st.info("Upload any screenshot (SMS, WhatsApp, web capture) to analyze using Windows Native OCR & Vision.")
            uploaded_file = st.file_uploader("Upload Message or Web Screenshot:", type=["png", "jpg", "jpeg", "webp"])
            
            if uploaded_file:
                target_bytes = uploaded_file.read()
                target_name = uploaded_file.name
                target_content = uploaded_file.name
                st.image(Image.open(io.BytesIO(target_bytes)), caption="Uploaded Screenshot", width=360)
            elif preset_img_name and os.path.exists(preset_img_name):
                target_bytes = open(preset_img_name, "rb").read()
                target_name = os.path.basename(preset_img_name)
                target_content = preset_img_name
                st.image(preset_img_name, caption=f"Preset Image: {target_name}", width=360)

            target_modality = "screenshot"

        else: # Multi-Modal Combined
            c_txt = st.text_area("Suspicious Accompanying Text:", value=input_text, height=90)
            c_file = st.file_uploader("Accompanying Screenshot (optional):", type=["png", "jpg", "jpeg"])
            target_modality = "multimodal"
            target_content = c_txt
            target_bytes = c_file.read() if c_file else None
            target_name = c_file.name if c_file else None

        analyze_btn = st.button("🛡️ Run ScamShield Investigation", type="primary", use_container_width=True)

    with col_meta:
        st.markdown("### 📋 Multi-Agent Workflow")
        st.markdown("""
        1. **Orchestrator**: Routes input dynamically.
        2. **NLP Agent**: Scans urgency, credentials & coercion.
        3. **URL Agent**: Random Forest ML + Shannon entropy.
        4. **OCR Agent**: WinOCR native + Tesseract extraction.
        5. **Vision Agent**: Visual layout & color alert cues.
        6. **Evidence Agent**: Deduplicates & normalizes findings.
        7. **Risk Fusion**: Severity-weighted 0–100 calibrated score.
        8. **Explanation Agent**: Grounded explanation & safe next steps.
        """)

    # Check execution trigger
    should_execute = analyze_btn or quick_search_btn or p_sbi or p_elec or p_lott or p_ip or p_otp or p_amazon
    if quick_search_btn and quick_input:
        target_content = quick_input.strip()
        target_modality = "auto"
        target_bytes = None
        target_name = None

    if should_execute:
        if not target_content and not target_bytes:
            st.warning("Please provide input text, URL, or upload a screenshot to analyze.")
        else:
            with st.spinner("Coordinating forensic agents across NLP, URL ML, and OCR pipelines..."):
                result = orchestrator.analyze(
                    content=target_content,
                    modality=target_modality,
                    image_bytes=target_bytes,
                    image_name=target_name
                )

            st.markdown("---")
            st.subheader("🛡️ Forensic Assessment Result")

            # Risk Banner & Color Theme
            risk_color = "#10b981" if result.risk_score < 25 else "#eab308" if result.risk_score < 50 else "#f97316" if result.risk_score < 75 else "#ef4444"
            st.markdown(
                f"""
                <div style="background-color: {risk_color}22; border-left: 6px solid {risk_color}; padding: 18px 24px; border-radius: 10px; margin-bottom: 20px;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: {risk_color}; letter-spacing: 0.5px;">
                        {result.risk_level.upper()}
                    </div>
                    <div style="font-size: 1.15rem; color: #f8fafc; margin-top: 6px;">
                        Multi-Modal Risk Score: <b>{result.risk_score:.1f} / 100</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Score Cards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Risk Score", f"{result.risk_score:.0f}/100")
            m2.metric("Detected Indicators", len(result.indicators))
            m3.metric("Evidence Findings", len(result.evidences))
            m4.metric("Active Modalities", len(result.modality_scores))

            # Modality Sub-Scores
            if result.modality_scores:
                st.markdown("##### Modality Risk Contribution")
                cols = st.columns(len(result.modality_scores))
                for c, (mod, score) in zip(cols, result.modality_scores.items()):
                    c.write(f"**{mod.upper()}: {score:.1f}%**")
                    c.progress(min(1.0, score / 100.0))

            # Grounded Explanation & Safe Action
            e_col, r_col = st.columns(2)
            with e_col:
                st.markdown("#### 🧠 Grounded Forensic Explanation")
                st.info(result.explanation)

            with r_col:
                st.markdown("#### 🛡️ Recommended Safe Actions")
                st.warning(result.recommendation)

            # Auditable Evidence Registry
            st.markdown("#### 📑 Auditable Forensic Evidence Registry")
            if result.evidences:
                evidence_data = []
                for ev in result.evidences:
                    evidence_data.append({
                        "Severity": ev.severity.upper(),
                        "Indicator": ev.indicator.replace('_', ' ').title(),
                        "Confidence": f"{ev.confidence*100:.0f}%",
                        "Source Agent": ev.source,
                        "Observed Forensic Evidence": ev.evidence,
                        "Technical Explanation": ev.explanation
                    })
                df_ev = pd.DataFrame(evidence_data)
                st.dataframe(df_ev, use_container_width=True)
            else:
                st.success("No suspicious indicators or forensic evidence detected. Content conforms to benign baseline.")

            # Official Cybercrime Complaint Docket Expander
            complaint_text = generate_official_complaint_docket(result, target_content, target_modality)
            with st.expander("📋 View Official Cybercrime Complaint Docket (National Cybercrime Portal / 1930)"):
                st.text(complaint_text)

            # Audit Trail Expander
            with st.expander("🔍 View Transparent Risk Fusion Audit Trail"):
                st.json(result.audit_trail)

            # Downloadable Reports
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📋 Download Cybercrime Complaint Docket (TXT)",
                    data=complaint_text,
                    file_name="scamshield_cybercrime_complaint.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with d_col2:
                report_dict = result.model_dump()
                report_json = json.dumps(report_dict, indent=2)
                st.download_button(
                    label="📥 Download Forensic Audit Report (JSON)",
                    data=report_json,
                    file_name="scamshield_audit_report.json",
                    mime="application/json",
                    use_container_width=True
                )

# ---------------- TAB 2: URL ML ANALYTICS ----------------
with tabs[1]:
    st.header("📈 URL Machine Learning Classifier & Feature Importance")
    st.markdown("""
    The ScamShield URL Agent extracts 16 lexical, structural, and information-theoretic features
    and applies a trained **Random Forest Classifier** to detect phishing domains.
    """)

    if orchestrator.url_agent.model_metrics:
        m = orchestrator.url_agent.model_metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Model Accuracy", f"{m['accuracy']*100:.1f}%")
        c2.metric("Precision", f"{m['precision']*100:.1f}%")
        c3.metric("Recall", f"{m['recall']*100:.1f}%")
        c4.metric("F1-Score", f"{m['f1_score']:.4f}")

        st.subheader("Random Forest Feature Importances")
        feat_df = pd.DataFrame(list(m["feature_importances"].items()), columns=["Feature", "Importance"])
        feat_df = feat_df.sort_values(by="Importance", ascending=False)
        st.bar_chart(feat_df.set_index("Feature"))

    st.markdown("---")
    st.subheader("🔬 Interactive URL Feature Extractor")
    test_url_input = st.text_input("Test any URL to view extracted feature vector:", value="http://sbi-netbanking-kyc.icu/pan-update.php")
    if test_url_input:
        from src.agents.url_features import extract_url_features
        extracted = extract_url_features(test_url_input)
        f_col1, f_col2 = st.columns([1, 1])
        with f_col1:
            st.write("**Extracted Numerical Features:**")
            st.json(extracted["features"])
        with f_col2:
            st.write("**Extracted Domain Metadata:**")
            st.json(extracted["metadata"])

# ---------------- TAB 3: EVALUATION & ABLATION ----------------
with tabs[2]:
    st.header("🧪 Evaluation Benchmark & Multi-Modal Ablation Experiments")
    st.markdown("""
    This suite executes standardized repeatable test cases across Text, URL, and Multi-modal inputs
    to evaluate precision, recall, F1-scores, confusion matrices, and ablation comparisons.
    """)

    if st.button("🚀 Run Full Evaluation Benchmark Suite", type="primary"):
        with st.spinner("Running benchmark test cases..."):
            report = eval_agent.generate_full_report()

        t_res = report["text_evaluation"]
        u_res = report["url_evaluation"]
        ab_res = report["ablation_experiments"]

        st.subheader("1. Modality Classification Performance")
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            st.markdown("##### 📝 Text Analysis Pipeline")
            st.write(f"- **Accuracy:** {t_res['accuracy']*100:.1f}%")
            st.write(f"- **Precision:** {t_res['precision']*100:.1f}%")
            st.write(f"- **Recall:** {t_res['recall']*100:.1f}%")
            st.write(f"- **F1-Score:** {t_res['f1_score']:.4f}")
            st.write(f"- **Confusion Matrix [ [TN, FP], [FN, TP] ]:** `{t_res['confusion_matrix']}`")

        with e_col2:
            st.markdown("##### 🔗 URL Classification Pipeline")
            st.write(f"- **Accuracy:** {u_res['accuracy']*100:.1f}%")
            st.write(f"- **Precision:** {u_res['precision']*100:.1f}%")
            st.write(f"- **Recall:** {u_res['recall']*100:.1f}%")
            st.write(f"- **F1-Score:** {u_res['f1_score']:.4f}")
            st.write(f"- **Confusion Matrix [ [TN, FP], [FN, TP] ]:** `{u_res['confusion_matrix']}`")

        st.markdown("---")
        st.subheader("2. Multi-Modal Ablation Study Comparison")
        st.markdown("Proves how combining Text, URL, and Vision overcomes individual modality blind spots:")
        
        ablation_rows = []
        for mod_name, metrics in ab_res.items():
            ablation_rows.append({
                "Modality Configuration": mod_name,
                "Accuracy": f"{metrics['accuracy']*100:.1f}%",
                "Precision": f"{metrics['precision']:.3f}",
                "Recall": f"{metrics['recall']:.3f}",
                "F1-Score": f"{metrics['f1_score']:.3f}"
            })
        st.table(pd.DataFrame(ablation_rows))

# ---------------- TAB 4: ARCHITECTURE & VIVA ----------------
with tabs[3]:
    st.header("📐 Architecture, UML Deliverables & Viva Prep Guide")
    st.markdown("""
    Complete technical documentation, UML models, and viva voce preparation material
    aligned with the **100-mark mini-project assessment**.
    """)

    st.subheader("System Architecture")
    st.code("""
[ User Input: SMS / WhatsApp / Email / URL / Screenshot ]
                        │
                        ▼
            [ Orchestrator Agent ]
         ┌──────────────┼──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
   [ NLP Agent ]   [ URL Agent ]  [ OCR Agent ]  [ Vision Agent ]
         │              │              │              │
         └──────────────┼──────────────┴──────────────┘
                        ▼
               [ Evidence Agent ]
                        │
                        ▼
             [ Risk Fusion Agent ] (Normalized 0-100 Score)
                        │
                        ▼
            [ Explanation Agent ] (Grounded in Evidence)
                        │
                        ▼
       [ Streamlit & FastAPI Dashboards ]
    """, language="text")

    st.subheader("6 Standard UML Diagrams")
    with st.expander("1. Use Case Diagram"):
        st.markdown("""
        - **Actors**: User, Cyber Analyst, External Verification API / LLM.
        - **Use Cases**: Submit Message Text, Submit URL, Upload Screenshot, View Risk Score, Inspect Evidence Grounds, Export Audit Report, Run Evaluation Benchmarks.
        """)

    with st.expander("2. Activity Diagram"):
        st.markdown("""
        - Ingest Input -> Check Modality -> Route to specialized Agents -> Extract Features -> Classify & Score -> Aggregate Evidence -> Correlate & Fuse Risk -> Ground Explanation -> Output Result.
        """)

    with st.expander("3. Sequence Diagram"):
        st.markdown("""
        - User -> UI -> OrchestratorAgent.analyze() -> Sub-Agents.analyze() -> EvidenceAgent.collect_evidence() -> RiskFusionAgent.calculate_risk() -> ExplanationAgent.generate_explanation() -> UI.
        """)

    with st.expander("4. Component Diagram"):
        st.markdown("""
        - Modules: `agents.orchestrator`, `agents.nlp`, `agents.url`, `agents.ocr`, `agents.vision`, `agents.evidence`, `agents.risk_fusion`, `agents.explanation`, `agents.evaluation`, `models.schemas`, `core.config`.
        """)

    with st.expander("5. Class Diagram"):
        st.markdown("""
        - Classes: `UserInput`, `Evidence`, `AgentResult`, `FinalRiskResult`, `NLPAgent`, `URLAgent`, `OCRAgent`, `VisionAgent`, `EvidenceAgent`, `RiskFusionAgent`, `ExplanationAgent`, `EvaluationAgent`.
        """)

    with st.expander("6. Deployment Diagram"):
        st.markdown("""
        - Client Browser <---> Streamlit UI (Port 8501) / FastAPI REST Server (Port 8000) <---> Local Python Runtime (Joblib Model, Pillow, Pytesseract, SQLite) <---> Optional Google Gemini API.
        """)

    st.markdown("---")
    st.subheader("🎓 College Viva Voce Q&A Cheat Sheet")
    st.markdown("""
    **Q1: Why an agentic architecture rather than a single end-to-end classifier?**  
    *Answer:* Multi-modal scams operate across distinct channels (e.g. deceptive text paired with spoofed URLs and visual urgency styling). Specialized agents allow modular feature extraction, independent auditable evidence, and avoid catastrophic forgetting.

    **Q2: How is the final risk score calculated?**  
    *Answer:* Risk Fusion combines severity-weighted evidence items (`Severity * Confidence`) normalized from 0–100, with a multi-modal correlation boost applied when both text and link exhibits deceptive markers.

    **Q3: What role does the LLM play?**  
    *Answer:* The LLM is strictly confined to the explanation layer to synthesize human-readable grounds from structured evidence. It is NOT the sole classifier, preventing hallucinations.

    **Q4: How does the system handle screenshots if Tesseract is not installed?**  
    *Answer:* The system implements graceful degradation: it attempts Tesseract first, and if unavailable, uses preset image catalogs and image processing heuristics so the live demonstration remains 100% operational on any laptop.
    """)

st.markdown("---")
st.caption("ScamShield AI • Designed for College Mini Project Assessment • All rights reserved.")
