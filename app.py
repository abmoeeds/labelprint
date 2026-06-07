import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime  # Added for generating dynamic names

def generate_thermal_label(text, alignment, is_bold, is_underline, font_size):
    # 60mm x 30mm dimensions
    width = 60 * mm
    height = 30 * mm
    
    buffer = io.BytesIO()
    
    # SimpleDocTemplate manages formatting, margins, and wrapping automatically
    # Set small 3mm margins to maximize the print area
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=(width, height),
        leftMargin=3*mm, 
        rightMargin=3*mm, 
        topMargin=3*mm, 
        bottomMargin=3*mm
    )
    
    # Map alignment selection
    align_map = {
        "Left": TA_LEFT,
        "Center": TA_CENTER,
        "Right": TA_RIGHT
    }
    
    # Build custom paragraph style based on UI selections
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 4, # Automatic line spacing adjustment
        alignment=align_map[alignment]
    )
    
    story = []
    
    # Process text lines and apply bold/underline HTML-like tags
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip() == "":
            formatted_lines.append("")
            continue
            
        processed_line = line
        if is_bold:
            processed_line = f"<b>{processed_line}</b>"
        if is_underline:
            processed_line = f"<u>{processed_line}</u>"
            
        formatted_lines.append(processed_line)
    
    # Join back with HTML breaks for multi-line support inside the Paragraph flowable
    full_html_text = "<br/>".join(formatted_lines)
    story.append(Paragraph(full_html_text, custom_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Unique Thermal Label Gen", page_icon="🏷️")
st.title("🏷️ Dynamic 60x30mm Label Gen")

# File naming options sidebar
st.sidebar.header("📁 File Saving Options")
file_prefix = st.sidebar.text_input("File Name Prefix", value="label")

# Formatting options sidebar
st.sidebar.header("🎨 Text Styling")

text_alignment = st.sidebar.radio(
    "Text Alignment",
    options=["Left", "Center", "Right"],
    index=1 # Default to center
)

col1, col2 = st.sidebar.columns(2)
with col1:
    make_bold = st.checkbox("Bold (B)", value=True)
with col2:
    make_underline = st.checkbox("Underline (U)", value=False)

font_size = st.sidebar.slider("Font Size (pt)", min_value=6, max_value=24, value=11)

# Main input text area
st.subheader("Label Content")
label_input = st.text_area(
    "Enter label text (Supports multiple lines):", 
    value="BARGAIN BOUTIQUE\nSKU: 987654321\n$14.99",
    height=120
)

if st.button("✨ Generate & Preview"):
    with st.spinner("Formatting layout..."):
        pdf_data = generate_thermal_label(
            label_input, 
            text_alignment, 
            make_bold, 
            make_underline, 
            font_size
        )
        
        # Generate a new unique filename using the current timestamp
        # Format: prefix_YYYYMMDD_HHMMSS.pdf (e.g., label_20260607_230145.pdf)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_prefix = "".join(c for c in file_prefix if c.isalnum() or c in ('_', '-')).strip()
        if not clean_prefix:
            clean_prefix = "label"
        unique_filename = f"{clean_prefix}_{timestamp}.pdf"
        
        st.success(f"Label created flawlessly! Generated filename: `{unique_filename}`")
        
        st.download_button(
            label="📥 Download Ready-to-Print PDF",
            data=pdf_data,
            file_name=unique_filename,  # Pass the unique dynamic filename here
            mime="application/pdf"
        )
