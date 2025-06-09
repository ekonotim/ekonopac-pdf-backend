from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import os

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate_pdf():
    try:
        print("✅ Received POST /generate request")
        data = request.json
        produce = data.get("produce", "Unknown").lower()
        pounds = float(data.get("pounds", 100))

        dilution = {
            "apples": 3.3 / 750,
            "avocados": 3.3 / 660,
            "guacamole": 3.3 / 660,
            "bananas": 3.3 / 500,
            "plums": 3.3 / 600,
            "pears": 3.3 / 720,
            "carrots": 3.3 / 700,
            "celery": 3.3 / 710
        }

        powder_lb = pounds * dilution.get(produce, 3.3 / 750)
        powder_oz = powder_lb * 16
        powder_grams = round(powder_oz * 28.35, 1)
        water_oz = round(powder_grams * 0.4)
        water_liters = round(water_oz * 0.0295735, 1)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER, topMargin=120, bottomMargin=70)
        styles = getSampleStyleSheet()
        brand_blue = colors.HexColor("#0066cc")

        story = []
        story.append(Paragraph(f"NatureSeal® Recipe Instructions for {produce.title()}",
                               ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER,
                                              fontSize=16, textColor=brand_blue, spaceAfter=12)))

        table_data = [
            ["Kilograms of Produce", f"{round(pounds * 0.4536, 1)} kg"],
            ["Grams of NatureSeal", f"{powder_grams} g"],
            ["Liters of Water Needed", f"{water_liters} L"],
            ["Recommended Product", "Avocado Blend (1.25 lb)" if produce in ["avocados", "guacamole"]
             else "Standard NatureSeal (3.3 lb)"]
        ]

        table = Table(table_data, colWidths=[220, 260])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), brand_blue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("Preparation Instructions",
                               ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13,
                                              textColor=brand_blue, spaceBefore=10, spaceAfter=8)))

        if produce == "guacamole":
            instructions = [
                "1. Scoop pulp into mixing bowl.",
                "2. Add 4 teaspoons of NatureSeal and blend until fully incorporated.",
                "3. Add remaining guacamole ingredients.",
                "4. Store covered and refrigerated."
            ]
        elif produce == "avocados":
            instructions = [
                "1. Dissolve 2 tablespoons of NatureSeal in 240 mL (1 cup) of cold water.",
                "2. Submerge avocado slices for at least 10 minutes.",
                "3. Stir occasionally to coat all surfaces.",
                "4. Drain well and refrigerate in sealed container."
            ]
        else:
            instructions = [
                f"1. Dissolve {powder_grams} g of NatureSeal into {water_liters} liters of cold water.",
                "2. Submerge produce for 1–5 minutes.",
                "3. Drain well and refrigerate promptly.",
                "4. After treating this batch, refrigerate solution immediately.",
                f"5. If you wish to reuse the solution, add {round(powder_grams / pounds, 1)} g of NatureSeal for every additional pound of produce treated.",
                "6. Discard solution after 8 hours or if contaminated."
            ]

        for step in instructions:
            story.append(Paragraph(step, styles["Normal"]))
            story.append(Spacer(1, 4))

        footer = Paragraph("<font color='white'>orders@ekonopac.com • (615) 230-9340 • www.ekonopac.com</font>",
                           ParagraphStyle(name="Footer", alignment=TA_CENTER, fontSize=9))
        footer_bg = Table([[footer]], colWidths=[LETTER[0] - 100])
        footer_bg.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), brand_blue),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(Spacer(1, 30))
        story.append(footer_bg)

        doc.build(story)
        buffer.seek(0)
        filename = f"EkonOPac_{produce.title()}_Treatment.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

    except Exception as e:
        print("❌ PDF generation error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
