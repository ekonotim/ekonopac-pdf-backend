from flask import Flask, request, send_file, jsonify
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from io import BytesIO
import sys

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_pdf():
    try:
        print("🔍 Request received", file=sys.stderr)
        data = request.json
        produce = data.get("produce", "Produce").lower()
        pounds = float(data.get("pounds", 100))
        print(f"➡️ Producing for: {produce}, {pounds} lbs", file=sys.stderr)

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

        cost_per_oz = 4.75 if produce in ["avocados", "guacamole"] else 2.84
        oz_needed = round(pounds * dilution.get(produce, 3.3 / 750) * 16, 1)
        cost = round(oz_needed * cost_per_oz, 2)
        print(f"🧪 oz needed: {oz_needed}, cost: ${cost}", file=sys.stderr)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER, topMargin=120, bottomMargin=70)
        styles = getSampleStyleSheet()
        brand_blue = colors.HexColor("#0066cc")

        story = []
        story.append(Paragraph(f"NatureSeal® Recipe Instructions for {produce.title()}", ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, textColor=brand_blue, spaceAfter=12)))

        table_data = [
            ["Pounds of Produce", f"{pounds} lbs"],
            ["Ounces of NatureSeal", f"{oz_needed:.1f} oz"],
            ["Estimated Cost to Treat", f"${cost:.2f}"],
            ["Recommended Product", "Avocado Blend (1.25 lb)" if produce in ["avocados", "guacamole"] else "Standard NatureSeal (3.3 lb)"]
        ]
        print("📊 Table data built", file=sys.stderr)

        table = Table(table_data, colWidths=[180, 300])
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
        print("🧱 Table added to story", file=sys.stderr)

        story.append(Paragraph("Preparation Instructions", ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, textColor=brand_blue, spaceBefore=10, spaceAfter=8)))

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
                f"1. Dissolve {oz_needed:.1f} oz of NatureSeal into 5 gallons of cold water.",
                "2. Submerge produce for 1–5 minutes in the solution.",
                "3. Drain well and refrigerate promptly.",
                "4. Discard solution after 8 hours or if contaminated."
            ]
        print(f"🧾 Instructions ready for: {produce}", file=sys.stderr)

        for step in instructions:
            story.append(Paragraph(step, styles["Normal"]))
            story.append(Spacer(1, 4))

        footer = Paragraph("<font color='white'>orders@ekonopac.com • (615) 230-9340 • www.ekonopac.com</font>", ParagraphStyle(name="Footer", alignment=TA_CENTER, fontSize=9))
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

        print("📄 Building PDF...", file=sys.stderr)
        doc.build(story)
        buffer.seek(0)
        filename = f"EkonOPac_{produce.title()}_Treatment.pdf"
        print("✅ PDF built successfully", file=sys.stderr)
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

    except Exception as e:
        print("🔥 PDF generation failed:", str(e), file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
