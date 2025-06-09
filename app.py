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
        tbsp = round(powder_grams * 0.113)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER, topMargin=120, bottomMargin=70)
        styles = getSampleStyleSheet()
        brand_blue = colors.HexColor("#0066cc")

        story = []
        story.append(Paragraph(f"NatureSeal® Recipe Instructions for {produce.title()}",
                               ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER,
                                              fontSize=16, textColor=brand_blue, spaceAfter=12)))

        table_data = [
            ["Pounds of Produce", f"{pounds} lbs"],
            ["Ounces of NatureSeal", f"{powder_oz:.1f} oz"],
            ["Tablespoons of NatureSeal", f"{tbsp} tbsp"],
            ["Water Needed", f"{water_oz} oz (~{round(water_oz/32, 1)} quarts)"],
            ["Recommended Product", "Avocado Blend (1.25 lb)" if produce in ["avocados", "guacamole"]
             else "Standard NatureSeal (3.3 lb)"]
        ]

        table = Table(table_data, colWidths=[200, 280])
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
                "2. Add 4 tsp of NatureSeal and blend until fully incorporated.",
                "3. Add remaining guacamole ingredients.",
                "4. Store covered and refrigerated."
            ]
        elif produce == "avocados":
            instructions = [
                "1. Dissolve 2 Tbsp of NatureSeal in 1 cup (8 oz) of cold water.",
                "2. Submerge avocado slices for at least 10 minutes.",
                "3. Stir occasionally to coat all surfaces.",
                "4. Drain well and refrigerate in sealed container."
            ]
        elif produce == "apples":
            instructions = [
                "1. Dissolve 1 cup NatureSeal into 1 gallon of cold water.",
                "2. Dip apple slices for 1–2 minutes, mixing gently.",
                "3. Treat up to 33 lbs per gallon. Recharge with 1/4 cup after each 33 lbs.",
                "4. Discard solution after 132 lbs or 8 hrs refrigerated.",
                "5. Drain, pack, and store at 36–41°F."
            ]
        else:
            instructions = [
                f"1. Dissolve {powder_oz:.1f} oz ({tbsp} tbsp) of NatureSeal into {water_oz} oz of cold water (~{round(water_oz/32, 1)} quarts).",
                "2. Submerge produce for 1–5 minutes in the solution.",
                "3. Drain well and refrigerate promptly.",
                "4. Discard solution after 8 hours or if contaminated.",
                "5. Recharge solution by adding ¼ oz of NatureSeal after every 10 lbs of produce."
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
