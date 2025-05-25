from flask import Flask, request, send_file, jsonify
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_pdf():
    try:
        data = request.json
        produce = data.get("produce", "Unknown").title()
        pounds = data.get("pounds", "Unknown")

        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 750, f"NatureSeal® Recipe Instructions for {produce}")
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, f"Pounds of Produce: {pounds}")
        p.drawString(100, 700, "Instructions:")
        p.drawString(120, 680, "1. Mix appropriate amount of NatureSeal in cold water.")
        p.drawString(120, 660, "2. Submerge cut produce for recommended time.")
        p.drawString(120, 640, "3. Drain well and refrigerate.")
        p.drawString(120, 620, "4. Discard solution after use.")

        p.showPage()
        p.save()
        buffer.seek(0)
        filename = f"EkonOPac_{produce}_Minimal.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
