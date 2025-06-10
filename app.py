
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)

def calculate_ounces(produce, pounds):
    dilution_rates = {
        'apples': 3.3 / 750,
        'avocados': 3.3 / 660,
        'guacamole': 3.3 / 660,
        'bananas': 3.3 / 500,
        'plums': 3.3 / 600,
        'pears': 3.3 / 720,
        'carrots': 3.3 / 700,
        'celery': 3.3 / 710,
    }
    return pounds * dilution_rates.get(produce, 3.3 / 750) * 16

def generate_recipe(produce, pounds):
    ounces = calculate_ounces(produce, pounds)
    water_oz = ounces * 0.4
    tbsp = ounces * 2  # 1 oz = 2 tbsp approx

    title = f"To treat {pounds} lbs of {produce.capitalize()}"
    instructions = []

    if produce == "guacamole":
        tsp = (4 / 2) * pounds  # 4 tsp per 2 lbs
        oz = tsp / 6  # 6 tsp per oz
        instructions = [
            title,
            f"NatureSeal Powder Needed: {oz:.1f} oz",
            f"Mix {oz:.1f} oz directly into {pounds} lbs of guacamole purée.",
            "Do not soak. Blend thoroughly before adding additional ingredients.",
            "Keep refrigerated at 36–41°F."
        ]
    elif produce == "avocados":
        gallons = water_oz / 128
        instructions = [
            title,
            f"NatureSeal Powder Needed: {ounces:.1f} oz",
            f"Water Needed: {water_oz:.0f} oz (~{gallons:.2f} gallons)",
            f"Dissolve powder into cold water and soak avocado slices for 10 minutes.",
            "Discard solution after 8 hours or if contaminated.",
            "Drain, pack, and refrigerate promptly."
        ]
    else:
        gallons = water_oz / 128
        recharge_amt = 0.25 * (pounds // 33)
        instructions = [
            title,
            f"NatureSeal Powder Needed: {ounces:.1f} oz",
            f"Water Needed: {water_oz:.0f} oz (~{gallons:.2f} gallons)",
            f"Dissolve powder into cold water. Soak slices for 1–2 minutes.",
            f"Recharge solution with ~0.25 cups for every 33 lbs of produce treated.",
            "Discard after 8 hours or if visibly contaminated.",
            "Drain, pack, and refrigerate promptly."
        ]

    return instructions

@app.route("/generate", methods=["POST"])
def generate_pdf():
    data = request.get_json()
    produce = data.get("produce", "").lower()
    pounds = float(data.get("pounds", 0))

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "NatureSeal® Recipe Instructions")

    c.setFont("Helvetica", 12)
    lines = generate_recipe(produce, pounds)
    y = height - 100
    for line in lines:
        c.drawString(72, y, line)
        y -= 20

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, 40, "For support, contact orders@ekonopac.com | (615) 230-9340 | www.ekonopac.com")

    c.showPage()
    c.save()
    packet.seek(0)
    return send_file(packet, as_attachment=True, download_name=f"EkonOPac_{produce}_Treatment.pdf", mimetype='application/pdf')

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
