from fpdf import FPDF
import os

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

def generate_pdf_report(buffer, text_summary: str, score: int):
    pdf = PDF()
    pdf.add_page()

    # Charger la police Unicode (DejaVuSans.ttf dans fonts/)
    font_path = os.path.join("fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_font("DejaVu", "B", font_path, uni=True)
    pdf.add_font("DejaVu", "I", font_path, uni=True)
    pdf.add_font("DejaVu", "BI", font_path, uni=True)  # Optionnel

    # Titre
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Rapport d'analyse ATS du CV", ln=True, align="C")
    pdf.ln(10)

    # Score
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(40, 100, 200)
    pdf.cell(0, 10, f"🎯 Score global : {score}/100", ln=True)
    pdf.ln(8)

    # Résumé
    pdf.set_font("DejaVu", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 8, "🧠 Analyse générée par Gemini :")
    pdf.ln(2)
    pdf.multi_cell(0, 8, text_summary)

    # Footer
    pdf.ln(10)
    pdf.set_font("DejaVu", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, "Généré automatiquement par CV Gemini ATS Checker", ln=True, align="C")

    # Export dans le buffer mémoire
    pdf.output(buffer)
