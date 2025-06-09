from flask import Flask, request, send_file
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_pdf():
    try:
        print("✅ Received POST /generate request")
        data = request.json
        produce = data.get("produce", "Unknown")
        pounds = data.get("pounds", "Unknown")

        # Create a basic PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, f"Test PDF for: {produce}")
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, f"Pounds: {pounds}")
        p.drawString(100, 700, "This is a test PDF to confirm POST is working.")
        p.showPage()
        p.save()
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name="EkonOPac_Test.pdf", mimetype="application/pdf")

    except Exception as e:
        print("❌ PDF generation error:", str(e))
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
