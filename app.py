import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import io

def generate_thermal_label(text_lines):
    # Define exact dimensions in millimeters
    width = 55 * mm
    height = 25 * mm
    
    # Create a bytes buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the canvas with our custom size
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Set up fonts and text object
    c.setFont("Helvetica-Bold", 10)
    
    # Start drawing text from the top-left, accounting for margins
    text_object = c.beginText(4 * mm, height - 6 * mm)
    text_object.setLeading(14) # Line spacing
    
    for line in text_lines:
        if line.strip():
            text_object.textLine(line)
            
    c.drawText(text_object)
    
    # Finish the page and save
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

# Streamlit UI
st.set_page_config(page_title="60x30mm Thermal Label Generator", page_icon="🏷️")

st.title("🏷️ Thermal Label Generator")
st.write("Create perfectly sized **60mm x 30mm** labels for your thermal printer.")

# Input area
st.subheader("Label Content")
label_input = st.text_area(
    "Enter text for your label (one per line):", 
    value="PRODUCT NAME\nSKU: 12345678\nPRICE: $19.99",
    height=120
)

# Process text
lines = label_input.split('\n')

if st.button("Generate Preview & Download"):
    with st.spinner("Generating your label..."):
        pdf_data = generate_thermal_label(lines)
        
        st.success("Label generated successfully!")
        
        # Download button
        st.download_button(
            label="📥 Download Label PDF",
            data=pdf_data,
            file_name="thermal_label_60x30.pdf",
            mime="application/pdf"
        )

st.info("💡 **Printer Tip:** When printing this PDF, make sure your printer settings are set to **100% Scale / Actual Size** and the paper size is configured to 60mm x 30mm to prevent stretching.")
