# ── Imports ────────────────────────────────────────────────
import os
import json
import sqlite3
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pickle
import numpy as np
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ── Database Setup ─────────────────────────────────────────
DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ph REAL,
            Hardness REAL,
            Solids REAL,
            Chloramines REAL,
            Sulfate REAL,
            Conductivity REAL,
            Organic_carbon REAL,
            Trihalomethanes REAL,
            Turbidity REAL,
            model_used TEXT,
            prediction INTEGER,
            confidence REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ── Load Models & Scaler ───────────────────────────────────
models = {}
for m in ["svm", "knn", "nn", "nb"]:
    model_path = f"models/{m}_model.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            models[m] = pickle.load(f)

with open("models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# ── App Setup ──────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── Health Check Route ─────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Water Potability API is running!"})

# ── Metrics Route ──────────────────────────────────────────
@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        with open("models/metrics.json", "r") as f:
            metrics = json.load(f)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": "Metrics not found"}), 404

# ── Prediction Route ───────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        features = [
            data["ph"], data["Hardness"], data["Solids"],
            data["Chloramines"], data["Sulfate"], data["Conductivity"],
            data["Organic_carbon"], data["Trihalomethanes"], data["Turbidity"]
        ]

        model_choice = data.get("model", "svm")
        if model_choice not in models:
            return jsonify({"error": "Model not available"}), 400

        model = models[model_choice]

        input_array = np.array([features])
        input_scaled = scaler.transform(input_array)

        prediction = model.predict(input_scaled)[0]
        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(input_scaled)[0]
            confidence = round(float(max(probability)) * 100, 2)
        else:
            confidence = 100.0

        result = {
            "prediction": int(prediction),
            "label": "Potable" if prediction == 1 else "Not Potable",
            "confidence": confidence,
            "model_used": model_choice.upper(),
            "features": features
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ── Store Data Route ───────────────────────────────────────
@app.route("/store", methods=["POST"])
def store_data():
    try:
        data = request.get_json()
        features = data.get("features", [])
        if len(features) != 9:
            return jsonify({"error": "Invalid features data"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (
                ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, 
                Organic_carbon, Trihalomethanes, Turbidity, model_used, prediction, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(features) + (data["model_used"], data["prediction"], data["confidence"]))
        conn.commit()
        conn.close()
        return jsonify({"message": "Data stored successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ── PDF Report Route ───────────────────────────────────────
@app.route("/report", methods=["GET"])
def generate_report():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions")
        rows = cursor.fetchall()
        conn.close()

        pdf_path = "report.pdf"
        # Landscape orientation so the wider table (13 columns) fits comfortably
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center
        subtitle_style = styles['Heading2']
        subtitle_style.textColor = colors.HexColor('#4F46E5')
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        summary_style = styles['Normal']
        summary_style.alignment = 1  # Center
        summary_style.fontSize = 11
        summary_style.textColor = colors.HexColor('#374151')

        # Title
        elements.append(Paragraph("AquaPure: Historical Prediction Log", title_style))
        elements.append(Spacer(1, 16))

        # ── Summary block ────────────────────────────────
        total = len(rows)
        potable_count = sum(1 for r in rows if r[11] == 1)
        not_potable_count = total - potable_count
        model_counts = {}
        for r in rows:
            model_counts[r[10]] = model_counts.get(r[10], 0) + 1
        most_used = max(model_counts, key=model_counts.get) if model_counts else "N/A"

        summary_text = (
            f"<b>Total Predictions:</b> {total} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Potable:</b> {potable_count} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Not Potable:</b> {not_potable_count} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Most Used Model:</b> {most_used}"
        )
        elements.append(Paragraph(summary_text, summary_style))
        elements.append(Spacer(1, 20))

        # ── Table data (all 9 feature columns included) ────
        data = [["ID", "pH", "Hardness", "Solids", "Chloramines", "Sulfate",
                  "Conductivity", "Org. Carbon", "THMs", "Turbidity",
                  "Model", "Prediction", "Confidence"]]
        for row in rows:
            data.append([
                row[0],
                round(row[1], 2), round(row[2], 2), round(row[3], 2),
                round(row[4], 2), round(row[5], 2), round(row[6], 2),
                round(row[7], 2), round(row[8], 2), round(row[9], 2),
                row[10], "Potable" if row[11] == 1 else "Not Potable", f"{row[12]}%"
            ])

        if len(data) > 1:
            table = Table(
                data,
                colWidths=[25, 30, 45, 45, 55, 45, 55, 55, 35, 45, 40, 65, 55]
            )
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F9FAFB'), colors.HexColor('#EEF2FF')])
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No predictions stored in the database yet.", normal_style))

        doc.build(elements)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)