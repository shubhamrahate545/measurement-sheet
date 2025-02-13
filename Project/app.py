from flask import Flask, request, send_file, render_template, jsonify
from fpdf import FPDF
import os
app = Flask(__name__)
# Constants
LOGO_PATH = os.path.join('static', 'logo.png')
PDF_FILENAME = "Ducting_Measurement_Sheet.pdf"
class PDF(FPDF):
   def header(self):
       """Add header to each page of the PDF."""
       self.image(LOGO_PATH, 10, 8, 25)
       self.set_font('Arial', 'B', 12)
       self.cell(200, 10, 'NEW SAI ENTERPRISES', ln=True, align='C')
       self.ln(5)
   def footer(self):
       """Add footer to each page of the PDF."""
       self.set_y(-15)
       self.set_font('Arial', 'I', 8)
       self.cell(0, 10, f'Page {self.page_no()}', align='C')
def create_project_details_section(pdf, project_details):
   """Add project details section to the PDF."""
   pdf.set_font("Arial", "", 12)
   pdf.cell(200, 10, f"Project Name: {project_details.get('projectName', '-')}", ln=True, align='L')
   pdf.cell(200, 10, f"Client Name: {project_details.get('clientName', '-')}", ln=True, align='L')
   pdf.cell(200, 10, f"Building Details: {project_details.get('buildingDetails', '-')}", ln=True, align='L')
   pdf.cell(200, 10, f"Date: {project_details.get('date', '-')}", ln=True, align='L')
   pdf.ln(10)
def create_table_header(pdf):
   """Add table header to the PDF."""
   pdf.set_fill_color(173, 216, 230)  # Light blue fill color
   pdf.cell(10, 10, "Sr.", border=1, align='C', fill=True)
   pdf.cell(50, 10, "Measurement", border=1, align='C', fill=True)
   pdf.cell(30, 10, "Type", border=1, align='C', fill=True)
   pdf.cell(30, 10, "Length", border=1, align='C', fill=True)
   pdf.cell(20, 10, "Qty", border=1, align='C', fill=True)
   pdf.cell(40, 10, "Area (SqFt)", border=1, align='C', fill=True)
   pdf.ln()
def add_table_row(pdf, index, record):
   """Add a row to the table in the PDF."""
   pdf.cell(10, 10, str(index), border=1, align='C')
   pdf.cell(50, 10, record.get("measurement", "-"), border=1, align='C')
   pdf.cell(30, 10, record.get("type", "-"), border=1, align='C')
   pdf.cell(30, 10, record.get("length", "-"), border=1, align='C')
   pdf.cell(20, 10, record.get("qty", "-"), border=1, align='C')
   pdf.cell(40, 10, f"{float(record.get('area', 0)):.2f} {record.get('unit', 'Sq. Ft.')}", border=1, align='C')
   pdf.ln()
def create_total_area_row(pdf, total_area, unit):
   """Add the total area row to the table in the PDF."""
   pdf.set_fill_color(173, 216, 230)  # Light blue fill color
   pdf.cell(140, 10, "Total:", border=1, align='R', fill=True)
   pdf.cell(40, 10, f"{total_area:.2f} {unit}", border=1, align='C', fill=True)
@app.route('/')
def home():
   """Render the home page."""
   return render_template("index.html")
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
   """Generate a PDF based on the submitted data."""
   try:
       data = request.json
       if not data:
           return jsonify({"error": "No data provided"}), 400
       # Extract project details
       project_details = data.get("projectDetails", {})
       records = data.get("records", [])
       # Create PDF
       pdf = PDF()
       pdf.set_auto_page_break(auto=True, margin=15)
       pdf.add_page()
       # Add project details section
       create_project_details_section(pdf, project_details)
       # Add table header
       create_table_header(pdf)
       # Add table rows and calculate total area
       total_area = 0
       for index, record in enumerate(records, start=1):
           area = float(record.get("area", 0))
           total_area += area
           add_table_row(pdf, index, record)
       # Add total area row
       create_total_area_row(pdf, total_area, records[0].get("unit", "Sq. Ft.") if records else "Sq. Ft.")
       # Save and return the PDF
       pdf.output(PDF_FILENAME)
       return send_file(PDF_FILENAME, as_attachment=True)
   except Exception as e:
       return jsonify({"error": str(e)}), 500
   finally:
       # Clean up: Delete the generated PDF file
       if os.path.exists(PDF_FILENAME):
           os.remove(PDF_FILENAME)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's provided port, default to 5000
    app.run(host="0.0.0.0", port=port)
   app.run(debug=True)
