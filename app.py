import streamlit as st
import pdf2image
import io
from PIL import Image
import base64
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from report import generate_pdf_report

# 🧠 Configuration de la page
st.set_page_config(page_title="CV ATS Checker", layout="centered")
#st.write("🎨 Thème actif :", st.get_option("theme.base"))


# === Langue ===
# lang = "en"
# if st.toggle("🇬🇧 / 🇫🇷", value=False):
#     lang = "fr"
# === Bar supérieure : toggle langue + bouton café
# === Barre supérieure : drapeaux + toggle à gauche, bouton café à droite
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("""
        <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
            🇬🇧 / 🇫🇷
        </div>
    """, unsafe_allow_html=True)

    # Toggle réel Streamlit
    lang = "fr" if st.toggle(label="", value=False) else "en"

with right_col:
    st.markdown("""
        <div style="display: flex; justify-content: flex-end; align-items: center;">
            <a href="https://buymeacoffee.com/yfc92" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
                     alt="Buy Me A Coffee" style="height: 42px;">
            </a>
        </div>
    """, unsafe_allow_html=True)



# === Traductions ===
translations = {
    "en": {
        "title": "🧠 CV ATS Checker",
        "upload": "📄 Upload your PDF CV",
        "not_cv": "❌ This file does not look like a complete professional CV.",
        "received": "✅ File received.",
        "compatibility": "Compatibility",
        "compatible": "🟢 Compatible",
        "not_compatible": "🔴 Not compatible",
        "score": "Score",
        "improve": "To Improve",
        "no_remarks": "No remarks",
        "report_note": "📄 The PDF report includes full analysis.",
        "download": "📄 Download full report",
    },
    "fr": {
        "title": "🧠 Analyse ATS de CV avec IA",
        "upload": "📄 Téléversez votre CV PDF",
        "not_cv": "❌ Ce document ne semble pas être un CV professionnel complet.",
        "received": "✅ Fichier reçu.",
        "compatibility": "Compatibilité",
        "compatible": "🟢 Compatible",
        "not_compatible": "🔴 Non compatible",
        "score": "Score",
        "improve": "À améliorer",
        "no_remarks": "Aucune remarque",
        "report_note": "🔍 Le rapport PDF contient l’analyse complète.",
        "download": "📄 Télécharger le rapport complet",
    }
}
t = translations[lang]

# === Clé API Gemini ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Fonctions ===

def convert_pdf_to_image(uploaded_file):
    
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    first_page = images[0]
    img_byte_arr = io.BytesIO()
    first_page.save(img_byte_arr, format='JPEG')
    img_data = base64.b64encode(img_byte_arr.getvalue()).decode()
    return [{"mime_type": "image/jpeg", "data": img_data}]

def ask_gemini(prompt, image_part):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt, image_part])
    return response.text

def summarize_improvements(improvements, lang):
    if not improvements:
        return f"<p>{translations[lang]['no_remarks']}</p>"

    prompt = {
        "en": (
            "Summarize the following improvement suggestions in 2 very short sentences, "
            "focusing only on the most critical issues for ATS compatibility. "
            "Do not explain or expand. Be brief."
        ),
        "fr": (
            "Résume les suggestions suivantes en 2 phrases très courtes, "
            "en te concentrant uniquement sur les points critiques pour la compatibilité ATS. "
            "Ne développe pas, reste concis."
        )
    }[lang]

    suggestions_text = "\n".join(improvements)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt, suggestions_text])
    return f"<p>{response.text.strip()}</p>"

# === Interface principale ===

st.title(t["title"])
uploaded_file = st.file_uploader(t["upload"], type=["pdf"])


if uploaded_file:
    st.success(t["received"])
    image_part = convert_pdf_to_image(uploaded_file)

    with st.spinner("🔎 Analyse..."):
        is_cv_prompt = {
            "en": "You're a recruiter. Is this document a professional resume? Answer Yes or No.",
            "fr": "Tu es recruteur. Est-ce un CV professionnel ? Réponds Oui ou Non."
        }[lang]
        response1 = ask_gemini(is_cv_prompt, image_part[0])
        is_cv = "oui" in response1.lower() if lang == "fr" else "yes" in response1.lower()

    if not is_cv:
        st.warning(t["not_cv"])
    else:
        with st.spinner("📊 ATS analysis..."):
            ats_prompt = {
                "en": (
                    "You are an ATS system. Analyze the resume.\n"
                    "Return ONLY the score on the first line as a number between 0 and 100.\n"
                    "Then explain ATS compatibility and give 3 improvement suggestions."
                ),
                "fr": (
                    "Tu es un système ATS. Analyse ce CV.\n"
                    "Retourne UNIQUEMENT le score sur la première ligne, sous forme de nombre entre 0 et 100.\n"
                    "Puis indique la compatibilité ATS et donne 3 suggestions d'amélioration."
                )
            }[lang]

            response2 = ask_gemini(ats_prompt, image_part[0])
            lines = response2.splitlines()

            score = 0
            for line in lines:
                match = re.search(r"\b(\d{1,3})\b", line)
                if match:
                    score = int(match.group(1))
                    break

            compatibility_text = "\n".join(lines[1:3]) if len(lines) > 2 else ""
            improvements = [line for line in lines[3:] if line.strip()]
            resume = summarize_improvements(improvements, lang)

            if score >= 70:
                comp_value = t["compatible"]
                score_color = "#4CAF50"
            else:
                comp_value = t["not_compatible"]
                score_color = "#E53935"

            gemini_says_incompatible = any(keyword in compatibility_text.lower() for keyword in ["not compatible", "non compatible", "incompatible"])
            if score >= 70 and gemini_says_incompatible:
                st.info("⚠️ Le score indique une bonne compatibilité, mais certains éléments peuvent perturber la lecture ATS (selon l'analyse IA).")

            st.markdown(f"""
            <style>
                .card-container {{
                    display: flex;
                    gap: 20px;
                    margin-top: 20px;
                }}
                .card {{
                    flex: 1;
                    background-color: rgba(249, 249, 249, 0.8);
                    color: #333333;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    min-height: 180px;
                    text-align: center;
                }}
                .card h4 {{
                    margin-bottom: 10px;
                    color: #1a73e8;
                }}
                .card .score {{
                    font-size: 36px;
                    font-weight: bold;
                    margin: 20px 0;
                    color: {score_color};
                }}
                .card p {{
                    text-align: left;
                    margin: 0;
                }}
            </style>
            <div class="card-container">
                <div class="card">
                    <h4>✅ {t["compatibility"]}</h4>
                    <p>{comp_value}</p>
                </div>
                <div class="card">
                    <h4>🎯 {t["score"]}</h4>
                    <div class="score">{score}%</div>
                </div>
                <div class="card">
                    <h4>❌ {t["improve"]}</h4>
                    <div>{resume}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.caption(t["report_note"])

            from io import BytesIO
            buffer = BytesIO()
            generate_pdf_report(buffer, response2, score)
            buffer.seek(0)

            st.download_button(
                label=t["download"],
                data=buffer,
                file_name="rapport_cv.pdf",
                mime="application/pdf"
            )
