
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
        powder_oz = round(powder_lb * 16, 1)
        powder_grams = powder_oz * 28.35
        water_oz = round(powder_grams * 0.4)
        quarts = round(water_oz / 32, 1)
        oz_per_lb = round(powder_oz / pounds, 2)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER, topMargin=100, bottomMargin=70)
        styles = getSampleStyleSheet()
        brand_blue = colors.HexColor("#0066cc")

        story = []
        story.append(Paragraph(f"NatureSeal® Recipe Instructions for {produce.title()}",
                               ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER,
                                              fontSize=16, textColor=brand_blue, spaceAfter=12)))

        # Custom header row
        header = [["To treat {} lbs of {}".format(pounds, produce.title()), ""]]
        table_data = [["NatureSeal Powder Needed", f"{powder_oz:.1f} oz"],
                      ["Water Needed", f"{water_oz} oz (~{quarts} quarts)"]]

        full_table = header + table_data

        table = Table(full_table, colWidths=[240, 240])
        table.setStyle(TableStyle([
            ("SPAN", (0, 0), (-1, 0)),
            ("BACKGROUND", (0, 0), (-1, 0), brand_blue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 1), (-1, -1), 0.25, colors.gray),
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
                "1. Dissolve 2 tablespoons of NatureSeal in 8 oz (1 cup) of cold water.",
                "2. Submerge avocado slices for at least 10 minutes.",
                "3. Stir occasionally to coat all surfaces.",
                "4. Drain well and refrigerate in sealed container."
            ]
        else:
            instructions = [
                f"1. Dissolve {powder_oz:.1f} oz of NatureSeal into {water_oz} oz (~{quarts} quarts) of cold water.",
                "2. Submerge produce for 1–5 minutes.",
                "3. Drain well and refrigerate promptly.",
                "4. After treating this batch, refrigerate the solution immediately.",
                f"5. To reuse the solution, add {oz_per_lb} oz of NatureSeal for every additional pound of produce.",
                "6. Discard solution after 8 hours or if contaminated."
            ]

        for step in instructions:
            story.append(Paragraph(step, styles["Normal"]))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 10))
        story.append(Paragraph(f"Recommended Product: {'Avocado Blend (1.25 lb)' if produce in ['avocados', 'guacamole'] else 'Standard NatureSeal (3.3 lb)'}",
                               ParagraphStyle(name="FooterNote", fontSize=10, textColor=brand_blue, spaceBefore=12)))

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
