from flask import Flask, request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from io import BytesIO

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_pdf():
    data = request.json
    produce = data.get("produce", "Produce")
    pounds = float(data.get("pounds", 100))

    dilution = {
        "apples": 3.3 / 750,
        "avocados": 3.3 / 660,
        "bananas": 3.3 / 500,
        "plums": 3.3 / 600,
        "pears": 3.3 / 720,
        "carrots": 3.3 / 700,
        "celery": 3.3 / 710,
        "guacamole": 3.3 / 660
    }
    cost_per_oz = 4.75 if produce in ["avocados", "guacamole"] else 2.84
    oz_needed = round(pounds * dilution.get(produce, 3.3 / 750) * 16, 1)
    cost = round(oz_needed * cost_per_oz, 2)

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

    story.append(Paragraph("Preparation Instructions", ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, textColor=brand_blue, spaceBefore=10, spaceAfter=8)))
    prep_steps = [
        f"1. Dissolve {oz_needed:.1f} oz of NatureSeal into 5 gallons of cold water.",
        f"2. Submerge cut {produce.lower()} for 3-5 minutes in the solution.",
        "3. Drain well and refrigerate promptly.",
        "4. Discard any unused solution after 8 hours or if visibly contaminated."
    ]
    for step in prep_steps:
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

    doc.build(story)
    buffer.seek(0)

    filename = f"EkonOPac_{produce.title()}_Treatment.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
